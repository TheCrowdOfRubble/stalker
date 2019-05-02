# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import scrapy.utils.datatypes
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Compose
import stalker.items.processors as processors


class BaseItem(scrapy.Item):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if args or kwargs:
            return
        for keys in self.fields:
            self[keys] = ''


class UserItem(BaseItem):
    user_id = scrapy.Field()
    nickname = scrapy.Field()
    username = scrapy.Field()
    avatar = scrapy.Field()
    weibo_amount = scrapy.Field()  # 微博数
    follow_amount = scrapy.Field()  # 关注数
    follower_amount = scrapy.Field()  # 粉丝数
    gender = scrapy.Field()
    introduction = scrapy.Field()
    birthday = scrapy.Field()
    certification = scrapy.Field()  # 微博认证
    certification_information = scrapy.Field()  # 微博认证信息
    location = scrapy.Field()
    weibo_expert = scrapy.Field()  # 微博达人
    sexual_orientation = scrapy.Field()
    relationship_status = scrapy.Field()  # 感情状况


class WeiboItem(BaseItem):
    weibo_id = scrapy.Field()
    user_id = scrapy.Field()
    time = scrapy.Field()
    content = scrapy.Field()
    repost_amount = scrapy.Field()
    comment_amount = scrapy.Field()
    like_amount = scrapy.Field()
    origin_weibo_id = scrapy.Field()
    platform = scrapy.Field()


class UserLoader(ItemLoader):
    default_item_class = UserItem
    default_output_processor = TakeFirst()

    user_id_in = Compose(TakeFirst(), processors.get_first_number)
    username_in = Compose(TakeFirst(), processors.get_username_from_user_detail_page_url)
    weibo_amount_in = Compose(TakeFirst(), processors.get_first_number)
    follow_amount_in = Compose(TakeFirst(), processors.get_first_number)
    follower_amount_in = Compose(TakeFirst(), processors.get_first_number)


class WeiboLoader(ItemLoader):
    default_item_class = WeiboItem
    default_output_processor = TakeFirst()

    weibo_id_in = Compose(TakeFirst(), lambda div_id: div_id[2:])  # div.id == 'M_Hsa2x7GED' -> 'Hsa2x7GED'
    time_in = Compose(TakeFirst(), processors.parse_weibo_time)
    like_amount_in = Compose(TakeFirst(), processors.get_first_number)
    repost_amount_in = Compose(TakeFirst(), processors.get_first_number)
    comment_amount_in = Compose(TakeFirst(), processors.get_first_number)
    # origin_weibo_id_in = Compose(TakeFirst())
