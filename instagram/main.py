import json
import logging
import sys
import time
from datetime import datetime
import os
import tarfile
import argparse

from jsonschema import validate
from loguru import logger
from tqdm import tqdm

from .instagram import Instagram


def format_time(timestamp, time_fmt):
    return datetime.utcfromtimestamp(timestamp).strftime(time_fmt)


timestamp = time.time()
filename = format_time(timestamp, 'instagram-story-%Y-%m-%d_%H-%M-%S.log')
logging.basicConfig(filename=filename, level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S')


def default_config():
    return 'instagram-story.config.json'


def archive_json():
    logging.info('Collecting list of JSON objects.')

    json_list = []
    for file in os.listdir('json'):
        if file.endswith('.json'):
            json_list.append(os.path.join('json', file))

    logging.info('Creating tar.xz file of JSON objects.')

    filename = format_time(time.time(), time_fmt='%Y-%m-%d_%H-%M-%S.tar.xz')
    path = os.path.join(os.getcwd(), 'json', filename)

    tar = tarfile.open(path, 'x:xz')
    for path in json_list:
        tar.add(path)
    tar.close()

    logging.info('Removing old JSON objects.')
    for path in json_list:
        os.remove(path)


def save_json(timestamp: int, content_type: str, content: dict, dirpath: str):
    """Save JSON file

    Args:
        timestamp: Unix timestamp
        content_type: Name
        content: JSON data
        dirpath: Prefix path to save json

    Returns:
        None
    """

    utcdatetime = format_time(timestamp, time_fmt='%Y-%m-%d_%H-%M-%S')
    utcyear = format_time(timestamp, time_fmt='%Y')

    filename = "{}_{}.json".format(utcdatetime, content_type)
    path = os.path.join(dirpath, utcyear, filename)

    dirpath = os.path.dirname(path)

    os.makedirs(dirpath, exist_ok=True)

    with open(path, 'tx') as f:
        json.dump(content, f)


def ask_user_config():
    logging.info('Creating config file')
    user_id = input('Enter your instagram user ID: ')
    session_id = input('Enter your instagram session ID: ')
    csrf_token = input('Enter your instagram CSRF token: ')
    mid = input('Enter your instagram mid: ')
    media_directory = input('Enter media save directory '
                            '(default current directory): ')
    config = [
        {
            'cookie': {
                'ds_user_id': user_id,
                'sessionid': session_id,
                'csrftoken': csrf_token,
                'mid': mid,
            },
            'media_directory': media_directory,
            'json_backup': 'json',
        }
    ]
    logging.info('Saving config.')

    with open(default_config(), 'tw+') as f:
        json.dump(config, f)

    return config


def validate_config(json_data):
    SCHEMA = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'cookie': {
                    'type': 'object',
                    'properties': {
                        'ds_user_id': {'type': 'string'},
                        'sessionid': {'type': 'string'},
                        'csrftoken': {'type': 'string'},
                        'mid': {'type': 'string'},
                    }
                },
                'username': {'type': 'string'},
                'media_directory': {'type': 'string'},
                'json_backup': {'type': 'string'},
                'download': {'type': 'boolean'},
            }
        }
    }
    validate(instance=json_data, schema=SCHEMA)

    return True


def get_config(config_file):
    if(os.path.isfile(config_file)):
        try:
            with open(config_file) as f:
                json_data = json.load(f)
                if validate_config(json_data):
                    return json_data

        except IOError:
            raise Exception(f'unable to read {config_file}')
            sys.exit(1)

        except json.decoder.JSONDecodeError:
            raise Exception(f'unable to parse {config_file} as json')
            sys.exit(1)
    else:
        logger.info(
            f'Creating {config_file} file in the current directory'
        )
        return ask_user_config()


def download_stories(config, options):
    print(f'Downloading stories for {config["username"]}')
    logging.info('Initializing module')

    instagram = Instagram(config, options)

    logging.info(f'Fetching stories for user: {config["username"]}')

    traytime = int(time.time())

    storyjson = instagram.get_user_stories().json()

    save_json(timestamp=traytime, content_type='tray', content=storyjson,
              dirpath=config['json_backup'])

    logging.info(f'Found {len(storyjson)} stories for'
                 f' user: {config["username"]}')

    instagram.download_user_tray(storyjson)
    users = instagram.get_users_id(storyjson)

    for user in tqdm(users):
        reeltime = int(time.time())
        uresp = instagram.get_users_stories_reel(user)
        ujson = uresp.json()
        save_json(timestamp=reeltime, content_type='reel_' + str(user),
                  content=ujson, dirpath=config['json_backup'])
        instagram.download_user_reel(ujson)

    logging.info('Finished downloading stoeies for user: '
                 + config["username"])


def main():
    """ Main function

    Returns:
        None
    """

    logging.info('Starting application.')

    parser = argparse.ArgumentParser(description='Instagram Story downloader')

    parser.add_argument('-f', '--config-location',
                        type=str,
                        help='Path for loading and storing config key file. '
                        'Defaults to ' + default_config())

    parser.add_argument('-s', '--save-list',
                        action='store_true',
                        help='Save the list of files downloaded to text file.')

    args = parser.parse_args()

    if args.config_location is not None:
        config_file = args.config_location
    else:
        config_file = default_config()

    for config in get_config(config_file):
        download_stories(config=config, options=args)

    logging.info('Shutting down application.')


if __name__ == '__main__':
    main()
