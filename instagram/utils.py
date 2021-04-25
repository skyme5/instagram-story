import json
import logging
import os
import time
from datetime import datetime

from jsonschema import validate

from .constants import FMT_DATE
from .constants import FMT_DATETIME
from .constants import USER_ASK_COOKIE
from .constants import USER_ASK_DIRECTORY
from .constants import USER_ASK_USER_ID
from .constants import USER_ASK_USERNAME


log = logging.getLogger(__name__)


def format_time(time_stamp, time_fmt):
    """Format timestamp to custom datetime format.

    Args:
        time_stamp (time): Unix timestamp.
        time_fmt (str): Custom datetime format string.

    Returns:
        str: Custom datetime formatted timestamp.
    """
    return datetime.utcfromtimestamp(time_stamp).strftime(time_fmt)


def home_path(*args):
    """Returns path to home user directory.

    It expands to `~` on UNIX and `%USERPROFILE%` on Windows.

    Any argument provided will be appended to the $HOME.

    Returns:
        str: Path to $HOME.
    """
    home = os.environ["HOME"] or os.path.expanduser("~")
    return os.path.join(home, *args)


def filepath_logging():
    """Custom logging filepath.

    Returns:
        str: Path to custom logging file.
    """
    filedir = ".instagram-story"
    filename = "instagram-story-%Y-%m-%d_%H-%M-%S.log"
    return format_time(time.time(), home_path(filedir, filename))


def dump_text_file(content: str, filepath: str):
    """Write content to filepath using `tx` mode.

    Args:
        content (str): File content to write.
        filepath (str): Filepath.

    This will overwrite the file.
    """
    dirpath = os.path.dirname(filepath)

    os.makedirs(dirpath, exist_ok=True)

    if not os.path.isfile(filepath):
        log.debug("File written: %s", filepath)
        with open(filepath, "w+") as f:
            f.write(content)


def ask_user_for_input():
    username = input(USER_ASK_USERNAME)
    user_id = input(USER_ASK_USER_ID)
    cookie = input(USER_ASK_COOKIE)
    directory = input(USER_ASK_DIRECTORY)
    return {
        "username": username,
        "id": user_id,
        "directory": directory,
        "json_backup": os.path.join(directory, "json"),
        "download": true,
        "headers": {"cookie": cookie},
    }


def config_validator(data: dict):
    """Validate config json data.

    Args:
        data (dict): Config json data

    Returns:
        bool: True if data validated successfully else false.
    """
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
    validate(instance=data, schema=SCHEMA)

    return True


def dump_response(timestamp: int, content_type: str, content: dict, prefix: str):
    """Save JSON file

    Args:
        timestamp: Unix timestamp
        content_type: Name
        content: JSON data
        prefix: Prefix path to save json

    Returns:
        None
    """
    utcdatetime = format_time(timestamp, time_fmt=FMT_DATETIME)
    folder = format_time(timestamp, time_fmt=FMT_DATE)

    filename = "{}_{}.json".format(utcdatetime, content_type)
    path = os.path.join(prefix, folder, filename)
    dump_text_file(json.dumps(content), path)
