# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import functools
import json
import os
import random

import stalker.utils as utils

'''
class StalkerSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class StalkerDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

T = typing.TypeVar('T', bound='RandomUserAgentMiddleware')


class RandomUserAgentMiddleware(object):
    proxy2ua: typing.Dict[str, str] = {}
    ua: fake_useragent.UserAgent

    def __init__(self, crawler: scrapy.spiders.Spider) -> type(None):
        self.ua = fake_useragent.UserAgent(fallback=crawler.settings.get('USER_AGENT', None))

    @classmethod
    def from_crawler(cls: typing.Type[T], crawler: scrapy.spiders.Spider) -> T:
        return cls(crawler)

    def process_request(self, request: scrapy.http.Request, spider: scrapy.spiders.Spider) -> type(None):
        proxy = request.meta.get('proxy')
        if proxy not in self.proxy2ua:
            self.proxy2ua[proxy] = self.ua.ramdom

        request.headers.setdefault('User-Agent', self.proxy2ua[proxy])
'''


class RandomHttpProxyMiddleware():
    @staticmethod
    def process_request(request, spider):
        request.meta['proxy'] = utils.get_random_proxy()


class RandomAccountMiddleware():
    accounts = []
    proxy2account = {}

    def __init__(self):
        def reduce_cookie_to_one_line(x1, x2):
            if "expirationDate" in x1:
                x1 = {x1["name"]: x1["value"]}
            x1[x2["name"]] = x2["value"]
            return x1

        def get_all_accounts(filename):
            with open(os.getcwd() + "/stalker/accounts/" + filename, "r") as account:
                jar = json.load(account)
            return functools.reduce(reduce_cookie_to_one_line, jar)

        self.accounts = list(map(get_all_accounts, os.listdir(os.getcwd() + "/stalker/accounts")))

    def process_request(self, request, spider):
        proxy = request.meta.get('proxy')
        if proxy not in self.proxy2account:
            self.proxy2account[proxy] = random.choice(self.accounts)
        request.cookies = self.proxy2account[proxy]
