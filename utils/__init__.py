import datetime
import random
import json
import sys

from scrapy.http import Response
from scrapy.utils.project import get_project_settings
import requests

settings = get_project_settings()


def get_random_proxy():
    if random.randint(0, 9) <= int(settings['CHANCE_OF_USE_PROXY']):  # 有几率不使用代理
        return None

    proxy = requests.get(settings['HTTP_PROXY_URL'] + "get/").content.decode('utf-8')
    if proxy == 'no proxy!':
        return None

    return "http://" + requests.get(settings['HTTP_PROXY_URL'] + "get/").content.decode('utf-8')


def get_datetime(time_format="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.now().strftime(time_format)


class TimePeriodGetter:
    an_hour_delta = datetime.timedelta(hours=2)  # fake

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
