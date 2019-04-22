# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import stalker.utils as utils
import stalker.utils.useragent as useragent
import stalker.utils.account as account
import stalker.settings as settings


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

    def process_request(self, request, spider):
        if request.meta.get('random'):  # random 模式，不设 account，随机 ua，随机 proxy
            request.meta['proxy'] = utils.get_random_proxy()
            return
        '''
        account_name = request.meta.get('account_name')
        if account_name not in self.account_name2proxy:  # 之前没遇到过的 account
            self.account_name2proxy[account_name] = utils.get_random_proxy()

        request.meta['proxy'] = self.account_name2proxy[account_name]
        '''


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
    def process_request(request, spider):
        print(request.url, request.meta.get('proxy'), request.meta.get('account_name'), request.headers['User-Agent'])

    @staticmethod
    def process_response(response, spider):
        if response.status in [200, 301, 302]:
            return
        utils.perror("BAD RESPONSE", response.status, response.url)