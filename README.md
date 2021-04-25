<p>
  <div align="center">
  <h1>
    Instagram Story Downloader<br /> <br />
    <a href="https://pypi.python.org/pypi/instagram-story">
      <img
        src="https://img.shields.io/pypi/v/instagram-story.svg"
        alt="Python Package"
      />
    </a>
    <a href="https://pypi.python.org/pypi/instagram-story">
      <img
        src="https://img.shields.io/github/workflow/status/skyme5/instagram-story/publish"
        alt="CI"
      />
    </a>
    <a href="https://codecov.io/gh/skyme5/instagram-story">
      <img
        src="https://img.shields.io/pypi/pyversions/instagram-story"
        alt="Python Versions"
      />
    </a>
    <a href="https://github.com/psf/black">
      <img
        src="https://img.shields.io/badge/code%20style-black-000000.svg"
        alt="The Uncompromising Code Formatter"
      />
    </a>
    <a href="https://pepy.tech/project/instagram-story">
      <img
        src="https://static.pepy.tech/badge/instagram-story"
        alt="Monthly Downloads"
      />
    </a>
    <a href="https://opensource.org/licenses/MIT">
      <img
        src="https://img.shields.io/badge/License-MIT-blue.svg"
        alt="License: MIT"
      />
    </a>
  </h1>
  </div>
</p>

## Installation

Install using pip

```bash
$ pip install -U instagram-story
```

## Usage

```text
usage: instagram-story [-h] [-f CONFIG_LOCATION] [-d DOWNLOAD_ONLY]

Instagram Story downloader

optional arguments:
  -h, --help            show this help message and exit
  -f CONFIG_LOCATION, --config-location CONFIG_LOCATION
                        Path for loading and storing config key file.
  -d DOWNLOAD_ONLY, --download-only DOWNLOAD_ONLY
                        Download stories for user id listed in the file.
```

On first run, a config file will be generated. The script will ask for required information such as your username, user id, cookies etc., cookies can be obtained from the developer tools of Google Chrome or Firefox. For this you can install the [EditThisCooki](http://www.editthiscookie.com/) extension and export your instagram cookie in comma separated values

```text
csrftoken=value;ds_user_id=value;ig_did=value;ig_nrcb=value;mid=value;rur=value;sessionid=value;shbid=value;shbts=value;
```

Value of `ds_user_id` is your instagram user id.

To periodically obtain stories from followed users, run this script at least every 24 hours. A Windows Scheduled Task or a Unix cron job is recommended to perform this automatically.

## Legal Disclaimer

> This project is in no way affiliated with, authorized, maintained, sponsored or endorsed by Instagram or any of its affiliates or subsidiaries. This is an independent project that utilizes Instagram's unofficial API. Use at your own risk.
