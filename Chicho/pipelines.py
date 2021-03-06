# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
import scrapy

class ChichoPipeline(object):

    def process_item(self, item, spider):
        return item


class MyImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for url in item['img_url']:
            yield scrapy.Request(url, meta={'item': item})

    # def file_path(self, request, response=None, info=None):
    #     item = request.meta['item']
    #     return 't'
