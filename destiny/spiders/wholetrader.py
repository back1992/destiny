# -*- coding: utf-8 -*-

import pandas as pd
import scrapy
from django.db.models import Max

from myapp.models import Codeset, Position, Signal
from destiny.sm2 import sm


class WholeTraderSpider(scrapy.Spider):
    name = "whole_trader"
    allowed_domains = ["baidu.com"]
    start_urls = (
        'http://www.baidu.com/',
    )

    def __init__(self, msg_cc='', *args, **kwargs):
        self.msg_cc = ""
        self.receiver = '13261871395@163.com'
        self.track_list = [2, 4, 8, 16]

        super(scrapy.Spider, self).__init__(*args, **kwargs)

    def parse(self, response):
        """

        :param response:
        :type response:
        """
        date = Position.objects.all().aggregate(Max('date'))['date__max']
        qs = Codeset.objects.filter(actived=True)
        df_signal = pd.DataFrame()
        for code in qs:
            df = Position.objects.filter(code=code, date=date, buyno__isnull=False, sellno__isnull=False,
                                         tradeno__isnull=False).to_dataframe()
            if df.empty:
                print(code, date, 'error')
            else:
                df['hold_interest'] = df['buyposition'] - df['sellposition']
                df['hold_var'] = df['buyvar'] - df['sellvar']
                df['volume_var'] = df['buyvar'] + df['sellvar']
                df['hold_total'] = df['buyposition'] + df['sellposition']
                df['no_total'] = 2 * df['tradeno'] + df['buyno'] + df['sellno']
                df = df.sort_values(by=['no_total'], ascending=[1])
                signal = self.get_signal_df(df)
                signal['code'] = code.codezh
                signal['contract'] = code.maincontract
                df_signal = df_signal.append(signal, ignore_index=True)
        print(df_signal)
        df_signal['vi'] = df_signal['interest'] + 3 * df_signal['var']

        df_signal_buy = df_signal[df_signal['vi'] > 0].sort_values(by=['vi'], ascending=[0])
        df_signal_sell = df_signal[df_signal['vi'] < 0].sort_values(by=['vi'], ascending=[1])
        sm("今日做多合约品种 " + date.strftime('%Y-%m-%d'), self.send_signal_buy(df_signal_buy), self.receiver, self.msg_cc)
        sm("今日做空合约品种 " + date.strftime('%Y-%m-%d'), self.send_signal_sell(df_signal_sell), self.receiver, self.msg_cc)

    def get_signal_df(self, df):
        strength_interest = 0
        strength_var = 0
        volume_var = 0
        for num in self.track_list:
            hold_total_sum = df[:num]['hold_total'].sum()
            strength_interest += df[:num]['hold_interest'].sum() * 100 / hold_total_sum
            strength_var += df[:num]['hold_var'].sum() * 100 / hold_total_sum
            volume_var += df[:num]['volume_var'].sum()
        name_list = ''
        for index, row in df[:2].iterrows():
            name_list += row['name'] + ' t' + str(row['tradeno']) + ' b:' + str(row['buyno']) + ' s:' + str(
                row['sellno'])
        result = {'interest': strength_interest, 'var': strength_var, 'name_list': name_list, 'volume_var': volume_var}
        return result

    def send_signal_buy(self, df):
        signal = ''
        for index, row in df.iterrows():
            if row['volume_var'] > 0:
                signal += '<h3 STYLE="color:red;">做多 ' + row['code'] + '-' + row['contract'] + '</h3>'
            else:
                signal += '<h3>做多 ' + row['code'] + '-' + row['contract'] + '</h3>'
            signal += '<p>' + row['name_list'] + '</p>'
            # signal += u'<p>持仓强度: ' + str(row['interest']) + '</p>'
            signal += u'<h4>交易强度: ' + str(int(row['var'])) + '</h4>'
            action_signal, created = Signal.objects.update_or_create(code=Codeset.objects.get(codezh=row['code']))
            action_signal.trade = row['var']
            action_signal.save()
        return signal

    def send_signal_sell(self, df):
        signal = ''
        for index, row in df.iterrows():
            if row['volume_var'] < 0:
                signal += '<h3 STYLE="color:green;">做空 ' + row['code'] + '-' + row['contract'] + '</h3>'
            else:
                signal += '<h3>做空 ' + row['code'] + '-' + row['contract'] + '</h3>'
            signal += '<p>' + row['name_list'] + '</p>'
            # signal += u'<p>持仓强度: ' + str(row['interest']) + '</p>'
            signal += u'<h4>交易强度: ' + str(int(row['var'])) + '</h4>'

            action_signal, created = Signal.objects.update_or_create(code=Codeset.objects.get(codezh=row['code']))
            action_signal.trade = row['var']
            action_signal.save()
        return signal
