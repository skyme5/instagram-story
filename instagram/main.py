import argparse
import ctypes
import json
import logging
import os
import tarfile
import time
from datetime import datetime

from jsonschema import validate
from loguru import logger
from tqdm import tqdm

from .instagram import Instagram


def format_time(time_stamp, time_fmt):
    return datetime.utcfromtimestamp(time_stamp).strftime(time_fmt)


log_filename = "/.instagram-story/instagram-story-%Y-%m-%d_%H-%M-%S.log"
log_filepath = os.environ["HOME"] + log_filename
log_filename_fmt = format_time(time.time(), log_filepath)
logging.basicConfig(
    filename=log_filename_fmt,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)


def default_config_file():
    home = os.environ["HOME"]
    return home + "/.instagram-story/config.json"


def default_include_file():
    home = os.environ["HOME"]
    return home + "/.instagram-story/include.txt"


def archive_json():
    logging.info("Collecting list of JSON objects.")

    json_list = []
    for file in os.listdir("json"):
        if file.endswith(".json"):
            json_list.append(os.path.join("json", file))

    logging.info("Creating tar.xz file of JSON objects.")

    filename = format_time(time.time(), time_fmt="%Y-%m-%d_%H-%M-%S.tar.xz")
    path = os.path.join(os.getcwd(), "json", filename)

    tar = tarfile.open(path, "x:xz")
    for path in json_list:
        tar.add(path)
    tar.close()

    logging.info("Removing old JSON objects.")
    for path in json_list:
        os.remove(path)


def save_json(timestamp: int, content_type: str, content: dict, prefix: str):
    """Save JSON file

    Args:
        timestamp: Unix timestamp
        content_type: Name
        content: JSON data
        prefix: Prefix path to save json

    Returns:
        None
    """

    utcdatetime = format_time(timestamp, time_fmt="%Y-%m-%d_%H-%M-%S")
    folder = format_time(timestamp, time_fmt="%Y-%m-%d")

    filename = "{}_{}.json".format(utcdatetime, content_type)
    path = os.path.join(prefix, folder, filename)

    dirpath = os.path.dirname(path)

    os.makedirs(dirpath, exist_ok=True)

    with open(path, "tx") as f:
        json.dump(content, f)


def ask_user_config():
    logging.info("Creating config file")
    username = input("Enter your instagram username: ")
    user_id = input("Enter your instagram user ID: ")
    cookie = input("Enter your instagram cookie: ")
    directory = input("Enter media save directory " "(default current directory): ")
    config = [
        {
            "username": username,
            "id": user_id,
            "directory": directory,
            "json_backup": os.path.join(directory, "json"),
            "download": true,
            "headers": {"cookie": cookie},
        }
    ]
    logging.info("Saving config.")

    with open(default_config_file(), "tw+") as f:
        json.dump(config, f)

    return config


def validate_config(json_data):
    SCHEMA = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "headers": {
                    "type": "object",
                    "properties": {
                        "cookie": {"type": "string"},
                    },
                },
                "username": {"type": "string"},
                "directory": {"type": "string"},
                "json_backup": {"type": "string"},
                "download": {"type": "boolean"},
            },
        },
    }
    validate(instance=json_data, schema=SCHEMA)

    return True


def get_include_list():
    if os.path.isfile(default_include_file()):
        try:
            with open(default_include_file()) as f:
                include_list = f.read().split("\n")
                include_list = [int(a) for a in include_list]
                return include_list
        except IOError:
            return []
    else:
        return []


def get_config(config_file):
    if os.path.isfile(config_file):
        try:
            with open(config_file) as f:
                json_data = json.load(f)
                if validate_config(json_data):
                    config = {"user_list": json_data, "include": get_include_list()}
                    return config
                else:
                    raise Exception("json_data validate error")

        except IOError:
            raise Exception(f"unable to read {config_file}")

        except json.decoder.JSONDecodeError:
            raise Exception(
                f"unable to parse {config_file} as json",
            )
    else:
        logger.info("Creating {} file in the current directory", config_file)
        return ask_user_config()


def download_stories(config, download, options):
    logging.info("Initializing module")

    instagram = Instagram(config, options)

    logging.info("Fetching stories for user: %s", config["username"])

    traytime = int(time.time())

    reels_tray = instagram.get_reels_tray()

    save_json(
        timestamp=traytime,
        content_type="tray",
        content=reels_tray,
        prefix=config["json_backup"],
    )

    logging.info(
        "Found %s stories for user: %s", len(reels_tray["tray"]), config["username"]
    )

    user_ids_all = instagram.get_user_ids()
    user_ids = [a for a in user_ids_all if a in download]
    users_ignored = instagram.ignored_users(download)

    print(
        "Downloading stories for {} ({}/{})".format(
            config["username"], len(user_ids), len(user_ids_all)
        )
    )

    for user_id in tqdm(user_ids):
        reel = instagram.get_user_reel(str(user_id))
        save_json(
            timestamp=int(reel.get("expiring_at")),
            content_type="reel_" + str(user_id),
            content=reel,
            prefix=config["json_backup"],
        )
        instagram.download_reel(reel)
        time.sleep(1)
        # else:
        #     ctypes.windll.user32.MessageBoxW(0, "Error Downloading", "instagram-story", 1)

    instagram.close()

    logging.warning("Following users were ignored: %s", ", ".join(users_ignored))
    logging.info("Finished downloading stories for user: %s", config["username"])


def main():
    """Main function

    Returns:
        None
    """

    logging.info("Starting application.")

    parser = argparse.ArgumentParser(description="Instagram Story downloader")

    parser.add_argument(
        "-f",
        "--config-location",
        type=str,
        help="Path for loading and storing config key file. "
        "Defaults to " + default_config_file(),
    )

    parser.add_argument(
        "-d",
        "--download-only",
        type=str,
        help="Download stories listed in the file"
        "Defaults to " + default_include_file(),
    )

    args = parser.parse_args()

    if args.config_location is not None:
        config_file = args.config_location
    else:
        config_file = default_config_file()

    config = get_config(config_file)
    user_config = config.get("user_list")
    for user in user_config:
        if user.get("download"):
            download_stories(config=user, download=config.get("include"), options=args)

    logging.info("Shutting down application.")


if __name__ == "__main__":
    main()
