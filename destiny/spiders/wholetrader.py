# -*- coding: utf-8 -*-

import pandas as pd
import scrapy
from django.db.models import Max

from myapp.models import Codeset, Position, Signal


class WholeTraderSpider(scrapy.Spider):
    name = "whole_trader"
    allowed_domains = ["hexun.com"]
    start_urls = (
        'http://data.futures.hexun.com/',
    )

    custom_settings = {
        'ITEM_PIPELINES': {
            # 'destiny.pipelines.TraderPipeline': 100,
            # 'destiny.pipelines.JsonWriterPipeline': 200,
        },
        'EXTENSIONS': {
            'destiny.extensions.SpiderOpenCloseLogging': 500,
        },
        # 'DEFAULT_REQUEST_HEADERS': {
        #     'Referer': 'http://localhost:8000'
        # }
    }

    def __init__(self, msg_cc='', *args, **kwargs):
        # self.msg_cc = "280037713@qq.com"
        self.msg_cc = ""
        self.receiver = '13261871395@163.com'
        self.track_list = [2, 4, 8, 16]
        # self.msg_cc = "linmuhai@sina.com"
        # self.msg_cc = "465613067@qq.com"

        super(scrapy.Spider, self).__init__(*args, **kwargs)

    def parse(self, response):
        """

        :param response:
        :type response:
        """
        Signal.objects.all().delete()
        date = Position.objects.all().aggregate(Max('date'))['date__max']
        qs = Codeset.objects.filter(actived=True)
        # df = self.get_signal_df(qs, date)
        for code in qs:
            df_signal = pd.DataFrame()
            df = Position.objects.filter(code=code, date=date, buyno__isnull=False, sellno__isnull=False,
                                         tradeno__isnull=False).to_dataframe()
            df['hold_interest'] = df['buyposition'] - df['sellposition']
            df['hold_var'] = df['buyvar'] - df['sellvar']
            df['hold_total'] = df['buyposition'] + df['sellposition']
            df['no_total'] = 2*df['tradeno'] + df['buyno'] + df['sellno']
            df = df.sort_values(by=['no_total'], ascending=[1])
            if df.empty:
                print(code, date)
            else:
                df_signal = df_signal.append(self.get_signal_df(df), ignore_index=True)
        print(df_signal)

        # df_buy = df[df['interest'] > 0][df['var'] > 0].sort_values(by=['var'], ascending=[0])
        # df_sell = df[df['interest'] < 0][df['var'] < 0].sort_values(by=['var'], ascending=[1])
        # sm("今日做多合约品种 " + date.strftime('%Y-%m-%d'), self.send_signal_buy(df_buy), self.receiver, self.msg_cc)
        # sm("今日做空合约品种 " + date.strftime('%Y-%m-%d'), self.send_signal_sell(df_sell), self.receiver, self.msg_cc)

    def get_signal_df(self, df):
        strength_interest = 0
        strength_var = 0
        for num in self.track_list:
            strength_interest += df[:num]['hold_interest'].sum() * 100 / df[:num]['hold_total'].sum()
            strength_var += df[:num]['hold_var'].sum() * 100 / df[:num]['hold_total'].sum()

        name_list = ''
        for index, row in df[:2].iterrows():
            name_list += row['name'] + ' t' + str(row['tradeno']) + ' b:' + str(row['buyno']) + ' s:' + str(
                row['sellno'])

        return {'interest': strength_interest, 'var': strength_var, 'name_list': name_list}


    # def get_signal(self, df):


    def send_signal_buy(self, df):
        signal = ''
        for index, row in df.iterrows():
            signal += '<h3 STYLE="color:red;">做多 ' + row['code'] + '-' + row['contract'] + '</h3>'
            signal += '<p>' + row['name_list'] + '</p>'
            # signal += u'<p>持仓强度: ' + str(row['interest']) + '</p>'
            signal += u'<h4>交易强度: ' + str(int(row['var'])) + '</h4>'
            action_signal = Signal()
            action_signal.code = Codeset.objects.get(codezh=row['code'])
            action_signal.name = 2
            action_signal.trade = 1
            action_signal.strength = int(row['var'])
            action_signal.save()
        return signal

    def send_signal_sell(self, df):
        signal = ''
        for index, row in df.iterrows():
            signal += '<h3 STYLE="color:green;">做空 ' + row['code'] + '-' + row['contract'] + '</h3>'
            signal += '<p>' + row['name_list'] + '</p>'
            # signal += u'<p>持仓强度: ' + str(row['interest']) + '</p>'
            signal += u'<h4>交易强度: ' + str(int(row['var'])) + '</h4>'
            action_signal = Signal()
            action_signal.code = Codeset.objects.get(codezh=row['code'])
            action_signal.name = 2
            action_signal.trade = -1
            action_signal.strength = int(row['var'])
            action_signal.save()

        return signal
