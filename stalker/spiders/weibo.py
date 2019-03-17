# -*- coding: utf-8 -*-
import json
from typing import List, Callable

import scrapy
import stalker.items as items
import stalker.utils as utils

RESERVED_WORD_IN_URL = [
    'repost',
    'attgroup',
    'pages',
    'comment',
    'mblog',
    'attitude',
    'addFav',
    'sinaurl',
    'fav',
    'account',
    'msg',
    'search',
    'topic',
    'spam',
    'at',
    's',
]


class WeiboSpider(scrapy.Spider):
    name: str = 'weibo'
    allowed_domains = ['weibo.cn']
    start_urls: List[str] = [
        'https://weibo.cn/rmrb',
    ]

    def parse(self, response: scrapy.http.Response) -> type(None):
        # 处理个人微博页
        user_item = self.parse_user_page(response)
        response.meta['user'] = user_item
        self.parse_weibo(response)

    def parse_user_page(self, response: scrapy.http.Response):
        """
        处理个人微博页
        """
        user_item = items.UserItem()

        if response.url.startswith("https://weibo.cn/u/"):
            user_item["user_id"] = int(response.url[19:])
        else:
            user_item["username"] = response.url[17:]
        user_item["avatar"] = response.css(".u img::attr(src)").extract_first("")
        statistics = response.css(".tip2")
        user_item["weibo_amount"] = int(statistics.re_first(r"(?<=微博\[)\d+(?=\])", 0))
        user_item["follow_amount"] = int(statistics.re_first(r"(?<=关注\[)\d+(?=\])", 0))
        user_item["follower_amount"] = int(statistics.re_first(r"(?<=粉丝\[)\d+(?=\])", 0))

        profile = response.css(".ut>a:nth-of-type(2)::attr(href)")
        user_item["user_id"] = int(profile.re_first(r"\d+", 0))

        # 处理个人资料页
        response.meta['user'] = user_item
        scrapy.Request(url="https://weibo.cn" + profile.get(), callback=self.parse_profile)

        return user_item

    def parse_profile(self, response: scrapy.http.Response) -> items.UserItem:
        user_item = response.meta['user']
        for profile in response.css(".c")[3].xpath("./text()"):
            key: str = profile.re_first(r'^.+(?=:|：)', "")
            value: str = profile.re_first(r'(?<=:|：).+$', "")
            if key == "" or key not in items.PROFILE_FIELD_CN_TO_EN:
                continue
            user_item[items.PROFILE_FIELD_CN_TO_EN[key]] = value
            return user_item

    def parse_weibo(self, response: scrapy.http.Response):
        for weibo in response.xpath('//div[@class="c"][@id]'):
            weibo_item = items.WeiboItem()
            weibo_item['user_id'] = response.meta['user']['user_id']
            weibo_item['username'] = response.meta['user']['username']
            weibo_item['weibo_id'] = weibo.xpath('.//@id').re_first(r"(?<=M_).+")
            weibo_item['origin_weibo_id'] = weibo.xpath('./*/a[@class="cc"]/@href').re(
                r"(?<=https://weibo.cn/comment/).+(?=\?)", "")

            statistics = weibo.xpath('.//div[last()]/a/text()')
            weibo_item["repost_amount"] = int(statistics.re_first(r"(?<=赞\[)\d+(?=\])", 0))
            weibo_item["comment_amount"] = int(statistics.re_first(r"(?<=转发\[)\d+(?=\])", 0))
            weibo_item["like_amount"] = int(statistics.re_first(r"(?<=评论\[)\d+(?=\])", 0))

            if len(weibo_item['origin_weibo_id']) == 1:
                # 原创微博
                weibo_item['origin_weibo_id'] = ""
                if weibo.xpath("count(.//div)").get() == '1.0':
                    # 无图原创
                    weibo_item['content'] = weibo.css('div>div').re_first(r'(?<=\<div\>).+(?=\<br\>)', "")
                else:
                    # 有图原创
                    weibo_item['content'] = weibo_item['content'] = weibo.css('div>div').re_first(
                        r'(?<=\<div\>).+(?=\<br\>)', "")
            else:
                # 转发微博
                weibo_item['origin_weibo_id'] = weibo_item['origin_weibo_id'][0]
                weibo_item['content'] = weibo.xpath('./div[last()]/node()[2]').extract_first('')

            yield weibo_item
