# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider


class WorkerSpider(RedisSpider):
    name = 'worker'
    allowed_domains = ['weibo.cn']
    custom_settings = {

    }

    def parse(self, response):
        pass
