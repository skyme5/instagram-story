"""Instagram class to handle requests to Instagram"""
import json
import logging
import os
import time
from datetime import datetime
from http.cookiejar import MozillaCookieJar

import requests


class Instagram:
    """This class sets up Instagram class than handles requests
    that fetch data from instagram.com using the provided cookie
    """

    def __init__(self, config, options):
        """This sets up this class to communicate with Instagram.

        Args:
            cookie: A dictionary object with the required cookie values
            (ds_user_id, sessionid, csrftoken).
        """
        self.options = options
        self.media_directory = config["media_directory"]
        self.userid = config["cookie"]["ds_user_id"]
        self.sessionid = config["cookie"]["sessionid"]
        self.csrftoken = config["cookie"]["csrftoken"]
        self.mid = config["cookie"]["mid"]

        cookie = "ds_user_id={}; sessionid={}; csrftoken={}; mid={} dnt: 1"
        self.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "accept-language": "en-US",
            "content_type": "application/x-www-form-urlencoded; charset=UTF-8",
            "cache-control": "no-cache",
            "cookie": cookie.format(
                self.userid, self.sessionid, self.csrftoken, self.mid
            ),
            # "pragma" : "no-cache",
            # "referer" : "https://www.instagram.com/",
            "user-agent": (
                "Instagram 10.26.0 (iPhone7,2; iOS 10_1_1;"
                " en_US; en-US; scale=2.00; gamut=normal;"
                " 750x1334) AppleWebKit/420+"
            ),
            "x-ig-capabilities": "36oD",
            # "x-ig-connection-type" : "WIFI",
            # "x-ig-fb-http-engine" : "Liger"
        }

        self.session = requests.Session()
        self.session.headers = self.headers

    def get_reel_tray(self):
        """Get reel tray from API.

        Returns:
            Response object with reel tray API response
        """
        endpoint = "https://i.instagram.com/api/v1/feed/reels_tray/"
        response = self.session.get(endpoint, timeout=60)
        if response.status_code != requests.codes.ok:  # pylint: disable=no-member
            logging.error("Status Code %s Error.", response.status_code)
            response.raise_for_status()

        return response

    def get_reel_media(self, user):
        """Get reel media of a user from API.

        Args:
            user: User ID

        Returns:
            Response object with reel media API response
        """
        endpoint = (
            "https://i.instagram.com/api/v1/feed/user/" + str(user) + "/reel_media/"
        )
        response = self.session.get(endpoint, timeout=60)
        if response.status_code != requests.codes.ok:  # pylint: disable=no-member
            logging.error("Status Code %s Error.", response.status_code)
            return False
        return response

    def get_user_stories(self):
        return self.get_reel_tray()

    def get_users_stories_reel(self, user):
        return self.get_reel_media(user)

    def get_users_id(self, tray: dict):
        """Extract user IDs from reel tray JSON.

        Args:
            tray: Reel tray response from IG

        Returns:
            List of user IDs
        """
        users = []
        for user in tray["tray"]:
            if "user" in user:
                if "pk" in user["user"]:
                    users.append(user["user"]["pk"])
        return users

    def get_ignored_users(self, tray: dict, download: list) -> list:
        """Extract user IDs from reel tray JSON.

        Args:
            tray: Reel tray response from IG

        Returns:
            List of user IDs
        """
        users = []
        for user in tray["tray"]:
            if "user" in user:
                if "pk" in user["user"]:
                    user_id = user["user"]["pk"]
                    if user_id not in download:
                        users.append(
                            "{} ({})".format(user["user"]["username"], user_id)
                        )
        return users

    def history_save_filenames(self, string):
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
        logging.debug("saving url %s => %s", url, dest)

        try:
            if os.path.getsize(dest) == 0:
                logging.info("Empty file exists. Removing.")
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
                    logging.error("Status Code %s Error.", response.status_code)
                    response.raise_for_status()
                for data in response.iter_content(chunk_size=4194304):
                    handle.write(data)
                handle.close()

            self.history_save_filenames(dest)
        except FileExistsError:
            logging.info("File already exists.")
        # This is the correct syntax
        except requests.exceptions.RequestException:
            logging.info("Connection was closed")

        if os.path.getsize(dest) == 0:
            logging.info("Error downloading. Removing.")
            os.remove(dest)

    def format_time(self, timestamp, time_fmt):
        return datetime.utcfromtimestamp(timestamp).strftime(time_fmt)

    def format_filepath(
        self,
        user: str,
        pk: int,
        timestamp: int,
        post_id: str,
        media_type: int,
        content: dict,
    ) -> str:
        """Format download path to a specific format/template

        Args:
            user: User name
            pk: User ID
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

        dirpath = os.path.join(self.media_directory, str(pk), utcyear)

        jsonfilepath = os.path.join(dirpath, filename)

        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        if not os.path.exists(jsonfilepath):
            f = open(jsonfilepath, "w+")
            json.dump(content, f)
            f.close()

        path = os.path.join(
            self.media_directory, str(pk), utcyear, utcdatetime + " " + post_id + ext
        )

        return path

    def get_largest_image(self, item, largest):
        return item["image_versions2"]["candidates"][largest]

    def download_user_reel(self, resp):
        """Download stories of a followed user's tray.

        Download the stories of a followed user.

        Args:
            resp: JSON dictionary of reel from IG API

        Returns:
            None
        """
        try:
            for item in resp["items"]:
                username = item["user"]["username"]
                post_pk = item["user"]["pk"]
                timestamp = item["taken_at"]
                post_id = item["id"]
                media_type = item["media_type"]
                if media_type == 2:  # Video
                    largest = 0
                    for version, video in enumerate(item["video_versions"]):
                        item_size = video["width"] * video["height"]
                        largest_size = (
                            item["video_versions"][largest]["width"]
                            * item["video_versions"][largest]["height"]
                        )
                        if item_size > largest_size:
                            largest = version

                    url = item["video_versions"][largest]["url"]

                elif media_type == 1:  # Image
                    largest = 0
                    candidates = item["image_versions2"]["candidates"]
                    for version, image in enumerate(candidates):
                        item_size = image["width"] * image["height"]
                        largest_item = self.get_largest_image(item, largest)
                        width = largest_item["width"]
                        height = largest_item["height"]
                        largest_size = width * height

                        if item_size > largest_size:
                            largest = version

                    url = self.get_largest_image(item, largest)["url"]

                else:  # Unknown
                    url = None
                    pass

                path = self.format_filepath(
                    username, post_pk, timestamp, post_id, media_type, item
                )
                self.download_file(url, path)

        # JSON 'item' key does not exist for later items in tray as of 6/2/2017
        except KeyError:
            pass

    def download_user_tray(self, resp):
        """Download stories of logged in user's tray.

        Download the stories as available in the tray. The tray contains a list
        of reels, a collection of the stories posted by a followed user.

        The tray only contains a small set of reels of the first few users.
        To download the rest, a reel must be obtained for each user in the
        tray.

        Args:
            resp: JSON dictionary of tray from IG API

        Returns:
            None
        """
        for reel in resp["tray"]:
            self.download_user_reel(reel)

    def close(self):
        """Close seesion to IG

        Returns:
            None
        """
        self.session.close()
