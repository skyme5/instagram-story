"""Instagram class to handle requests to Instagram"""
import json
import logging
import os
import pickle
import time
from datetime import datetime

import requests

from .constants import ENDPOINT_REELS_TRAY
from .constants import ENDPOINT_USER_REELS
from .constants import ENDPOINT_USER_REELS_PREFIX
from .constants import MEDIA_TYPE_EXT
from .utils import dump_text_file
from .utils import format_time
from .utils import home_path


class Instagram:
    """Instagram class for handling API requests and downloading files."""

    def __init__(self, config, options):
        """Initialize class variables."""
        self.log = logging.getLogger(__name__)
        self.options = options
        self.directory = config["media_directory"]
        self.id = config["id"]
        self.cookie = config["headers"]["cookie"]
        self.cj_path = home_path(".instagram-story", "cookie-{}".format(self.id))

        self.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "accept-language": "en-US",
            "content_type": "application/x-www-form-urlencoded; charset=UTF-8",
            "cache-control": "no-cache",
            "user-agent": (
                "Mozilla/5.0 (Linux; Android 8.1.0; motorola one Build/OPKS28.63-18-3; wv)"
                " AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0"
                " Chrome/70.0.3538.80 Mobile Safari/537.36"
                " Instagram 72.0.0.21.98"
                " Android (27/8.1.0; 320dpi; 720x1362; motorola; motorola one;"
                " deen_sprout; qcom; pt_BR; 132081645)"
            ),
        }

        self.session = requests.Session()
        self.session.headers = self.headers
        self.session.headers.update({"cookie": self.cookie})

    def _cj_load(self):
        """Load cookies from file."""
        if os.path.exists(self.cj_path):
            with open(self.cj_path, "rb") as f:
                self.session.cookies.update(pickle.load(f))

    def _cj_dump(self):
        """Save Cookies to file."""
        with open(self.cj_path, "wb") as f:
            pickle.dump(self.session.cookies, f)

    def _api_request(self, endpoint):
        """Get reel tray for logged in user from Instagram API.

        Returns: Reel tray response object
        """
        self.log.debug("Making API request %s", endpoint)
        response = self.session.get(endpoint, timeout=60)
        if response.status_code != requests.codes.ok:  # pylint: disable=no-member
            self.log.error(
                "Status Code %s Error for %s.", response.status_code, endpoint
            )
            response.raise_for_status()
        return response

    def get_tray(self):
        """Get reel tray from Instagram API.

        Returns: Reel tray response object
        """
        self.reels_tray = self._api_request(ENDPOINT_REELS_TRAY).json()
        return self.reels_tray

    def _reel_cached(self, user_id: str):
        reel = [
            a
            for a in self.reels_tray["tray"]
            if user_id == str(a["id"]) and a["prefetch_count"] > 0
        ]
        return reel

    def get_reel(self, user_id: str):
        """Get reel tray from Instagram API.

        Returns: Reel tray response object
        """
        cached = self._reel_cached(user_id)
        if len(cached) > 0:
            return cached[0]

        response = self._api_request(ENDPOINT_USER_REELS + user_id)
        return response.json().get("reels").get(user_id)

    def get_reel_chunk(self, user_ids: list):
        """Get reel tray from Instagram API.

        Returns: Reel tray response object
        """
        suffix = "&".join(["reel_ids={}".format(a) for a in user_ids])

        response = self._api_request(ENDPOINT_USER_REELS_PREFIX.format(suffix))
        return response.json().get("reels")

    def user_ids(self) -> list:
        """Extract user IDs from reel tray JSON.

        Returns:
            List of user IDs
        """
        users = []
        for item in self.reels_tray["tray"]:
            if "user" in item:
                if "pk" in item["user"]:
                    users.append(str(item["user"]["pk"]))
        return users

    def ignored_users(self, download_ids: list) -> list:
        """Extract user IDs from reel tray JSON.

        Args:
            tray: Reel tray response from IG

        Returns:
            List of user IDs
        """
        users = []
        for item in self.reels_tray["tray"]:
            if "user" in item:
                user_id = str(item["user"]["pk"])
                username = item["user"]["username"]
                if user_id not in download_ids:
                    users.append("{} ({})".format(username, user_id))
        return users

    def dump_filename(self, string):
        filename = format_time(time.time(), "cache-%Y-%m-%d_%H.log")
        with open(
            os.path.join(os.environ["HOME"], ".instagram-story", filename), "a+"
        ) as archive:
            archive.write(string + "\n")

    def download_file(self, url: str, dest: str):
        """Download file and save to destination

        Args:
            url: URL of item to download
            dest: File system destination to save item to

        Returns:
            None
        """
        self.log.debug("saving url %s => %s", url, dest)

        try:
            if os.path.getsize(dest) == 0:
                self.log.info("Empty file exists. Removing.")
                os.remove(dest)
        except FileNotFoundError:
            pass

        try:
            dirpath = os.path.dirname(dest)
            os.makedirs(dirpath, exist_ok=True)
            with open(dest, "xb") as handle:
                response = self.session.get(url, stream=True, timeout=160)
                if (
                    response.status_code != requests.codes.ok
                ):  # pylint: disable=no-member
                    self.log.error("Status Code %s Error.", response.status_code)
                    response.raise_for_status()
                for data in response.iter_content(chunk_size=4194304):
                    handle.write(data)
                handle.close()

            self.dump_filename(dest)
        except FileExistsError:
            self.log.info("File already exists.")
        # This is the correct syntax
        except requests.exceptions.RequestException:
            self.log.info("Connection was closed")

        if os.path.getsize(dest) == 0:
            self.log.info("Error downloading. Removing.")
            os.remove(dest)

    def format_filepath(
        self,
        user_id: int,
        timestamp: int,
        post_id: str,
        media_type: int,
        content: dict,
    ) -> str:
        """Format download path to a specific format/template

        Args:
            user: User name
            user_id: User ID
            timestamp: UTC Unix timestamp
            post_id: Post ID
            media_type: Media type as defined by IG

        Returns:
            None
        """

        utcdatetime = format_time(timestamp, time_fmt="%Y-%m-%d_%H-%M-%S")
        utcyear = format_time(timestamp, time_fmt="%Y")

        ext = MEDIA_TYPE_EXT[media_type]
        path_prefix = os.path.join(self.directory, str(user_id), utcyear)

        json_filepath = os.path.join(
            path_prefix, "{} {}.json".format(utcdatetime, post_id)
        )

        dump_text_file(json.dumps(content), json_filepath)

        filename = "{} {}{}".format(utcdatetime, post_id, ext)
        path = os.path.join(path_prefix, filename)

        return path

    def download_reel(self, tray):
        """Download story from tray.

        Args:
            tray: Reel response object from API.
        """

        username = tray["user"]["username"]
        user_id = tray["user"]["pk"]
        try:
            for item in tray["items"]:
                post_id = item["id"]
                timestamp = item["taken_at"]
                media_type = item["media_type"]
                if media_type == 2:  # Video
                    url = item["video_versions"][0]["url"]

                elif media_type == 1:  # Image
                    url = item["image_versions2"]["candidates"][0]["url"]

                else:  # Unknown
                    url = None
                    pass

                path = self.format_filepath(
                    user_id, timestamp, post_id, media_type, item
                )
                self.download_file(url, path)

        # JSON 'item' key does not exist for later items in tray as of 6/2/2017
        except KeyError:
            pass

    def close(self):
        """Close seesion to IG."""
        self.session.close()
        self._cj_dump()
