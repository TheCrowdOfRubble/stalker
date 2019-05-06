import urllib.parse as urlparser
import logging

import datetime
import json
import sys

import requests
import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Compose, SelectJmes

import stalker.settings as settings


def get_random_proxy() -> str:
    return "http://" + requests.get("http://127.0.0.1:5010/get/").content.decode('utf-8')


def get_datetime(time_format="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.now().strftime(time_format)


_an_hour_delta = datetime.timedelta(hours=1)


def get_an_hour_period():
    now = datetime.datetime.now()

    return (now - _an_hour_delta).strftime('%Y-%m-%d %H:00:00'), now.strftime('%Y-%m-%d %H:00:00')


def beautify_print(obj):
    print(json.dumps(obj, sort_keys=True, indent=4))


def perror(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def move_to_next_page(url: str, page_id=-1) -> (int, str):
    url_components: urlparser.ParseResult = urlparser.urlparse(url)
    query = dict(urlparser.parse_qsl(url_components.query, keep_blank_values=True))
    if page_id == -1:
        if 'page' in query:
            page_id = Compose(SelectJmes('page'), int)(query)
            if page_id < 1:
                page_id = 1
            if page_id <= settings.MAX_PAGE_VISIT:
                page_id += 1
        else:
            page_id = 2

    query['page'] = page_id
    url_components = urlparser.ParseResult(
        scheme=url_components.scheme,
        netloc=url_components.netloc,
        path=url_components.path,
        params=None,
        query=urlparser.urlencode(query),
        fragment=None
    )
    next_page_url = urlparser.urlunparse(url_components)

    return page_id, next_page_url


def get_page_amount(response: scrapy.http.Response) -> int:
    return int(response.xpath("//div[@id='pagelist']/form/div/text()[last()]").re_first(r'(?<=/).+(?=页)', 1))


def is_my_account(response: scrapy.http.Response) -> bool:
    forms = response.css('form::attr(action)')
    if len(forms) <= 0 or len(forms) > 3:
        logging.info('BAD USER DETAIL PAGE: %s', response.url)
        return True  # 即便是坏页面，也要返回 True，以防 parse 进入下面的逻辑

    action = forms.get()
    if action.startswith('https://weibo.cn/mblog/sendmblog'):
        return True

    return False
