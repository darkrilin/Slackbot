from urllib.parse import urlencode
from urllib.request import urlopen
import time
import json
import codecs
import os

reader = codecs.getreader("utf-8")

token = os.environ['SLACK_TEST_TOKEN']

#Delete files older than this:
days = 14
ts_to = int(time.time()) - days * 24 * 60 * 60

params = dict()


def list_files():
    params = {
        'token':token,
        'ts_to':ts_to,
        'count':500,
    }
    uri = 'https://slack.com/api/files.list'
    response = reader(urlopen(uri + '?' + urlencode(params)))
    return json.load(response)['files']


def delete_files(file_ids):
    size = 0
    count = 0
    num_files = len(file_ids)
    for file_id in file_ids:
        count = count + 1
        params = {
            'token':token,
            'file':file_id
        }

        uri = 'https://slack.com/api/files.info'
        response = reader(urlopen(uri + '?' + urlencode(params)))
        size += json.load(response)['file']['size']

        uri = 'https://slack.com/api/files.delete'
        response = reader(urlopen(uri + '?' + urlencode(params)))

        print(count, "of", num_files, "-", file_id, json.load(response)['ok'], " ... ", '{0:.2f} MB saved'.format(size / 1048576))


def total_file_size():
    params = {
        'token': token,
        'count': 500,
    }
    uri = 'https://slack.com/api/files.list'
    response = reader(urlopen(uri + '?' + urlencode(params)))
    size = 0

    file_ids = [f['id'] for f in json.load(response)['files']]
    print(len(file_ids))
    for file_id in file_ids:
        params = {
            'token': token,
            'file': file_id
        }

        uri = 'https://slack.com/api/files.info'
        response = reader(urlopen(uri + '?' + urlencode(params)))
        size += json.load(response)['file']['size']
        print('{0:.2f} MB total'.format(size / 1048576))

    return '{0:.2f} MB'.format(size / 1048576)


files = list_files()
file_ids = [f['id'] for f in files]
delete_files(file_ids)
print(str(len(file_ids)) + " files deleted")

print(total_file_size())
