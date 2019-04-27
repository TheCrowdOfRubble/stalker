import datetime
import json
import sys

import requests


def get_random_proxy() -> str:
    return "http://" + requests.get("http://127.0.0.1:5010/get/").content.decode('utf-8')


def get_datetime(time_format="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.now().strftime(time_format)


def beautify_print(obj):
    print(json.dumps(obj, sort_keys=True, indent=4))


def perror(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
