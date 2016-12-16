# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field
from scrapy_djangoitem import DjangoItem
from myapp.models import Quandlset, Proxyip


class DestinyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class signal_investing_item(Item):
    code = Field()
    title = Field()
    period = Field()
    time = Field()
    channel = Field()
    signalmacd = Field()
    signalcci = Field()
    signalkdj = Field()
    s60 = Field()
    last_close = Field()
    mean60 = Field()
    amplitude = Field()