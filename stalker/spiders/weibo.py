# -*- coding: utf-8 -*-
import json
from typing import List, Callable

import scrapy
import stalker.items as items


class WeiboSpider(scrapy.Spider):
    name: str = 'weibo'
    allowed_domains = ['weibo.cn']
    start_urls: List[str] = [
        'https://weibo.cn/rmrb',
    ]

    def parse(self, response: scrapy.http.Response) -> type(None):
        """
        用以处理个人微博页
        """
        user_item = items.UserItem()

        if response.url.startswith("https://weibo.cn/u/"):
            user_item["user_id"] = int(response.url[19:])
        else:
            user_item["username"] = response.url[17:]
        statistics = response.css(".tip2")
        user_item["weibo_amount"] = int(statistics.re_first(r"(?<=微博\[)\d+(?=\])", 0))
        user_item["weibo_amount"] = int(statistics.re_first(r"(?<=微博\[)\d+(?=\])", 0))
        user_item["follow_amount"] = int(statistics.re_first(r"(?<=关注\[)\d+(?=\])", 0))
        user_item["follower_amount"] = int(statistics.re_first(r"(?<=粉丝\[)\d+(?=\])", 0))

        profile = response.css(".ut>a:nth-of-type(2)::attr(href)")
        user_item["user_id"] = int(profile.re(r"\d+")[0])
        yield scrapy.Request(url="https://weibo.cn" + profile.get(),
                             callback=self.parse_profile_function_generator(user_item))

    def parse_profile_function_generator(self, user_item: items.UserItem) -> Callable[
        [scrapy.http.Response], items.UserItem]:
        """
        用以处理个人资料页，需要带着个人微博页的信息
        """

        def parse_profile(response: scrapy.http.Response) -> items.UserItem:
            for profile in response.css(".c")[3].xpath("./text()"):
                key: str = profile.re_first(r'^.+(?=:|：)', "")
                value: str = profile.re_first(r'(?<=:|：).+$', "")
                if key == "" or key not in items.PROFILE_FIELD_CN_TO_EN:
                    continue
                user_item[items.PROFILE_FIELD_CN_TO_EN[key]] = value
            print("!!!!!!", user_item)

        return parse_profile

    def parse_weibo(self, response: scrapy.http.Response):
        """
        用以处理单条微博详情页
        """
        pass
