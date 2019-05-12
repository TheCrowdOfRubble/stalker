from typing import Union, Iterator, Callable, List, Tuple, Any
import logging

from scrapy.http import Request, Response
from scrapy.loader.processors import MapCompose, TakeFirst

from stalker.items.processors import remove_invisible_character, get_dict_from_profile, EmptyTo
from stalker.parse import FetchItemsAndNext
import stalker.items as items
import utils


class FetchUsersAndNext(FetchItemsAndNext):
    def __init__(self, fetch_all: Callable[[Response], List], callback: Callable[[Response], Any]):
        def fetch_single_user(url: str) -> Iterator[Union[Request, bool]]:
            yield Request(url=url, meta={'dont_fetch_weibo': True})
            yield True

        super().__init__(fetch_all, fetch_single_user, callback)


class User:
    @staticmethod
    def get_base_user_item(response: Response) -> items.UserItem:
        user_loader = items.UserLoader(response=response)

        user_loader.add_css('user_id', 'a[href$="/info"]::attr(href)')
        user_loader.add_xpath('weibo_amount', '//div[@class="tip2"]/span/text()')
        user_loader.add_xpath('follow_amount', '//div[@class="tip2"]/a[1]/text()')
        user_loader.add_xpath('follower_amount', '//div[@class="tip2"]/a[2]/text()')

        return user_loader.load_item()  # 并不全的用户资料

    def get_full_user_item(self, response: Response) -> items.UserItem:
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

    def get_all_fans(self, response: Response) -> Iterator[Request]:
        def fetch_all_fans(res: Response) -> List[str]:
            return res.xpath('//div[@class="c"]/table/tr/td[2]/a[1]/@href').getall()

        for rtn in FetchUsersAndNext(fetch_all_fans, self.get_all_fans)(response):
            yield rtn
