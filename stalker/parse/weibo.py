import urllib.parse as urlparser
from typing import Union, Iterator, List

from scrapy.http import Response, Request
from scrapy.loader.processors import TakeFirst
from scrapy.selector import Selector

import stalker.items as items
from stalker.items.processors import get_weibo_content
from stalker.parse import FetchItemsAndNext
from stalker.parse.user import FetchUsersAndNext


class Weibo:
    def get_all_weiboes(self, response):
        user_item = response.meta.get('user_item')
        max_time = response.meta.get('max_time')
        min_time = response.meta.get('min_time')

        def fetch_all_weiboes(res: Response) -> List[str]:
            return res.xpath('//div[@class="c"][contains(@id, "M_")]')

        def parse_single_weibo(weibo: Selector) -> Iterator[Union[items.WeiboItem, bool]]:
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

            # 从微博详情页抓取更多用户
            # if weibo_item["repost_amount"] > 0:
            #     yield Request(
            #         url="https://weibo.cn/repost/" + weibo_item['weibo_id'],
            #         callback=self.get_all_interactor,
            #         meta={'random': True}
            #     )
            # if weibo_item["comment_amount"] > 0:
            #     yield Request(
            #         url="https://weibo.cn/comment/" + weibo_item['weibo_id'],
            #         callback=self.get_all_interactor,
            #         meta={'random': True}
            #     )
            # if weibo_item["like_amount"] > 0:
            #     yield Request(
            #         url="https://weibo.cn/attitude/" + weibo_item['weibo_id'],
            #         callback=self.get_all_interactor,
            #         meta={'random': True}
            #     )

            is_pinned = weibo_loader.get_css('.kt', TakeFirst())  # 置顶微博
            if min_time <= weibo_item['time'] < max_time:  # [min, max)
                yield weibo_item
                yield True
            elif is_pinned:  # 是置顶微博，继续
                yield True
            elif min_time <= weibo_item['time']:  # 比最早时间晚，继续
                yield True
            else:  # 既不在时间范围内，也不是置顶微博，还比最早时间早
                yield False

        for rtn in FetchItemsAndNext(
                fetch_all_weiboes,
                parse_single_weibo,
                self.get_all_weiboes,
                response.meta
        )(response):
            yield rtn

    def get_all_interactor(self, response):
        def fetch_all_interactor(res: Response) -> List[str]:
            url_parts = res.xpath(
                "//div[@class='c'][preceding-sibling::div[@class='pms'] and following-sibling::div[@class='pa']]/a[1]["
                "not(contains(@href, '/repost/hot') or contains(@href, '/comment/hot'))]/@href"
            ).getall()
            return list(map(
                lambda url_part: urlparser.urljoin('https://weibo.cn', url_part),
                url_parts
            ))

        for rtn in FetchUsersAndNext(fetch_all_interactor, self.get_all_interactor)(response):
            yield rtn
