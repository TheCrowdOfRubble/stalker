# -*- coding: utf-8 -*-
import logging
from typing import Union

from scrapy.http import Request, Response
from scrapy_redis.spiders import RedisSpider

import stalker.items as items
import stalker.parse.user as userparser
import stalker.parse.weibo as weiboparser
import utils


class ZhuangdingSpider(RedisSpider, userparser.User, weiboparser.Weibo):
    name = 'zhuangding'
    allowed_domains = ['weibo.cn']
    custom_settings = {
        "SCHEDULER": "scrapy_redis.scheduler.Scheduler",
        "DUPEFILTER_CLASS": "scrapy_redis.dupefilter.RFPDupeFilter"
    }

    def __init__(self, **kwargs):
        super(RedisSpider, self).__init__(**kwargs)
        super(userparser.User, self).__init__()
        super(weiboparser.Weibo, self).__init__()

    def parse(self, response: Response) -> Union[type(None), items.UserItem, items.WeiboItem, Request]:
        user_profile_page_url = response.css('a[href$="/info"]::attr(href)').get()
        # 该用户不存在，如 https://weibo.cn/u/3 ，或该用户被封禁，如 https://weibo.cn/u/2803301711 ,或是自己的用户
        if not user_profile_page_url or response.url == 'https://weibo.cn/':
            logging.info('NO USER %s', response.url)
            return None

        # 获取基本 user_item
        user_item = self.get_base_user_item(response)

        # 补全 user_item
        # yield Request(
        #     url='https://weibo.cn/%d/info' % user_item['user_id'],
        #     callback=self.get_full_user_item,
        #     meta={'user_item': user_item},
        #     priority=100,  # 优先采集用户
        # )

        # 获取粉丝们
        # yield Request(
        #     url='https://weibo.cn/%d/fans' % user_item['user_id'],
        #     callback=self.get_all_fans,
        #     priority=90,  # 优先采集用户
        # )

        # 只有从消息队列中取出的任务才抓取微博，其他的都不抓，比如从微博详情页抓的新用户（默认是抓的，除非显示说明不抓）
        if response.meta.get('dont_fetch_weibo'):
            return None

        # 获取微博们
        response.meta['user_item'] = user_item
        response.meta['min_time'], response.meta['max_time'] = utils.get_an_hour_period()  # 发表时间 [min, max)
        for rtn in self.get_all_weiboes(response):
            yield rtn
