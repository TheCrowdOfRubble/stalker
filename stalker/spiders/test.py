# -*- coding: utf-8 -*-
from typing import Union, Iterator
import urllib.parse as urlparser
import logging

from icecream import ic
import scrapy
from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request, Response
from scrapy.loader.processors import MapCompose, TakeFirst

from stalker.items.processors import get_dict_from_profile, remove_invisible_character, EmptyTo, get_weibo_content
import stalker.parse as parse
import stalker.items as items
import stalker.settings as settings
import utils
from stalker.parse import FetchItemsAndNext


def is_last(parsed_element):
    return False


class TestSpider(RedisSpider):
    name = 'test'
    allowed_domains = ['weibo.cn']
    # start_urls = [
    #     'https://weibo.cn/2803301701/fans'
    # ]
    redis_key = 'start_urls'

    def get_all_user_urls(self, res: Response):
        urls = res.xpath('//div[@class="c"]/table/tr/td[2]/a[1]/@href').getall()
        return urls, True

    def parse(self, response: Response):
        for i in FetchItemsAndNext(self.get_all_user_urls, self.parse)(response):
            yield i
