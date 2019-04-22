import datetime
import json
import re
import sys

import requests


def get_random_proxy():
    return "http://" + requests.get("http://127.0.0.1:5010/get/").content.decode('utf-8')


_user_id_pattern = re.compile(r'https://weibo.cn/u/(\d+)')
_username_pattern = re.compile(r'https://weibo.cn/(.+)\??')


def get_id_and_name(url):
    user_id = 0
    username = ""
    if url.startswith("https://weibo.cn/u/"):
        user_id = int(_user_id_pattern.match(url).group(1))
    else:
        username = _username_pattern.match(url).group(1)
    return user_id, username


def get_datetime(time_format="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.now().strftime(time_format)


def beautify_print(obj):
    print(json.dumps(obj, sort_keys=True, indent=4))


def perror(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
