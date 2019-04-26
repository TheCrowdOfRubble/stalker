# -*- coding: utf-8 -*-
import urllib.parse

import scrapy

import stalker.parser.user as user_parser
import stalker.parser.weibo as weibo_parser
import stalker.parser.page_count as page_count_parser
import stalker.settings as settings


class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['weibo.cn']
    start_urls = settings.START_URLS

    def parse(self, response: scrapy.http.Response):
        user_item = {
            'user_id': user_parser.get_user_id_from_detail_page(response)
        }
        yield user_parser.parse(response)

        # 获得个人微博
        for weibo in weibo_parser.parse(response, user_item):
            yield weibo

        page_count = page_count_parser.parse(response)
        for page in range(2, min(page_count, settings.MAX_PAGE_VISIT)):  # 从第二页开始
            yield scrapy.Request(
                url=urllib.parse.urljoin(response.url, "?page=%d" % page),
                callback=self.parse_user_weibo_page,
                meta={'user_item': user_item},
                priority=333
            )

    @staticmethod
    def parse_user_weibo_page(response):
        user_item = response.meta.get('user_item')
        for weibo in weibo_parser.parse(response, user_item):
            yield weibo
