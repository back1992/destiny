# -*- coding: utf-8 -*-
import pandas as pd
import scrapy
import sys
from django.db.models import Count, Avg
from django.db.models import F
from django.db.models import Q

from destiny.items import *
from myapp.models import *
from django.db.models import Sum
from destiny.sm2 import sm


class LadonSignalSpider(scrapy.Spider):
    name = "ladon_signal"
    allowed_domains = ["baidu.com"]
    start_urls = (
        'http://www.baidu.com',
    )

    def __init__(self, msg_cc='', *args, **kwargs):
        # self.msg_cc = "280037713@qq.com"
        self.receiver = "13261871395@163.com"
        self.msg_cc = ""

        super(scrapy.Spider, self).__init__(*args, **kwargs)

    def parse(self, response):
        df = pd.DataFrame()

        df = Signal.objects.filter(~Q(position=0)).to_dataframe()

        df_buy = df[df['position'] > 0].sort_values(by=['position'], ascending=[0])
        df_sell = df[df['position'] < 0].sort_values(by=['position'], ascending=[1])
        print(df_buy)
        print(df_sell)
        sm("加权做多信号 ", self.send_signal_buy(df_buy), self.receiver, self.msg_cc)
        sm("加权做空信号 ", self.send_signal_sell(df_sell), self.receiver, self.msg_cc)

    def send_signal_buy(self, df):
        signal = ''
        for index, row in df.iterrows():
            signal += '<h3 STYLE="color:red;">做多 ' + row['code'] + '</h3>'
            signal += u'<p>强度: ' + str(int(row['position'])) + '</p>'
        return signal

    def send_signal_sell(self, df):
        signal = ''
        for index, row in df.iterrows():
            signal += '<h3 STYLE="color:green;">做空 ' + row['code'] + '</h3>'
            signal += u'<p>强度: ' + str(int(row['position'])) + '</p>'
        return signal
