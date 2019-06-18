import datetime
import random
import json
import sys
import re

from scrapy.http import Response
from scrapy.utils.project import get_project_settings
import requests

settings = get_project_settings()

extra_proxy_pattern = re.compile('(?<=<p>).+</p>')


def get_random_proxy():
    if random.randint(0, 99) <= int(settings['CHANCE_OF_USE_PROXY']):  # 有几率不使用代理
        return None

    proxy = requests.get(settings['HTTP_PROXY_URL'] + "get/").content.decode('utf-8')
    if proxy == 'no proxy!':
        html = requests.get('http://p.ashtwo.cn/').content.decode('utf-8')
        proxy = extra_proxy_pattern.findall(html)
        if not proxy:
            return None
        proxy = proxy[0]

    return "http://" + proxy


def get_datetime(time_format="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.now().strftime(time_format)


class TimePeriodGetter:
    an_hour_delta = datetime.timedelta(hours=3)  # fake

    def __call__(self):
        now = datetime.datetime.now()

        return (now - self.an_hour_delta).strftime('%Y-%m-%d %H:00:00'), now.strftime('%Y-%m-%d %H:00:00')


def beautify_print(obj):
    print(json.dumps(obj, sort_keys=True, indent=4))


def perror(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_page_amount(response: Response) -> int:
    return int(response.xpath("//div[@id='pagelist']/form/div/text()[last()]").re_first(r'(?<=/).+(?=页)', 1))


# exported functions
get_an_hour_period = TimePeriodGetter()
