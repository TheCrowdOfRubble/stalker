# -*- coding: utf-8 -*-
import json
import logging

import scrapy
from scrapy_redis.spiders import RedisSpider

from stalker.items import UserJsonLoader, WeiboJsonLoader
from utils import get_an_hour_period


class MWeiboSpider(RedisSpider):
    name = 'mweibo'
    allowed_domains = ['m.weibo.cn']
    custom_settings = {
        "SCHEDULER": "scrapy_redis.scheduler.Scheduler",
        "DUPEFILTER_CLASS": "scrapy_redis.dupefilter.RFPDupeFilter",

        'DEFAULT_REQUEST_HEADERS': {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-language': 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6',
            'dnt': 1,
            'mweibo-pwa': 1,
            'X-Requested-With': 'XMLHttpRequest'
        },

        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,

            'stalker.middlewares.FullRandomMiddleware': 100,
            'stalker.middlewares.HTTPLoggerMiddleware': 101,
        },

        # "ITEM_PIPELINES": {
        #     'stalker.pipelines.PrintPipeline': 300
        # },
    }

    def parse(self, response):
        FullRandomMiddleware

