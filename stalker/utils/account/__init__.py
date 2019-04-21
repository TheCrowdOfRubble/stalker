import functools
import json
import os
import glob
import random

# /run/media/baronhou/Data/Projects/python/a_crowd_of_rubble/stalker/stalker/utils/useragent
_BASE_PATH = os.path.dirname(os.path.realpath(__file__))

_accounts = []


def _reduce_cookie_to_one_line(x1, x2):
    if "expirationDate" in x1:
        x1 = {x1["name"]: x1["value"]}
    x1[x2["name"]] = x2["value"]
    return x1


for account_file_name in glob.glob(os.path.join(_BASE_PATH, 'accounts', '*.json')):
    with open(account_file_name) as f:
        cookie = functools.reduce(_reduce_cookie_to_one_line, json.load(f))
        _accounts.append(cookie)


def get_random_account():
    return random.choice(_accounts)


print("账号加载完毕，共加载账号", len(_accounts), "个")
