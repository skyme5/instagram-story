import argparse
import json
import logging
import os
import re
import time

from tqdm import tqdm

from .constants import CONFIG_PATH_INCLUDE
from .constants import CONFIG_PATH_JSON
from .constants import INFO_ALL_DONE
from .constants import INFO_DOWNLOADING
from .constants import INFO_FETCHING_FOR
from .constants import INFO_FINISH_DOWNLOADING
from .constants import INFO_REEL_FOUND
from .constants import INFO_REEL_FOUND_FOR_USER
from .constants import INFO_USER_INCLUDE
from .constants import WARNING_IGNORED
from .instagram import Instagram
from .utils import ask_user_for_input
from .utils import config_validator
from .utils import dump_response
from .utils import filepath_logging
from .utils import home_path


logging.basicConfig(
    filename=filepath_logging(),
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger(__name__)


def init_user_config():
    log.info("Config created at: {}".format(home_path(CONFIG_PATH_JSON)))
    config = [ask_user_for_input()]

    with open(home_path(CONFIG_PATH_JSON), "tw+") as f:
        json.dump(config, f)

    print("Config created at: {}".format(home_path(CONFIG_PATH_JSON)))
    print("Run again to download stories")
    exit()


def get_include_list(download_only) -> list:
    if os.path.isfile(download_only):
        try:
            with open(download_only) as f:
                users = re.findall("^[\d]+", f.read(), re.MULTILINE)
                log.info(INFO_USER_INCLUDE, len(users))
                return users
        except:
            return []

    return []


def read_config(config_file: str, download_only: str) -> dict:
    if not os.path.isfile(config_file):
        init_user_config()

    try:
        with open(config_file) as f:
            json_data = json.load(f)
            if config_validator(json_data):
                config = {
                    "user_list": json_data,
                    "include": get_include_list(download_only),
                }
                return config
            else:
                raise Exception("json_data validate error")

    except IOError:
        raise Exception(f"unable to read {config_file}")

    except json.decoder.JSONDecodeError:
        raise Exception(
            f"unable to parse {config_file} as json",
        )


def download_stories(config: dict, download_ids: list, options: dict):
    username = config["username"]
    json_backup = config["json_backup"]

    instagram = Instagram(config, options)

    log.info(INFO_FETCHING_FOR, username)

    reels_tray = instagram.get_tray()

    dump_response(
        timestamp=int(time.time()),
        content_type="tray_{}".format(config["id"]),
        content=reels_tray,
        prefix=json_backup,
    )

    log.info(INFO_REEL_FOUND, len(reels_tray["tray"]), username)

    user_ids_with_reel = instagram.user_ids()

    if len(download_ids) > 0:
        users_to_download = [a for a in user_ids_with_reel if a in download_ids]
    else:
        users_to_download = user_ids_with_reel

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

                    name = reel["user"]["username"]
                    count = reel["media_count"] or len(reel["items"])
                    pbar.set_description("+{} {} ({})".format(count, name, user_id))
                    log.info(INFO_REEL_FOUND_FOR_USER, count, name, user_id)

                    dump_response(
                        timestamp=int(reel.get("expiring_at")),
                        content_type="user_reel_{}".format(user_id),
                        content=reel,
                        prefix=json_backup,
                    )

                    instagram.download_reel(reel)

                    time.sleep(1)
                    pbar.update(1)
        pbar.set_description("")
        pbar.update(0)
        # else:
        #     ctypes.windll.user32.MessageBoxW(0, "Error Downloading", "instagram-story", 1)

    instagram.close()

    log.warning(WARNING_IGNORED, ", ".join(users_ignored))
    log.info(INFO_FINISH_DOWNLOADING, username)


def main():
    parser = argparse.ArgumentParser(description="Instagram Story downloader")

    parser.add_argument(
        "-f",
        "--config-location",
        type=str,
        default=home_path(CONFIG_PATH_JSON),
        help="Path for loading and storing json config key file. "
        "Defaults to " + home_path(CONFIG_PATH_JSON),
    )
    parser.add_argument(
        "-d",
        "--download-only",
        type=str,
        default=home_path(CONFIG_PATH_INCLUDE),
        help="Download stories listed in the file. "
        "Defaults to " + home_path(CONFIG_PATH_INCLUDE),
    )

    args = parser.parse_args()

    config_filepath = args.config_location or home_path(CONFIG_PATH_JSON)
    download_only = args.download_only

    config = read_config(config_filepath, download_only)

    for user in config.get("user_list"):
        downlaod_ids = config.get("include")
        if user.get("download"):
            download_stories(user, downlaod_ids, args)

    log.info(INFO_ALL_DONE)


if __name__ == "__main__":
    main()
