import datetime
import json
import re

import requests


def get_random_proxy():
    return "http://" + requests.get("http://127.0.0.1:5010/get/").content.decode('utf-8')


def get_id_and_name(url):
    user_id = 0
    username = ""
    if url.startswith("https://weibo.cn/u/"):
        user_id = int(url[19:])
    else:
        username = url[17:]
    return user_id, username


def get_datetime(time_format):
    return datetime.datetime.now().strftime(time_format)


def get_insert_sql(table_name, fields):
    keys = ""
    values = ""
    for field_name in fields:
        keys += "`%s`," % field_name
        values += "%s,"
    return "INSERT INTO `%s` (%s) VALUES (%s)" % (table_name, keys[:-1], values[:-1])


def beautify_print(obj):
    print(json.dumps(obj, sort_keys=True, indent=4))
