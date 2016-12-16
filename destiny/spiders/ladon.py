# -*- coding: utf-8 -*-
from datetime import timedelta

import math
import pandas as pd
import scrapy
import sys
from django.db.models import Count, Avg, Max
from django.db.models import F
from django.db.models import Q
from destiny.items import *
from myapp.models import Codeset, Price, Position, Ladon
from django.db.models import Sum


class LadonSpider(scrapy.Spider):
    name = "ladon"
    allowed_domains = ["baidu.com"]
    start_urls = (
        'http://www.baidu.com',
    )

    def __init__(self, msg_cc='', *args, **kwargs):
        # self.msg_cc = "280037713@qq.com"
        self.msg_cc = ""
        # self.msg_cc = "465613067@qq.com"

        super(scrapy.Spider, self).__init__(*args, **kwargs)

    def parse(self, response):
        Ladon.objects.all().delete()
        # date = df_price.index[0]
        # print(date)
        qs = Codeset.objects.filter(actived=True)
        for code in qs[:3]:
            df_ladon = pd.DataFrame()
            df_pos = Position.objects.annotate(last_date=Max('date')).filter(code=code, date=F('last_date'),
                                                                             tradeno__isnull=False).to_dataframe()
            # print(df_pos)
            df_price = Price.objects.filter(code=code).order_by('-date').to_dataframe(['close'], index='date')
            print(df_price[:5])

            for name in df_pos['name'][:3]:
                df_name = Position.objects.filter(code=code, name=name, tradeno__isnull=False).filter(
                    Q(buyno__isnull=False) | Q(sellno__isnull=False)).order_by('-date').to_dataframe(index='date')
                df_name['hold_total'] = df_name['buyposition'] + df_name['sellposition']
                df_name['hold_interest'] = df_name['buyposition'] - df_name['sellposition']
                df_name['hold_var'] = df_name['buyvar'] - df_name['sellvar']
                df_name['hold_var_strength'] = df_name['hold_var'] / (
                    df_name['buyposition'] + df_name['sellposition'])
                df_name['direction'] = df_name['hold_var'] * df_name['hold_interest']
                # df_name = pd.concat(df_name, df_price, axis=1)
                df_name['close'] = df_price['close']
                # remove today data cause no result price
                df_name = df_name[1:]
                df_name = df_name[df_name['direction'] > 0]
                print(df_name[:5])
                corelation = df_name.corr()['close']['hold_interest']
                print(corelation)
                if not math.isnan(corelation):
                    df_ladon = df_ladon.append(
                        {'name': name, 'corelation': corelation,
                         'tradeno': df_name['tradeno'].iloc[-1], 'hold_var': df_name['hold_var'].iloc[-1],
                         'hold_var_strength': df_name['hold_var_strength'].iloc[-1],
                         'date': df_name.index[0]},
                        ignore_index=True)
                print(df_ladon)
                # df_ladon = df_ladon.sort_values(['corelation'], ascending=[False]).reset_index()
            df_ladon = df_ladon.sort_values(['corelation'], ascending=[False])
            df_records = df_ladon.to_dict('records')
            print(df_records[:5])
            #
            #         model_instances = [Ladon(code=code,
            #                                  name=record['name'],
            #                                  corelation=record['corelation'],
            #                                  holdvarstrength=record['hold_var_strength'],
            #                                  holdvar=record['hold_var'],
            #                                  tradeno=record['tradeno'], date=record['date'], no=index + 1) for index, record
            #                            in
            #                            enumerate(df_records)]
            #
            #         Ladon.objects.bulk_create(model_instances)
