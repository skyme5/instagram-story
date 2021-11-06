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
        src="https://pepy.tech/badge/instagram-story"
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
  <a href="https://buymeacoffee.com/skyme5" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;" ></a>
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

## Options

On first run, a config file will be generated. The script will ask for required information such as your username, user id, cookies etc., cookies can be obtained from the developer tools of Google Chrome or Firefox.

For exporting cookies you can install the [EditThisCooki](http://www.editthiscookie.com/) extension and follow [this guide](http://www.editthiscookie.com/blog/2014/03/import-export-cookies/) for exporting cookies in comma-separated format. (For this you need to set `Extension->Settings->Options->Choose the preferred export format for cookies`->`Semicolon separated name=value pairs`).

```text
csrftoken=value;ds_user_id=value;ig_did=value;ig_nrcb=value;mid=value;rur=value;sessionid=value;shbid=value;shbts=value;
```

Value of `ds_user_id` is your instagram user id.

To periodically obtain stories from followed users, run this script at least every 24 hours. A Windows Scheduled Task or a Unix cron job is recommended to perform this automatically.

### Download only selected users

There is a options to download only user ids listed in `include.txt` text file. If the option `-d` or `--download-only` and points to a valid text file with list of user ids then the story will be downloaded for only those id listed in this file.

## Example

```text
E:\>instagram-story
Enter your instagram username: instagrm-test
Enter your instagram user id: 501517166
Enter your instagram cookie: ig_did=52FED55D-4C3E-408F-997C-803D6385D39A; mid=c1e513b4990f_94603666c341ef61; csrftoken=AR6+5nk3N0S3xkTrRc9Pfg; ds_user_id=501517166; sessionid=501517166%3A94603666c341ef61%2a1; shbid=2051; shbts=1619505936.8752491; rur=ARN
Enter directory for saving media files (defaults to directory): B:\story
Config created at: C:\msys64\home\me\.instagram-story\config.json
Run again to download stories
```

## Legal Disclaimer

> This project is in no way affiliated with, authorized, maintained, sponsored or endorsed by Instagram or any of its affiliates or subsidiaries. This is an independent project that utilizes Instagram's unofficial API. Use at your own risk.
