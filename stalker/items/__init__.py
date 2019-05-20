# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
from datetime import datetime

import scrapy.utils.datatypes
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Compose, Identity, MapCompose, SelectJmes
from scrapy.linkextractors import LinkExtractor
from dateutil import parser

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

    tags = scrapy.Field()  # 不会存到数据库中去


class UserLoader(ItemLoader):
    default_item_class = UserItem
    default_output_processor = TakeFirst()

    user_id_in = Compose(TakeFirst(), processors.get_first_number)
    user_id_out = Compose(TakeFirst(), int)

    username_in = Compose(TakeFirst(), processors.get_username_from_user_detail_page_url)

    weibo_amount_in = Compose(TakeFirst(), processors.get_first_number)
    weibo_amount_out = Compose(TakeFirst(), int)

    follow_amount_in = Compose(TakeFirst(), processors.get_first_number)
    follow_amount_out = Compose(TakeFirst(), int)

    follower_amount_in = Compose(TakeFirst(), processors.get_first_number)
    follower_amount_out = Compose(TakeFirst(), int)


class WeiboLoader(ItemLoader):
    default_item_class = WeiboItem
    default_output_processor = TakeFirst()

    weibo_id_in = Compose(TakeFirst(), lambda div_id: div_id[2:])  # div.id == 'M_Hsa2x7GED' -> 'Hsa2x7GED'

    time_in = Compose(TakeFirst(), processors.parse_weibo_time)

    like_amount_in = Compose(TakeFirst(), processors.get_first_number)
    like_amount_out = Compose(TakeFirst(), int)

    repost_amount_in = Compose(TakeFirst(), processors.get_first_number)
    repost_amount_out = Compose(TakeFirst(), int)

    comment_amount_in = Compose(TakeFirst(), processors.get_first_number)
    comment_amount_out = Compose(TakeFirst(), int)


class BaseJsonLoader(ItemLoader):
    default_item_class = BaseItem
    default_output_processor = TakeFirst()

    FIELD_MAPPING = {}

    def __init__(self, obj: dict):
        super().__init__()

        for json_key in obj:
            if json_key not in self.FIELD_MAPPING:
                continue
            db_key = self.FIELD_MAPPING[json_key]
            self.add_value(db_key, obj[json_key])


class UserJsonLoader(BaseJsonLoader):
    default_item_class = UserItem
    FIELD_MAPPING = {
        'id': 'user_id',
        'screen_name': 'nickname',
        'avatar_hd': 'avatar',
        'statuses_count': 'weibo_amount',
        'follow_count': 'follow_amount',
        'followers_count': 'follower_amount',
        'gender': 'gender',
        'description': 'certification_information',
        'verified_reason': 'certification_information',
    }

    # gender_in = Compose(lambda gender: '女' if gender == 'f' else '男')
    gender_in = Compose(TakeFirst(), lambda gender: '女' if gender == 'f' else '男')


def _get_tags(text):
    pass


class WeiboJsonLoader(BaseJsonLoader):
    default_item_class = WeiboItem
    FIELD_MAPPING = {
        'bid': 'weibo_id',
        'user': 'user_id',
        'created_at': 'time',
        'raw_text': 'content',
        'reposts_count': 'repost_amount',
        'comments_count': 'comment_amount',
        'attitudes_count': 'like_amount',
        'retweeted_status': 'origin_weibo_id',
        'text': 'tags',
    }

    user_id_in = Compose(TakeFirst(), SelectJmes('id'))

    origin_weibo_id_in = Compose(TakeFirst(), SelectJmes('bid'))

    time_in = Compose(TakeFirst(), parser.parse, lambda date: datetime.strftime(date, '%Y-%m-%d %H:%M:%S'))

    tags_in = Compose(TakeFirst(), processors.tags_extractor)
    tags_out = Identity()