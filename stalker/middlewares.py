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


class RandomHttpProxyMiddleware:
    @staticmethod
    def process_request(request, spider):
        request.meta['proxy'] = utils.get_random_proxy()


class RandomAccountMiddleware:
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
