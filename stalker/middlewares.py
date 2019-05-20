# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import json
import logging
import re

import scrapy
import scrapy.exceptions
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.http import Request, Response

import utils
import utils.useragent as useragent
import utils.account as account
import stalker.settings as settings


class FullRandomMiddleware:
    api_to_page_pattern = re.compile(r'info\?uid=')

    def process_request(self, request: Request, spider):
        # retry_times = request.meta.get('retry_times')
        # if retry_times:
        #     retry_times = int(retry_times)
        # else:
        #     retry_times = 0
        #
        # request.headers['referer'] = self.api_to_page_pattern.sub('', request.url)
        #
        # if retry_times < settings.MAX_RETRY_TIMES:
        #     request.meta['proxy'] = utils.get_random_proxy()
        #     request.headers.setdefault('User-Agent', useragent.get_random_useragent())
        # else:
        #     RandomAccountMiddleware.process_request(request, spider)
        #     request.meta['proxy'] = None
        #     request.headers['User-Agent'] = settings.USER_AGENT
        #     request.headers['x-xsrf-token'] = request.cookies.get("XSRF-TOKEN")

        request.headers['referer'] = self.api_to_page_pattern.sub('', request.url)
        # RandomAccountMiddleware.process_request(request, spider)
        request.meta['proxy'] = None
        request.headers['User-Agent'] = settings.USER_AGENT
        # request.headers['x-xsrf-token'] = request.cookies.get("XSRF-TOKEN")


class RandomAccountMiddleware:
    @staticmethod
    def process_request(request, spider):
        if request.meta.get('random'):  # random 模式，不设 account，随机 ua，随机 proxy
            return

        account_name, account_dict = account.get_random_account()
        request.meta['account_name'] = account_name
        request.cookies.update(account_dict)


class RandomHttpProxyMiddleware:
    account_name2proxy = {}

    @staticmethod
    def process_request(request, spider):
        if request.meta.get('random'):  # random 模式，不设 account，随机 ua，随机 proxy
            request.meta['proxy'] = utils.get_random_proxy()
            return

        # account_name = request.meta.get('account_name')
        # if account_name not in self.account_name2proxy:  # 之前没遇到过的 account
        #     self.account_name2proxy[account_name] = utils.get_random_proxy()
        #
        # request.meta['proxy'] = self.account_name2proxy[account_name]


class RandomUserAgentMiddleware:
    account_name2ua = {}

    def process_request(self, request, spider):
        if request.meta.get('random'):  # random 模式，不设 account，随机 ua，随机 proxy
            request.headers.setdefault('User-Agent', useragent.get_random_useragent())
            return

        account_name = request.meta.get('account_name')
        if account_name not in self.account_name2ua:  # 之前没遇到过的 account
            self.account_name2ua[account_name] = useragent.get_random_useragent()

        request.headers.setdefault('User-Agent', self.account_name2ua[account_name])


class HTTPLoggerMiddleware:
    @staticmethod
    def process_request(request: Request, spider):
        # logging.info(
        #     "%s %s %s %s",
        #     request.url,
        #     request.meta.get('proxy'),
        #     request.meta.get('account_name'),
        #     request.headers['User-Agent']
        # )
        print(request.headers, request.cookies, request.body, request.meta)

    @staticmethod
    def process_response(request, response: Response, spider):
        logging.info(response.headers)
        if response.status not in [200]:
            logging.error("BAD RESPONSE %s %s", response.status, request.url)
        return response


class BadResponseDropperMiddleware:
    @staticmethod
    def process_request(request: Request, spider: scrapy.Spider) -> type(None):
        for ignore_url in settings.IGNORE_URLS:
            if not request.url.startswith(ignore_url):
                continue

            account_name = request.meta.get('account_name')
            if account_name:
                logging.critical('ACCOUNT %s FAILED IN %s', account_name, request.url)
                account.remove_account(account_name)
            raise scrapy.exceptions.IgnoreRequest('IGNORE %s' % request.url)
