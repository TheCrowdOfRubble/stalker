# -*- coding: utf-8 -*-
import typing
import urllib.parse as urlparser
import logging

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Compose, SelectJmes
import scrapy_redis.spiders

import utils
import stalker.items as items
from stalker.items.processors import get_dict_from_profile, remove_invisible_character, get_weibo_content, EmptyTo
import stalker.settings as settings
import parser


class ZhuangdingSpider(scrapy_redis.spiders.RedisSpider):
    name = 'zhuangding'
    allowed_domains = ['weibo.cn']
    redis_key = 'stalker:start_urls'

    def parse(self, response: scrapy.http.Response):
        user_loader = items.UserLoader(response=response)

        user_profile_url = user_loader.get_css('a[href$="/info"]::attr(href)', TakeFirst())
        if not user_profile_url or response.url == 'https://weibo.cn/':
            logging.info('NO USER %s', response.url)
            return

        user_loader.add_value('user_id', user_profile_url)
        user_loader.add_xpath('weibo_amount', '//div[@class="tip2"]/span/text()')
        user_loader.add_xpath('follow_amount', '//div[@class="tip2"]/a[1]/text()')
        user_loader.add_xpath('follower_amount', '//div[@class="tip2"]/a[2]/text()')

        user_item = user_loader.load_item()
        response.meta['user_item'] = user_item

        yield scrapy.Request(
            url=response.urljoin(user_profile_url),
            callback=self.parse_profile,
            meta={'user_item': user_item},
            priority=100,  # 优先采集用户
        )

        response.meta['user_item'] = user_item
        response.meta['min_time'] = utils.get_datetime("%Y-%m-%d %H:00:00")
        response.meta['max_page'] = min(parser.get_page_amount(response), settings.MAX_PAGE_VISIT)
        for weibo_item in self.parse_weiboes(response):
            yield weibo_item

    def parse_profile(self, response: scrapy.http.Response) -> items.UserItem:
        # 不准搞成 @staticmethod 否则 Scrapy-Redis 不认
        user_item: items.UserItem = response.meta.get('user_item')
        user_loader = items.UserLoader(item=user_item, response=response)

        user_loader.add_xpath('avatar', '//img[@alt="头像"]/@src')

        key_value_pairs_in_profile = user_loader.get_xpath(
            '//div[@class="c"]/text()',
            MapCompose(remove_invisible_character, get_dict_from_profile)
        )

        for key_value_pair in key_value_pairs_in_profile:
            key = TakeFirst()(key_value_pair)
            user_loader.add_value(key, key_value_pair[key])

        user_item = user_loader.load_item()
        user_item['username'] = EmptyTo(None)(user_item['username'])  # 即使我加在输出处理器上，仍然不行，只好这么办了
        return user_item

    def parse_weiboes(self, response: scrapy.http.Response) -> typing.Iterator[items.WeiboItem]:
        user_item = response.meta.get('user_item')
        min_time = response.meta.get('min_time')

        beyond = not bool(min_time)  # 未设置 oldest_weibo_datetime 字段就直接设为 True
        for weibo in response.xpath('//div[@class="c"][contains(@id, "M_")]'):
            weibo_loader = items.WeiboLoader(selector=weibo)

            weibo_loader.add_value('user_id', user_item['user_id'])

            weibo_loader.add_xpath('weibo_id', './@id')

            weibo_loader.add_xpath('time', './div[last()]/span[@class="ct"]/text()')

            weibo_loader.add_xpath('like_amount', './div[last()]/a[last()-3]/text()')
            weibo_loader.add_xpath('repost_amount', './div[last()]/a[last()-2]/text()')
            weibo_loader.add_xpath('comment_amount', './div[last()]/a[last()-1]/text()')

            weibo_loader.add_xpath(
                'origin_weibo_id',
                './*/a[@class="cc"]/@href',
                re=r'(?<=https://weibo.cn/comment/).+(?=\?)'
            )

            weibo_loader.add_value('content', get_weibo_content(weibo_loader))

            weibo_loader.add_xpath('platform', './div[last()]/span[@class="ct"]/text()', re=r'(?<=来自).+')

            weibo_item = weibo_loader.load_item()
            yield weibo_item

            if beyond or weibo_item['time'] < min_time:
                beyond = True

            # 爬取微博详情页，抓取更多用户
            for new_request in self._get_more_user(weibo_item):
                yield new_request

        # 爬取更多页面
        if not beyond:
            new_request = self._read_more_page(response)
            if new_request:
                yield new_request

    def _get_more_user(self, weibo_item: items.WeiboItem):
        if weibo_item["repost_amount"] > 0:
            yield scrapy.Request(
                url="https://weibo.cn/repost/" + weibo_item['weibo_id'],
                callback=self._parse_weibo_details,
                meta={'random': True}
            )
        if weibo_item["comment_amount"] > 0:
            yield scrapy.Request(
                url="https://weibo.cn/comment/" + weibo_item['weibo_id'],
                callback=self._parse_weibo_details,
                meta={'random': True}
            )
        if weibo_item["like_amount"] > 0:
            yield scrapy.Request(
                url="https://weibo.cn/attitude/" + weibo_item['weibo_id'],
                callback=self._parse_weibo_details,
                meta={'random': True}
            )

    def _read_more_page(self, response: scrapy.http.Response):
        max_page = response.meta.get('max_page')
        url_components: urlparser.ParseResult = urlparser.urlparse(response.url)
        query = dict(urlparser.parse_qsl(url_components.query, keep_blank_values=True))
        if 'page' in query:
            page_id = Compose(SelectJmes('page'), int)(query)
            if page_id < 1:
                page_id = 1
            if page_id <= settings.MAX_PAGE_VISIT:
                page_id += 1
        else:
            page_id = 2

        if page_id > max_page:
            return None

        query['page'] = page_id
        url_components = urlparser.ParseResult(
            scheme=url_components.scheme,
            netloc=url_components.netloc,
            path=url_components.path,
            params=None,
            query=urlparser.urlencode(query),
            fragment=None
        )
        next_page_url = urlparser.urlunparse(url_components)

        return scrapy.Request(
            url=next_page_url,
            callback=self.parse_weiboes,
            meta=response.meta,
        )

    def _parse_weibo_details(self, response):
        self._get_more_users(response)  # 处理第一页

        page_count = parser.get_page_amount(response)
        for page in range(2, min(page_count, settings.MAX_PAGE_VISIT)):  # 从第二页开始
            yield scrapy.Request(url=urlparser.urljoin(response.url, "?page=%d" % page), callback=self._get_more_users)

    def _get_more_users(self, response):
        users = response.xpath(
            "//div[@class='c'][preceding-sibling::div[@class='pms'] and following-sibling::div[@class='pa']]/a[1]["
            "not(contains(@href, '/repost/hot') or contains(@href, '/comment/hot'))]/@href"
        ).getall()
        for elem in users:
            yield scrapy.Request(url=urlparser.urljoin("https://weibo.cn", elem), priority=90)  # 用户优先处理
