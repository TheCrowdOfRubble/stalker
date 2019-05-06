# -*- coding: utf-8 -*-
from typing import Union, Iterator
import urllib.parse as urlparser
import logging

import scrapy_redis.spiders
from scrapy.http import Request, Response
from scrapy.loader.processors import MapCompose, TakeFirst

from stalker.items.processors import get_dict_from_profile, remove_invisible_character, EmptyTo, get_weibo_content
import parser
import stalker.items as items
import stalker.settings as settings
import utils


class ZhuangdingSpider(scrapy_redis.spiders.RedisSpider):
    name = 'zhuangding2'
    allowed_domains = ['weibo.cn']
    redis_key = 'stalker:start_urls'

    def parse(self, response: Response) -> Union[Iterator[Request], Iterator[items.WeiboItem], type(None)]:
        """
        解析用户详情页，产生 user_item 的一部分 https://weibo.cn/rmrb
        """
        user_loader = items.UserLoader(response=response)

        user_profile_url = user_loader.get_css('a[href$="/info"]::attr(href)', TakeFirst())

        # 该用户不存在，如 https://weibo.cn/u/3 ，或该用户被封禁，如 https://weibo.cn/u/2803301711 ,或是自己的用户
        if not user_profile_url or response.url == 'https://weibo.cn/' and not utils.is_my_account(response):
            logging.info('NO USER %s', response.url)
            return None

        user_loader.add_value('user_id', user_profile_url)
        user_loader.add_xpath('weibo_amount', '//div[@class="tip2"]/span/text()')
        user_loader.add_xpath('follow_amount', '//div[@class="tip2"]/a[1]/text()')
        user_loader.add_xpath('follower_amount', '//div[@class="tip2"]/a[2]/text()')

        user_item = user_loader.load_item()  # 并不全的用户资料

        # 爬取用户资料页
        yield Request(
            url='https://weibo.cn/%d/info' % user_item['user_id'],
            callback=self.parse_profile,
            meta={'user_item': user_item},
            priority=100,  # 优先采集用户
        )

        yield Request(
            url='https://weibo.cn/%d/info' % user_item['user_id'],
            callback=self.parse_profile,
            meta={'user_item': user_item},
            priority=99,  # 优先采集用户
        )

        # 只有从消息队列中取出的任务才抓取微博，其他的都不抓，比如从微博详情页抓的新用户（默认是抓的，除非显示说明不抓）
        if response.meta.get('dont_fetch_weibo'):
            return None

        response.meta['user_item'] = user_item
        response.meta['min_time'], response.meta['max_time'] = utils.get_an_hour_period()  # 抓取的最大、小发表时间 [小, 大)
        response.meta['max_page'] = utils.get_page_amount(response)  # 最大翻页数
        for weibo_item in self.parse_weiboes(response):
            yield weibo_item

    def parse_profile(self, response: Response) -> items.UserItem:
        """
        解析用户资料页，补全 user_item https://weibo.cn/3282669464/info
        不准搞成 @staticmethod，否则 Scrapy-Redis 不认
        """
        user_item: items.UserItem = response.meta.get('user_item')
        user_loader = items.UserLoader(item=user_item, response=response)

        user_loader.add_xpath('avatar', '//img[@alt="头像"]/@src')

        # 将资料页处理成 kv 格式
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

    def parse_weiboes(self, response: Response) -> Iterator[items.WeiboItem]:
        """
        解析用户详情页，抓取本页微博，并且可能继续翻页 https://weibo.cn/u/3282669464 https://weibo.cn/u/3282669464?page=2
        """
        user_item = response.meta.get('user_item')
        max_time = response.meta.get('max_time')
        min_time = response.meta.get('min_time')

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

            # 从微博详情页抓取更多用户
            if weibo_item["repost_amount"] > 0:
                yield Request(
                    url="https://weibo.cn/repost/" + weibo_item['weibo_id'],
                    callback=self.get_more_user_from_weibo_detail_page,
                    meta={'random': True}
                )
            if weibo_item["comment_amount"] > 0:
                yield Request(
                    url="https://weibo.cn/comment/" + weibo_item['weibo_id'],
                    callback=self.get_more_user_from_weibo_detail_page,
                    meta={'random': True}
                )
            if weibo_item["like_amount"] > 0:
                yield Request(
                    url="https://weibo.cn/attitude/" + weibo_item['weibo_id'],
                    callback=self.get_more_user_from_weibo_detail_page,
                    meta={'random': True}
                )

            # 抓到的微博不属于 [min, max)，停止，进入 else 分支
            if not min_time <= weibo_item['time'] < max_time:
                break
        else:  # 爬取更多用户微博页
            new_user_weibo_page_request = self.read_more_user_weibo_page(response)
            if new_user_weibo_page_request:
                yield new_user_weibo_page_request

    def get_more_user_from_weibo_detail_page(self, response):
        self.get_more_user_urls(response)  # 处理第一页

        page_count = utils.get_page_amount(response)
        for page in range(2, min(page_count, settings.MAX_PAGE_VISIT)):  # 从第二页开始
            yield Request(
                url=utils.move_to_next_page(response.url, page),
                callback=self.get_more_user_urls,
            )

    def get_more_user_urls(self, response):
        user_urls = response.xpath(
            "//div[@class='c'][preceding-sibling::div[@class='pms'] and following-sibling::div[@class='pa']]/a[1]["
            "not(contains(@href, '/repost/hot') or contains(@href, '/comment/hot'))]/@href"
        ).getall()
        print(user_urls)
        for url in user_urls:
            yield Request(
                url=urlparser.urljoin("https://weibo.cn", url),
                # meta={'dont_fetch_weibo': True},
                priority=90,  # 用户优先处理
            )

    def read_more_user_weibo_page(self, response: Response) -> Union[Request, type(None)]:
        """
        翻更多的用户微博页
        """
        page_id, next_page_url = utils.move_to_next_page(response.url)
        if page_id > int(response.meta.get('max_page')):
            return None

        return Request(
            url=next_page_url,
            callback=self.parse_weiboes,
            meta=response.meta,
        )

    def get_more_users_from_fans(self, response: Response):
        user_urls = response.xpath('//div[@class="c"]/table/tbody/tr/td[2]/a[1]/@href').getall()
        for url in user_urls:
            yield Request(
                url=urlparser.urljoin("https://weibo.cn", url),
                # meta={'dont_fetch_weibo': True},
                priority=90,  # 用户优先处理
            )
