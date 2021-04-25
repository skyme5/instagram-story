import argparse
import ctypes
import json
import logging
import os
import tarfile
import time
from datetime import datetime

from loguru import logger
from tqdm import tqdm

from .constants import CONFIG_PATH_INCLUDE
from .constants import CONFIG_PATH_JSON
from .constants import INFO_ALL_DONE
from .constants import INFO_DOWNLOADING
from .constants import INFO_FETCHING_FOR
from .constants import INFO_FINISH_DOWNLOADING
from .constants import INFO_REEL_FOUND
from .constants import WARNING_IGNORED
from .instagram import Instagram
from .utils import ask_user_for_input
from .utils import config_validator
from .utils import dump_response
from .utils import dump_text_file
from .utils import filepath_logging
from .utils import format_time
from .utils import home_path


logging.basicConfig(
    filename=filepath_logging(),
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)


def init_user_config():
    logging.info("Creating config file")
    config = [ask_user_for_input]
    logging.info("Saving config.")

    with open(home_path(CONFIG_PATH_JSON), "tw+") as f:
        json.dump(config, f)

    return config


def get_include_list() -> list:
    if os.path.isfile(home_path(CONFIG_PATH_INCLUDE)):
        try:
            with open(home_path(CONFIG_PATH_INCLUDE)) as f:
                return f.read().split("\n")
        except IOError:
            return []

    return []


def read_config(config_file: str) -> dict:
    if os.path.isfile(config_file):
        try:
            with open(config_file) as f:
                json_data = json.load(f)
                if config_validator(json_data):
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


def download_stories(config: dict, download_ids: list, options: dict):
    username = config["username"]
    json_backup = config["json_backup"]

    instagram = Instagram(config, options)

    logging.info(INFO_FETCHING_FOR, username)

    reels_tray = instagram.get_tray()

    dump_response(
        timestamp=int(time.time()),
        content_type="tray",
        content=reels_tray,
        prefix=json_backup,
    )

    logging.info(INFO_REEL_FOUND, len(reels_tray["tray"]), username)

    user_ids_with_reel = instagram.user_ids()
    users_to_download = [a for a in user_ids_with_reel if a in download_ids]
    users_ignored = instagram.ignored_users(download_ids)

    print(
        INFO_DOWNLOADING.format(
            username, len(users_to_download), len(user_ids_with_reel)
        )
    )

    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i : i + n]

    with tqdm(total=len(users_to_download)) as pbar:
        for user_ids in chunks(users_to_download, 8):
            reels_chunk = instagram.get_reel_chunk(user_ids)
            for user_id in user_ids:
                if user_id in reels_chunk:
                    reel = reels_chunk.get(user_id)
                    dump_response(
                        timestamp=int(reel.get("expiring_at")),
                        content_type="user_reel_{}".format(user_id),
                        content=reel,
                        prefix=json_backup,
                    )
                    instagram.download_reel(reel)
                    time.sleep(1)
                    pbar.update(1)
        # else:
        #     ctypes.windll.user32.MessageBoxW(0, "Error Downloading", "instagram-story", 1)

    instagram.close()

    logging.warning(WARNING_IGNORED, ", ".join(users_ignored))
    logging.info(INFO_FINISH_DOWNLOADING, username)


def main():
    parser = argparse.ArgumentParser(description="Instagram Story downloader")

    parser.add_argument(
        "-f",
        "--config-location",
        type=str,
        help="Path for loading and storing config key file. "
        "Defaults to " + home_path(CONFIG_PATH_JSON),
    )
    parser.add_argument(
        "-d",
        "--download-only",
        type=str,
        help="Download stories listed in the file. "
        "Defaults to " + home_path(CONFIG_PATH_INCLUDE),
    )

    args = parser.parse_args()

    config_filepath = args.config_location or home_path(CONFIG_PATH_JSON)

    config = read_config(config_filepath)

    for user in config.get("user_list"):
        downlaod_ids = config.get("include")
        if user.get("download"):
            download_stories(user, downlaod_ids, args)

    logging.info(INFO_ALL_DONE)


if __name__ == "__main__":
    main()
