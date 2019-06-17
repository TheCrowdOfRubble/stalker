# -*- coding: utf-8 -*-
import json
import logging

from scrapy_redis.spiders import RedisSpider

from items import WeiboJsonLoader, UserJsonLoader


class MWeiboCnSpider(RedisSpider):
    name = 'm.weibo.cn'
    allowed_domains = ['m.weibo.cn']
    custom_settings = {
        "SCHEDULER": "scrapy_redis.scheduler.Scheduler",
        'COOKIES_ENABLED': False,

        'DEFAULT_REQUEST_HEADERS': {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6',
            'dnt': 1,
            'mweibo-pwa': 1,
            'X-Requested-With': 'XMLHttpRequest'
        },

        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'stalker.middlewares.MWeiboMiddleware': 1,
            'stalker.middlewares.LoggerMiddleware': 999,
        },
    }

    def parse(self, response):
        try:
            json_response = json.loads(response.body_as_unicode())
        except Exception as _:
            logging.critical("NOT JSON RESPONSE IN %s", response.url)
            return

        try:
            user = json_response['data']['user']
            weiboes = json_response['data']['statuses']
        except Exception as _:
            logging.critical("BAD RESPONSE IN %s AS %s", response.url, json_response)
            return

        yield UserJsonLoader(user).load_item()

        for weibo in weiboes:
            yield WeiboJsonLoader(weibo).load_item()

