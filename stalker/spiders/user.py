# -*- coding: utf-8 -*-
import typing

import scrapy

import stalker.items as items
import parser.user.detail_page
import parser.user.profile_page as profile_parser
import parser.user as user_parser


class UserSpider(scrapy.Spider):
    name = 'user'
    allowed_domains = ['weibo.cn']
    start_urls = ['https://weibo.cn/u/1266321801']

    def parse(self, response: scrapy.http.Response):
        user_item = {
            'user_id': user_parser.get_user_id_from_detail_page(response)
        }
        yield user_parser.parse(response)

    @staticmethod
    def parse1(response: scrapy.http.Response) -> typing.Iterator[items.UserItem]:
        user_detail_page_url = profile_parser.get_user_detail_page_url(response)
        user_id = user_parser.get_user_id_from_profile_page_url(response.url)

        if user_detail_page_url == '':
            return

        user_item = items.UserItem()
        user_item.set_all()

        # 解析用户资料页
        response.meta['user'] = user_item
        user_item = profile_parser.parse(response)

        # 解析用户详情页
        yield scrapy.Request(
            url=user_detail_page_url,
            callback=parser.user.detail_page.parse,
            meta={"user": user_item},
            priority=666,
        )

        # 继续下个用户
        for i in range(1, 1000000):
            yield scrapy.Request(url='https://weibo.cn/%d/info' % (user_id + i))
