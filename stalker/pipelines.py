# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import stalker.items as items
import scrapy.exceptions

"""
class StalkerPipeline(object):
    def process_item(self, item, spider):
        return item
"""


class PersistencePipeline(object):
    def process_item(self, item, spider):
        if type(item) is items.UserItem:
            self.process_user_item(item)
        else:
            self.process_weibo_item(item)

    def process_user_item(self, item):
        print(item['user_id'])
        pass

    def process_weibo_item(self, item):
        print(item['weibo_id'])
        pass
