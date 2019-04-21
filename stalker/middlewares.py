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
import stalker.utils.useragent as useragent
import stalker.utils.account as account
import stalker.settings as settings


class RandomHttpProxyMiddleware:
    @staticmethod
    def process_request(request, spider):
        request.meta['proxy'] = utils.get_random_proxy()


class RandomUserAgentMiddleware:
    proxy2ua = {}

    def process_request(self, request, spider):
        proxy = request.meta.get('proxy')  # 没有返回 None

        if proxy is not None:
            if proxy not in self.proxy2ua:
                self.proxy2ua[proxy] = useragent.get_random_useragent()  # None 也可当 key
            request.headers.setdefault('User-Agent', self.proxy2ua[proxy])
        else:
            request.headers.setdefault('User-Agent', settings.USER_AGENT)


class RandomAccountMiddleware:
    proxy2account = {}

    def process_request(self, request, spider):
        proxy = request.meta.get('proxy')  # 没有返回 None

        if proxy is not None:
            if proxy not in self.proxy2account:
                self.proxy2account[proxy] = account.get_random_account()  # None 也可当 key
            request.cookies.update(self.proxy2account[proxy])
        else:
            request.cookies.update(account.get_random_account())

        print(request.url, request.meta.get('proxy'), request.cookies)
