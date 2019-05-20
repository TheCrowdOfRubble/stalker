import glob
import json
import logging
import os
import random

# /run/media/baronhou/Data/Projects/python/a_crowd_of_rubble/stalker/stalker/utils/useragent
_BASE_PATH = os.path.dirname(os.path.realpath(__file__))

_accounts = {}
_account_names = []


def _get_account_name(path: str):
    filename = path.rsplit('/', 1)[1]
    account_name = filename.rsplit('.', 1)[0]
    return account_name


for account_file_name in glob.glob(os.path.join(_BASE_PATH, 'accounts', '*.json')):
    with open(account_file_name) as f:
        account_name = _get_account_name(account_file_name)
        cookies = {}
        for part in json.load(f):
            cookies[part['name']] = part['value']
        _accounts[account_name] = cookies

_account_names = list(_accounts.keys())


def get_random_account():
    random_key = random.choice(_account_names)
    return random_key, _accounts[random_key]


def remove_account(account_name: str) -> type(None):
    try:
        _account_names.remove(account_name)
    except Exception as e:
        pass


logging.info("账号加载完毕，共加载账号 %d 个", len(_accounts))
