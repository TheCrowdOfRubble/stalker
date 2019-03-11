# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UserItem(scrapy.Item):
    user_id = scrapy.Field()
    nickname = scrapy.Field()
    username = scrapy.Field()
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


class WeiboItem(scrapy.Item):
    weibo_id = scrapy.Field()
    user_id = scrapy.Field()
    username = scrapy.Field()
    time = scrapy.Field()
    content = scrapy.Field()
    repost_amount = scrapy.Field()
    comment_amount = scrapy.Field()
    like_amount = scrapy.Field()


PROFILE_FIELD_CN_TO_EN = {
    "昵称": "nickname",
    "认证": "certification",
    "性别": "gender",
    "地区": "location",
    "生日": "birthday",
    "认证信息": "certification_information",
    "简介": "introduction",
    "性取向": "sexual_orientation",
    "感情状况": "relationship_status",
    "达人": "weibo_expert",
}
