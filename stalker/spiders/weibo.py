# -*- coding: utf-8 -*-
import urllib.parse

import scrapy

import parser.user as user_parser
import parser.user.weibo_page as user_weibo_page_parser
import parser.weibo as weibo_parser
import parser.utils.page_count as page_count_parser
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
                callback=user_weibo_page_parser.parse_user_weibo_page,
                meta={'user': user_item},
                priority=333
            )
