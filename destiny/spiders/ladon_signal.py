# -*- coding: utf-8 -*-
import pandas as pd
import scrapy
import sys
from django.db.models import Count, Avg
from django.db.models import F
from destiny.items import *
from myapp.models import Codeset, Price, Position, Ladon
from django.db.models import Sum
from destiny.sm2 import sm


class LadonSignalSpider(scrapy.Spider):
    name = "ladon_signal"
    allowed_domains = ["baidu.com"]
    start_urls = (
        # 'http://quote.futures.hexun.com/price.aspx?market=all&type=zhuli',
        # 'http://vip.stock.finance.sina.com.cn/quotes_service/view/js/qihuohangqing.js',
        # 'http://quote.futures.hexun.com/EmbPrice.aspx?market=3&type=all',
        'http://www.baidu.com',
    )

    custom_settings = {
        'ITEM_PIPELINES': {
            # 'destiny.pipelines.PositionListPipeline': 100,
        },
        'EXTENSIONS': {
            # 'destiny.extensions.SpiderOpenCloseLogging': 500,
        },
        # 'DEFAULT_REQUEST_HEADERS': {
        #     'Referer': 'http://localhost:8000'
        # }
    }

    def __init__(self, msg_cc='', *args, **kwargs):
        # self.msg_cc = "280037713@qq.com"
        self.receiver = "13261871395@163.com"
        self.msg_cc = ""
        # self.msg_cc = "465613067@qq.com"

        super(scrapy.Spider, self).__init__(*args, **kwargs)

    def parse(self, response):
        df = pd.DataFrame()
        qs = Codeset.objects.filter(actived=True)
        for code in qs:
            try:
                ls = Ladon.objects.filter(code=code).to_dataframe()
                # ls = Ladon.objects.filter(code=code)
            except:
                print(code, 'error')
            date = ls['date'][0]
            ls['weight_var'] = ls['holdvar'] * ls['corelation']
            ls['abs_hold_var'] = abs(ls['holdvar'])
            signal = ls['weight_var'].sum() / ls['abs_hold_var'].sum()
            df = df.append(
                {'code': code.codezh, 'signal': signal},
                ignore_index=True)
        df = df.sort_values(by=['signal'], ascending=[0])

        df_buy = df[df['signal'] > 0].sort_values(by=['signal'], ascending=[0])
        df_sell = df[df['signal'] < 0].sort_values(by=['signal'], ascending=[1])
        sm("加权做多信号 " + date.strftime('%Y-%m-%d'), self.send_signal_buy(df_buy), self.receiver, self.msg_cc)
        sm("加权做空信号 " + date.strftime('%Y-%m-%d'), self.send_signal_sell(df_sell), self.receiver, self.msg_cc)

    def send_signal_buy(self, df):
        signal = ''
        for index, row in df.iterrows():
            signal += '<h3 STYLE="color:red;">做多 ' + row['code'] + '</h3>'
            signal += u'<p>强度: ' + str(int(row['signal'] * 100)) + '</p>'
        return signal

    def send_signal_sell(self, df):
        signal = ''
        for index, row in df.iterrows():
            signal += '<h3 STYLE="color:green;">做空 ' + row['code'] + '</h3>'
            signal += u'<p>强度: ' + str(int(row['signal'] * 100)) + '</p>'
        return signal
