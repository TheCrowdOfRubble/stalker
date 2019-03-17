# -*- coding: utf-8 -*-
import json
import time
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
        # print(response.url)
        # yield scrapy.Request(url="https://weibo.cn/repost/HljvrnYse", callback=self.parse_weibo_details)
        # yield scrapy.Request(url="https://weibo.cn/comment/HljvrnYse", callback=self.parse_weibo_details)
        # yield scrapy.Request(url="https://weibo.cn/attitude/HljvrnYse", callback=self.parse_weibo_details)
        # """
        # 获得个人资料
        print(response.url)
        yield self.parse_user_page(response)

        # 获得个人微博
        for weibo in self.parse_weiboes(response):
           yield weibo
        # """

    def parse_user_page(self, response: scrapy.http.Response):
        user_item = items.UserItem()
        user_item['create_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        user_item['modify_time'] = user_item['create_time']

        user_item["user_id"], user_item["username"] = utils.get_id_and_name(response.url)
        user_item["avatar"] = response.css(".u img::attr(src)").extract_first("")
        statistics = response.css(".tip2")
        user_item["weibo_amount"] = int(statistics.re_first(r"(?<=微博\[)\d+(?=\])", 0))
        user_item["follow_amount"] = int(statistics.re_first(r"(?<=关注\[)\d+(?=\])", 0))
        user_item["follower_amount"] = int(statistics.re_first(r"(?<=粉丝\[)\d+(?=\])", 0))

        profile = response.css(".ut>a:nth-of-type(2)::attr(href)")
        user_item["user_id"] = int(profile.re_first(r"\d+", 0))

        # 处理个人资料页
        return scrapy.Request(url="https://weibo.cn" + profile.get(), callback=self.parse_profile, meta={
            "user": user_item
        })

    def parse_profile(self, response: scrapy.http.Response):
        user_item = response.meta['user']
        for profile in response.css(".c")[3].xpath("./text()"):
            key: str = profile.re_first(r'^.+(?=:|：)', "")
            value: str = profile.re_first(r'(?<=:|：).+$', "")
            if key == "" or key not in items.PROFILE_FIELD_CN_TO_EN:
                continue
            response.meta['user'][items.PROFILE_FIELD_CN_TO_EN[key]] = value
        return user_item

    def parse_weiboes(self, response: scrapy.http.Response):
        """
        处理个人微博页的微博
        """
        for weibo in response.xpath('//div[@class="c"][@id]'):
            weibo_item = items.WeiboItem()
            weibo_item['create_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            weibo_item['modify_time'] = weibo_item['create_time']
            weibo_item["user_id"], weibo_item["username"] = utils.get_id_and_name(response.url)
            # weibo_item['user_id'] = response.meta['user']['user_id']
            # weibo_item['username'] = response.meta['user']['username']
            weibo_item['weibo_id'] = weibo.xpath('.//@id').re_first(r"(?<=M_).+")
            weibo_item['origin_weibo_id'] = weibo.xpath('./*/a[@class="cc"]/@href')\
                                                 .re(r"(?<=https://weibo.cn/comment/).+(?=\?)", "")

            additional = weibo.css('.ct::text')
            weibo_item['time'] = additional.re_first(r'.+(?=[\xA0])', '')
            weibo_item['platform'] = additional.re_first(r'(?<=来自).+', '')

            statistics = weibo.xpath('.//div[last()]/a/text()')
            weibo_item["repost_amount"] = int(statistics.re_first(r"(?<=赞\[)\d+(?=\])", 0))
            weibo_item["comment_amount"] = int(statistics.re_first(r"(?<=转发\[)\d+(?=\])", 0))
            weibo_item["like_amount"] = int(statistics.re_first(r"(?<=评论\[)\d+(?=\])", 0))

            if len(weibo_item['origin_weibo_id']) == 1:
                # 原创微博
                weibo_item['origin_weibo_id'] = ""
                if weibo.xpath("count(.//div)").get() == '1.0':
                    # 无图原创
                    weibo_item['content'] = weibo.css('div>div')\
                                                 .re_first(r'(?<=\<div\>).+(?=\<br\>)', "")\
                                                 .replace(u"\xA0", u"")
                else:
                    # 有图原创
                    weibo_item['content'] = weibo.xpath('./div[1]/node()').extract_first('').replace(u"\xA0", u"")
            else:
                # 转发微博
                weibo_item['origin_weibo_id'] = weibo_item['origin_weibo_id'][0]
                weibo_item['content'] = weibo.xpath('./div[last()]/node()[2]').extract_first('').replace(u"\xA0", u"")

            yield weibo_item

            yield scrapy.Request(url="https://weibo.cn/repost/" + weibo_item['weibo_id'],
                                 callback=self.parse_weibo_details)
            yield scrapy.Request(url="https://weibo.cn/comment/" + weibo_item['weibo_id'],
                                 callback=self.parse_weibo_details)
            yield scrapy.Request(url="https://weibo.cn/attitude/" + weibo_item['weibo_id'],
                                 callback=self.parse_weibo_details)

    def parse_weibo_details(self, response: scrapy.http.Response):
        """
        处理微博详情页，用以爬取更多用户
        """
        page_count = int(response.xpath("//div[@id='pagelist']/form/div/text()[2]").re_first(r'(?<=/).+(?=页)', 1))

        # for page in range(1, min(page_count, 10)):
        for page in range(1, 2):
            yield scrapy.Request(url=response.url + "?page=%d" % page, callback=self.get_more_users)

    def get_more_users(self, response: scrapy.http.Response):
        for elem in response.xpath("//div[@class='c'][preceding-sibling::div[@class='pms'] and following-sibling::div[@class='pa']]/a[1][not(contains(@href, '/comment/hot'))]/@href").getall():
            print("https://weibo.cn" + elem)
            yield scrapy.Request(url="https://weibo.cn" + elem)
