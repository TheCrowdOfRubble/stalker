# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import typing
import logging

import twisted.python.failure
from twisted.enterprise import adbapi
import scrapy
from scrapy_redis.pipelines import RedisPipeline, default_serialize, defaults

import stalker.items as items
import stalker.settings as settings


class PersistencePipeline:
    def __init__(self) -> type(None):
        self.db_pool = adbapi.ConnectionPool(
            "MySQLdb",
            db=settings.DB_NAME,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            passwd=settings.DB_PASSWORD,
            charset=settings.DB_CHARSET,
            cp_min=settings.DB_MIN_POOL_SIZE,
            cp_max=settings.DB_MAX_POOL_SIZE,
            use_unicode=settings.DB_USE_UNICODE,
        )

    def process_item(self, item: items.BaseItem, spider: scrapy.Spider) -> type(None):
        if isinstance(item, items.UserItem):
            self._process_user_item(item)
        elif isinstance(item, items.WeiboItem):
            self._process_weibo_item(item)
        else:
            logging.critical("GET WRONG ITEM %s", item)

    def _process_user_item(self, user_item):
        self.db_pool.runInteraction(self._exec_sql(settings.USER_INSERT_SQL), (
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
        )).addErrback(self._update_user_item, user_item)

    def _process_weibo_item(self, weibo_item):
        self.db_pool.runInteraction(self._exec_sql(settings.WEIBO_INSERT_SQL), (
            weibo_item["weibo_id"],
            weibo_item["user_id"],
            weibo_item["time"],
            weibo_item["content"],
            weibo_item["repost_amount"],
            weibo_item["comment_amount"],
            weibo_item["like_amount"],
            weibo_item["origin_weibo_id"],
            weibo_item["platform"],
        )).addErrback(self._update_weibo_item, weibo_item)

    def _update_user_item(self, failure: twisted.python.failure.Failure, user_item: items.UserItem) -> type(None):
        self.db_pool.runInteraction(
            self._exec_sql(settings.USER_UPDATE_SQL), (
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
                user_item["user_id"],
            )
        ).addErrback(self._error_handler, user_item)

    def _update_weibo_item(self, failure: twisted.python.failure.Failure, weibo_item: items.WeiboItem) -> type(None):
        self.db_pool.runInteraction(
            self._exec_sql(settings.WEIBO_UPDATE_SQL), (
                weibo_item["user_id"],
                weibo_item["time"],
                weibo_item["content"],
                weibo_item["repost_amount"],
                weibo_item["comment_amount"],
                weibo_item["like_amount"],
                weibo_item["origin_weibo_id"],
                weibo_item["platform"],
                weibo_item["weibo_id"]
            )
        ).addErrback(self._error_handler, weibo_item)

    @staticmethod
    def _exec_sql(raw_sql: str) -> typing.Callable[[adbapi.Transaction, items.BaseItem], type(None)]:
        def exec_sql(cursor: adbapi.Transaction, item: items.BaseItem) -> type(None):
            cursor.execute(raw_sql, item)
            logging.info(cursor._last_executed)

        return exec_sql

    @staticmethod
    def _error_handler(failure, item):
        logging.warning("ERROR IN UPDATE %s", item)


class WeiboItemExportToRedisPipeline(RedisPipeline):
    def __init__(self, server, key=defaults.PIPELINE_KEY, serialize_func=default_serialize):
        super().__init__(server, key, serialize_func)

    def process_item(self, item, spider):
        if isinstance(item, items.WeiboItem):
            super().process_item(item, spider)

        return item
