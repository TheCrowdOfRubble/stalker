# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
import re

from twisted.enterprise import adbapi

import stalker.items as items

dbpool = adbapi.ConnectionPool('MySQLdb', host='127.0.0.1', database='The_Crowd_of_Rubble', user='root',
                               password='rootroot', charset='utf8mb4', cp_min=1, cp_max=1, use_unicode=True)

second_pattern = re.compile(r'\d+(?=秒前)')
minute_pattern = re.compile(r'\d+(?=分钟前)')
today_pattern = re.compile(r'今天 (\d+):(\d+)')
yesterday_pattern = re.compile(r'昨天 (\d+):(\d+)')
year_pattern = re.compile(r'(\d+)月(\d+)日 (\d+):(\d+)')


def get_time_from_second_pattern(matched):
    now = datetime.datetime.now()
    second = int(matched.group(0))
    delta = datetime.timedelta(seconds=second)
    return (now - delta).strftime("%Y-%m-%d %H:%M:%S")


def get_time_from_minute_pattern(matched):
    now = datetime.datetime.now()
    minute = int(matched.group(0))
    delta = datetime.timedelta(minutes=minute)
    return (now - delta).strftime("%Y-%m-%d %H:%M:%S")


today = datetime.date.today().strftime("%Y-%m-%d %%s:%%s:00")
yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d %%s:%%s:00")
this_year = datetime.date.today().strftime("%Y-%%s-%%s %%s:%%s:00")


def get_time_from_today_pattern(matched):
    return today % (matched.group(0), matched.group(1))


def get_time_from_yesterday_pattern(matched):
    return yesterday % (matched.group(0), matched.group(1))


def get_time_from_year_pattern(matched):
    return this_year % (matched.group(0), matched.group(1), matched.group(2), matched.group(3))


patterns = {
    second_pattern: get_time_from_second_pattern,
    minute_pattern: get_time_from_minute_pattern,
    today_pattern: get_time_from_today_pattern,
    yesterday_pattern: get_time_from_yesterday_pattern,
    year_pattern: get_time_from_year_pattern,
}

keys = ""
values = ""
for field_name in items.WeiboItem.fields:
    keys += "`%s`," % field_name
    values += "%s,"
weibo_insert_sql = "INSERT INTO `weiboes` (%s) VALUES (%s)" % (keys[:-1], values[:-1])
for field_name in items.UserItem.fields:
    keys += "`%s`," % field_name
    values += "%s,"
user_insert_sql = "INSERT INTO `users` (%s) VALUES (%s)" % (keys[:-1], values[:-1])


class PersistencePipeline():
    def process_item(self, item, spider):
        if isinstance(item, items.UserItem):
            self.process_user_item(item)
        else:
            self.process_weibo_item(item)

    def process_user_item(self, item):
        dbpool.runInteraction(self.insert_user, item)

    def process_weibo_item(self, item):
        # dbpool.runInteraction(self.insert_weibo, item)
        item['time'] = self.get_time(item['time'])
        exit()

    @staticmethod
    def insert_user(tx, item):
        tx.execute(user_insert_sql, tuple(dict(item).values()))  # 业已转义

    @staticmethod
    def insert_weibo(tx, item):
        tx.execute(weibo_insert_sql, tuple(dict(item).values()))  # 业已转义

    @staticmethod
    def get_time(time):
        for pattern, function in patterns:
            matched = pattern.match(time)
            if time:
                return function(matched)
        return time

# TODO: 整理为了加速设置的全局变量到 utils 包下
