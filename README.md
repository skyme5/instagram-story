# Instagram Story

Download instagram stories from your profile.

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

On first run, a config file will be generated. The script will ask for required information such as your username, user id, cookies etc., cookies can be obtained from the developer tools of Google Chrome or Firefox.

To periodically obtain stories from followed users, run this script at least every 24 hours. A Windows Scheduled Task or a Unix cron job is recommended to perform this automatically.

## Legal Disclaimer

This project is in no way affiliated with, authorized, maintained, sponsored or endorsed by Instagram or any of its affiliates or subsidiaries. This is an independent project that utilizes Instagram's unofficial API. Use at your own risk.
