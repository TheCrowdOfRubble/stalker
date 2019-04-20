# -*- coding: utf-8 -*-
import time

import scrapy

import stalker.items as items
import stalker.utils as utils
import stalker.utils.weibo_datetime_parser as weibo_datetime_parser


class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['weibo.cn']
    start_urls = [
        'https://weibo.cn/rmrb',
    ]

    def parse(self, response):
        print(response.url)

        # 获得个人资料
        yield self.parse_user_page(response)

        # 获得个人微博
        for weibo in self.parse_weiboes(response):
            yield weibo

    def parse_user_page(self, response):
        user_item = items.UserItem()
        user_item.set_all()

        user_item['modify_time'] = user_item['create_time'] = utils.get_datetime("%Y-%m-%d %H:%M:%S")

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

    @staticmethod
    def parse_profile(response):
        user_item = response.meta['user']
        for profile in response.css(".c")[3].xpath("./text()"):
            key = profile.re_first(r'^.+(?=:|：)', "")
            value = profile.re_first(r'(?<=:|：).+$', "")
            if key == "" or key not in items.PROFILE_FIELD_CN_TO_EN:
                continue
            response.meta['user'][items.PROFILE_FIELD_CN_TO_EN[key]] = value
        return user_item

    def parse_weiboes(self, response):
        """
        处理个人微博页的微博
        """
        for weibo in response.xpath('//div[@class="c"][@id]'):
            weibo_item = items.WeiboItem()
            weibo_item['create_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            weibo_item['modify_time'] = weibo_item['create_time']
            weibo_item["user_id"], weibo_item["username"] = utils.get_id_and_name(response.url)
            weibo_item['weibo_id'] = weibo.xpath('.//@id').re_first(r"(?<=M_).+")
            weibo_item['origin_weibo_id'] = weibo.xpath('./*/a[@class="cc"]/@href') \
                .re(r"(?<=https://weibo.cn/comment/).+(?=\?)", "")

            additional = weibo.css('.ct::text')
            weibo_item['time'] = weibo_datetime_parser.parse(additional.re_first(r'.+(?=[\xA0])', ''))
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
                    weibo_item['content'] = weibo.css('div>div') \
                        .re_first(r'(?<=\<div\>).+(?=\<br\>)', "") \
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

    def parse_weibo_details(self, response):
        """
        处理微博详情页，用以爬取更多用户
        """
        self.get_more_users(response)  # 处理第一页

        page_count = int(response.xpath("//div[@id='pagelist']/form/div/text()[2]").re_first(r'(?<=/).+(?=页)', 1))
        for page in range(2, min(page_count, 3)):  # 从第二页开始
            yield scrapy.Request(url=response.url + "?page=%d" % page, callback=self.get_more_users)

    @staticmethod
    def get_more_users(response):
        users = response.xpath("//div[@class='c'][preceding-sibling::div[@class='pms'] and following-sibling::div[@class='pa']]/a[1][not(contains(@href, '/repost/hot') or contains(@href, '/comment/hot'))]/@href").getall()
        for elem in users:
            yield scrapy.Request(url="https://weibo.cn" + elem)
