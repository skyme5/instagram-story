"""Instagram class to handle requests to Instagram"""
import json
import logging
import os
import pickle
import time
from datetime import datetime

import requests


class Instagram:
    """This class sets up Instagram class than handles requests
    that fetch data from instagram.com using the provided cookie
    """

    def __init__(self, config, options):
        """This sets up this class to communicate with Instagram."""
        self.log = logging.getLogger(__name__)
        self.options = options
        self.directory = config["media_directory"]
        self.id = config["id"]
        self.cookie = config["headers"]["cookie"]
        self.cj_path = self._get_home_path("cookie-{}".format(self.id))

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
        # Only attempt to load if the cookie file exists.
        if os.path.exists(self.cj_path):
            with open(self.cj_path, "rb") as f:
                self.session.cookies.update(pickle.load(f))

    def _cj_dump(self):
        with open(self.cj_path, "wb") as f:
            pickle.dump(self.session.cookies, f)

    def _get_home_path(self, filename):
        return os.path.join(os.environ["HOME"], ".instagram-story", filename)

    def _get_reels_tray(self):
        """Get reel tray from Instagram API.

        Returns: Reel tray response object
        """
        endpoint = "https://i.instagram.com/api/v1/feed/reels_tray/"
        response = self.session.get(endpoint, timeout=60)
        if response.status_code != requests.codes.ok:  # pylint: disable=no-member
            self.log.error("Status Code %s Error.", response.status_code)
            response.raise_for_status()
        return response

    def get_reels_tray(self):
        """Get reel tray from Instagram API.

        Returns: Reel tray response object
        """
        self.reels_tray = self._get_reels_tray().json()
        return self.reels_tray

    def get_user_reel(self, user_id: str):
        """Get reel tray from Instagram API.

        Returns: Reel tray response object
        """
        endpoint = "https://i.instagram.com/api/v1/feed/reels_media/?reel_ids="
        response = self.session.get(endpoint + user_id, timeout=60)
        if response.status_code != requests.codes.ok:  # pylint: disable=no-member
            self.log.error("Status Code %s Error.", response.status_code)
            response.raise_for_status()
        with open("23.txt", "w", encoding="utf-8") as f:
            f.write(response.text)
        return response.json().get("reels").get(str(user_id))

    def get_user_ids(self) -> list:
        """Extract user IDs from reel tray JSON.

        Args:
            tray: Reel tray response from IG

        Returns:
            List of user IDs
        """
        users = []
        for item in self.reels_tray["tray"]:
            if "user" in item:
                if "pk" in item["user"]:
                    users.append(item["user"]["pk"])
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
                user_id = item["user"]["pk"]
                username = item["user"]["username"]
                if user_id not in download_ids:
                    users.append("{} ({})".format(username, user_id))
        return users

    def dump_filename(self, string):
        filename = self.format_time(time.time(), "cache-%Y-%m-%d_%H.log")
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

    def format_time(self, timestamp, time_fmt):
        return datetime.utcfromtimestamp(timestamp).strftime(time_fmt)

    def format_filepath(
        self,
        user: str,
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

        utcdatetime = self.format_time(timestamp, time_fmt="%Y-%m-%d_%H-%M-%S")
        utcyear = self.format_time(timestamp, time_fmt="%Y")

        if media_type == 1:
            ext = ".jpg"
        elif media_type == 2:
            ext = ".mp4"
        elif media_type == 3:
            ext = ".json"

        filename = utcdatetime + " " + post_id + ".json"

        dirpath = os.path.join(self.directory, str(user_id), utcyear)

        jsonfilepath = os.path.join(dirpath, filename)

        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        if not os.path.exists(jsonfilepath):
            f = open(jsonfilepath, "w+")
            json.dump(content, f)
            f.close()

        path = os.path.join(
            self.directory, str(user_id), utcyear, utcdatetime + " " + post_id + ext
        )

        return path

    def download_reel(self, tray):
        """Download stories of a followed user's tray.

        Download the stories of a followed user.

        Args:
            resp: JSON dictionary of reel from IG API

        Returns:
            None
        """

        username = tray["user"]["username"]
        user_id = tray["user"]["pk"]
        try:
            for item in tray["items"]:
                post_id = item["id"]
                timestamp = item["taken_at"]
                media_type = item["media_type"]
                if media_type == 2:  # Video
                    largest = 0
                    for version, video in enumerate(item["video_versions"]):
                        item_size = video["width"] * video["height"]

                        largest_item = item["video_versions"][largest]
                        width = largest_item["width"]
                        height = largest_item["height"]
                        largest_size = width * height

                        if item_size > largest_size:
                            largest = version

                    url = item["video_versions"][largest]["url"]

                elif media_type == 1:  # Image
                    largest = 0
                    candidates = item["image_versions2"]["candidates"]
                    for version, image in enumerate(candidates):
                        item_size = image["width"] * image["height"]

                        largest_item = item["image_versions2"]["candidates"][largest]
                        width = largest_item["width"]
                        height = largest_item["height"]
                        largest_size = width * height

                        if item_size > largest_size:
                            largest = version

                    url = item["image_versions2"]["candidates"][largest]["url"]

                else:  # Unknown
                    url = None
                    pass

                path = self.format_filepath(
                    username, user_id, timestamp, post_id, media_type, item
                )
                self.download_file(url, path)

        # JSON 'item' key does not exist for later items in tray as of 6/2/2017
        except KeyError:
            pass

    def close(self):
        """Close seesion to IG

        Returns:
            None
        """
        self.session.close()
        self._cj_dump()
