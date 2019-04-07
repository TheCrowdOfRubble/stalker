# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import stalker.items as items
from twisted.enterprise import adbapi

dbpool = adbapi.ConnectionPool('MySQLdb', host='127.0.0.1', database='The_Crowd_of_Rubble', user='root',
                               password='rootroot', charset='utf8mb4', cp_min=1, cp_max=1, use_unicode=True)


class PersistencePipeline(object):
    def process_item(self, item, spider):
        if type(item) is items.UserItem:
            self.process_user_item(item)
        else:
            self.process_weibo_item(item)

    def process_user_item(self, item):
        dbpool.runInteraction(self.insert, "users", item)

    def process_weibo_item(self, item):
        dbpool.runInteraction(self.insert, "weiboes", item)

    def insert(self, tx, table_name, item):
        keys = ""
        values = ""
        for field in item:
            keys += "`%s`," % field
            values += "%s,"
        sql = "INSERT INTO %s (%s) VALUES (%s)" % (table_name, keys[:-1], values[:-1])
        tx.execute(sql, tuple(dict(item).values()))
