# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from twisted.enterprise import adbapi

import stalker.items as items


class PersistencePipeline:
    @classmethod
    def from_crawler(cls, crawler):
        db_params = dict(
            db=crawler.settings.get('DB_NAME'),
            host=crawler.settings.get('DB_HOST'),
            port=crawler.settings.get('DB_PORT'),
            user=crawler.settings.get('DB_USER'),
            passwd=crawler.settings.get('DB_PASSWORD'),
            charset=crawler.settings.get('DB_CHARSET'),
            cp_min=crawler.settings.get('DB_MIN_POOL_SIZE'),
            cp_max=crawler.settings.get('DB_MAX_POOL_SIZE'),
            use_unicode=crawler.settings.get('DB_USE_UNICODE'),
        )
        return cls(db_params, crawler.settings.get('WEIBO_INSERT_SQL'), crawler.settings.get('USER_INSERT_SQL'))

    def __init__(self, db_params, weibo_insert_sql, user_insert_sql):
        self.db_pool = adbapi.ConnectionPool("MySQLdb", **db_params)
        self.weibo_insert_sql = weibo_insert_sql
        self.user_insert_sql = user_insert_sql

    def process_item(self, item, spider):
        if isinstance(item, items.UserItem):
            self._process_user_item(item)
        else:
            self._process_weibo_item(item)

    def _process_user_item(self, user_item):
        self.db_pool.runInteraction(self._insert_item(self.user_insert_sql), (
            user_item["user_id"],
            user_item["nickname"],
            user_item["username"],
            user_item["avatar"],
            user_item["weibo_amount"],
            user_item["follow_amount"],
            user_item["follower_amount"],
            user_item["gender"],
            user_item["introduction"],
            user_item["birthday"],
            user_item["certification"],
            user_item["certification_information"],
            user_item["location"],
            user_item["weibo_expert"],
            user_item["sexual_orientation"],
            user_item["relationship_status"],
            user_item["create_time"],
            user_item["modify_time"],
        ))

    def _process_weibo_item(self, weibo_item):
        self.db_pool.runInteraction(self._insert_item(self.weibo_insert_sql), (
            weibo_item["weibo_id"],
            weibo_item["user_id"],
            weibo_item["username"],
            weibo_item["time"],
            weibo_item["content"],
            weibo_item["repost_amount"],
            weibo_item["comment_amount"],
            weibo_item["like_amount"],
            weibo_item["origin_weibo_id"],
            weibo_item["platform"],
            weibo_item["create_time"],
            weibo_item["modify_time"],
        ))

    @staticmethod
    def _insert_item(raw_sql):
        def insert(cursor, item):
            cursor.execute(raw_sql, item)
        return insert
