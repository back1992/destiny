# -*- coding: utf-8 -*-
import math
import pandas as pd
from django.db.models import Count, Avg, Max
from django.db.models import F
from django.db.models import Q
from destiny.items import *
from myapp.models import Codeset, Price, Position, Ladon


class LadonSpider(scrapy.Spider):
    name = "ladon"
    allowed_domains = ["baidu.com"]
    start_urls = (
        'http://www.baidu.com',
    )

    def __init__(self, msg_cc='', *args, **kwargs):
        self.msg_cc = ""

        super(scrapy.Spider, self).__init__(*args, **kwargs)

    def parse(self, response):
        Ladon.objects.all().delete()
        qs = Codeset.objects.filter(actived=True)
        # qs = Codeset.objects.filter(codeen='CS')
        for code in qs:
            df_ladon = pd.DataFrame()
            date = Position.objects.all().aggregate(Max('date'))['date__max']
            name_list = list(
                Position.objects.filter(code=code, date=date, buyno__lt=60, sellno__lt=60).values_list('name',
                                                                                                       flat=True))
            print(len(name_list))
            df_price = Price.objects.filter(code=code).order_by('-date').to_dataframe(['close'], index='date')
            if not df_price.empty:
                weight_var = 0
                for name in name_list:
                    df_name = Position.objects.filter(code=code, name=name).order_by('date').to_dataframe(index='date')
                    df_name['hold_interest'] = df_name['buyposition'] - df_name['sellposition']
                    df_name['hold_total'] = df_name['buyposition'] + df_name['sellposition']
                    df_name['hold_var'] = df_name['buyvar'] - df_name['sellvar']
                    df_name['close'] = df_price['close']
                    # print(df_name[:5])
                    corelation = df_name.corr()['close']['hold_interest']
                    weight_var += df_name['hold_var'].iloc[-1] * corelation / df_name['hold_total'].iloc[-1]
                print(code, weight_var, df_name.index[-1])
                # if not math.isnan(corelation):
                #     df_ladon = df_ladon.append(
                #         {'name': name, 'corelation': corelation,
                #          'tradeno': df_name['tradeno'].iloc[-1], 'hold_var': df_name['hold_var'].iloc[-1],
                #          'hold_var_strength': df_name['hold_var_strength'].iloc[-1],
                #          'date': df_name.index[0]},
                #         ignore_index=True)
                # print(df_ladon)
                #     # df_ladon = df_ladon.sort_values(['corelation'], ascending=[False]).reset_index()
                # df_ladon = df_ladon.sort_values(['corelation'], ascending=[False])
                # df_records = df_ladon.to_dict('records')
                # print(df_records[:5])
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
