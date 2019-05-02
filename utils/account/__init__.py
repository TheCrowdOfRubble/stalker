import functools
import json
import os
import glob
import random
import logging

# /run/media/baronhou/Data/Projects/python/a_crowd_of_rubble/stalker/stalker/utils/useragent
_BASE_PATH = os.path.dirname(os.path.realpath(__file__))

_accounts = {}
_account_names = []


def _reduce_cookie_to_one_line(x1, x2):
    if "expirationDate" in x1:
        x1 = {x1["name"]: x1["value"]}
    x1[x2["name"]] = x2["value"]
    return x1


for account_file_name in glob.glob(os.path.join(_BASE_PATH, 'accounts', '*.json')):
    with open(account_file_name) as f:
        cookie = functools.reduce(_reduce_cookie_to_one_line, json.load(f))
        _accounts[account_file_name] = cookie

_account_names = list(_accounts.keys())


# def _str2dict(cookies_str):
#     cookies = {}
#     items = cookies_str.split(';')
#     for item in items:
#         key = item.split('=')[0].replace(' ', '')  # 记得去除空格
#         value = item.split('=')[1]
#         cookies[key] = value
#     return cookies
#
#
# with open(os.path.join(_BASE_PATH, 'accounts.json')) as f:
#     accounts = json.load(f)
#     for account_name in accounts:
#         _accounts[account_name] = _str2dict(accounts[account_name])
#     _account_names = list(_accounts.keys())


def get_random_account():
    random_key = random.choice(_account_names)
    return random_key, _accounts[random_key]


def remove_account(account_name: str) -> type(None):
    pass
    # try:
    #     _account_names.remove(account_name)
    # except Exception as e:
    #     pass


logging.info("账号加载完毕，共加载账号 %d 个", len(_accounts))
