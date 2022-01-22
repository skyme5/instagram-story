import os

"""Filenames"""
CONFIG_DIR = ".instagram-story"
CONFIG_FILENAME_INCLUDE = "include.txt"
CONFIG_FILENAME_JSON = "config.json"

CONFIG_PATH_INCLUDE = os.path.join(CONFIG_DIR, CONFIG_FILENAME_INCLUDE)
CONFIG_PATH_JSON = os.path.join(CONFIG_DIR, CONFIG_FILENAME_JSON)

"""Datetime Format"""
FMT_DATE = "%Y-%m-%d"
FMT_DATETIME = "%Y-%m-%d_%H-%M-%S"

"""User input string"""
USER_ASK_COOKIE = "Enter your instagram cookie: "
USER_ASK_DIRECTORY = "Enter directory for saving media files (defaults to directory): "
USER_ASK_USERNAME = "Enter your instagram username: "
USER_ASK_USER_ID = "Enter your instagram user id: "

INFO_ALL_DONE = "Shutting down application."
INFO_DOWNLOADING = "Downloading stories for {} ({}/{})"
INFO_FETCHING_FOR = "Fetching stories for user: %s"
INFO_FINISH_DOWNLOADING = "Finished downloading stories for user: %s"
INFO_REEL_FOUND = "Found %s stories for user: %s"
INFO_REEL_FOUND_FOR_USER = "Found %s stories for %s (%s)"
INFO_USER_INCLUDE = "Found %s users in include.txt"

WARNING_IGNORED = "Following users were ignored: %s"

"""API Endpoints"""
ENDPOINT_REELS_TRAY = "https://i.instagram.com/api/v1/feed/reels_tray/"
ENDPOINT_USER_REELS = "https://i.instagram.com/api/v1/feed/reels_media/?reel_ids="
ENDPOINT_USER_REELS_PREFIX = "https://i.instagram.com/api/v1/feed/reels_media/?{}"

"""Instagram Media Id to Extension mapping"""
MEDIA_TYPE_EXT = ["", ".jpg", ".mp4", ".json"]
