from urllib.parse import urlencode
from urllib.request import urlopen
from time import time
from json import load
from codecs import getreader
from os import environ

reader = getreader("utf-8")
token = environ['SLACK_TEST_TOKEN']  # Uses legacy test API token - TODO: This will need to be updated

days = 14  # Purge files older than 14 days
timestamp = int(time()) - days * 24 * 60 * 60


def list_files(slack_token, ts_to):
    """
    Fetches a list of all the public files on the slack server
    :param slack_token:
    :param ts_to: Files created before this timestamp
    :return: List of public files
    """
    params = {
        'token': slack_token,
        'ts_to': ts_to,
        'count': 500,
    }

    response = reader(urlopen('https://slack.com/api/files.list?' + urlencode(params)))
    file_list = load(response)['files']

    return file_list


def delete_files(file_ids, slack_token, verbose=False):
    """
    Deletes all files with IDs matching the given list
    :param file_ids:
    :param slack_token:
    :param verbose:
    """
    size = 0
    count = 0
    num_files = len(file_ids)

    for file_id in file_ids:
        count += 1
        params = {
            'token': slack_token,
            'file': file_id
        }

        response = reader(urlopen('https://slack.com/api/files.info?' + urlencode(params)))
        size += load(response)['file']['size']

        response = reader(urlopen('https://slack.com/api/files.delete?' + urlencode(params)))
        ok = load(response)['ok']
        mb = size / 1048576

        if verbose:
            print("{0} of {1} - {2} {3} ... {4:.2f} MB saved".format(count, num_files, file_id, ok, mb))


def total_file_size(slack_token, verbose=False):
    """
    Finds the total size of all files on the slack server
    :param slack_token:
    :param verbose:
    :return:
    """
    params = {
        'token': slack_token,
        'count': 500,
    }
    response = reader(urlopen('https://slack.com/api/files.list?' + urlencode(params)))
    size = 0

    file_ids = [f['id'] for f in load(response)['files']]
    for file_id in file_ids:
        params = {
            'token': token,
            'file': file_id
        }

        response = reader(urlopen('https://slack.com/api/files.info?' + urlencode(params)))
        size += load(response)['file']['size']
        mb = size / 1048576
        if verbose:
            print('{0:.2f} MB total'.format(mb))

    mb = size / 1048576
    return '{0:.2f} MB'.format(mb)


if __name__ == '__main__':
    files = [f['id'] for f in list_files(token, timestamp)]
    delete_files(files, token, verbose=True)

    print("{} files deleted".format(len(files)))
    print(total_file_size(token))
