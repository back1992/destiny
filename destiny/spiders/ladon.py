# -*- coding: utf-8 -*-
from django.db.models import Max
from destiny.items import *
from myapp.models import *


class LadonSpider(scrapy.Spider):
    name = "ladon"
    allowed_domains = ["baidu.com"]
    start_urls = (
        'http://www.baidu.com',
    )

    def parse(self, response):
        Ladon.objects.all().delete()
        qs = Codeset.objects.filter(actived=True)
        for code in qs:
            date = Position.objects.all().aggregate(Max('date'))['date__max']
            name_list = list(
                Position.objects.filter(code=code, date=date, buyno__lt=60, sellno__lt=60).values_list('name',
                                                                                                       flat=True))
            df_price = Price.objects.filter(code=code).order_by('-date').to_dataframe(['close'], index='date')
            if not df_price.empty:
                weight_var = 0
                for name in name_list:
                    df_name = Position.objects.filter(code=code, name=name).order_by('date').to_dataframe(index='date')
                    df_name['hold_interest'] = df_name['buyposition'] - df_name['sellposition']
                    df_name['hold_total'] = df_name['buyposition'] + df_name['sellposition']
                    df_name['hold_var'] = df_name['buyvar'] - df_name['sellvar']
                    print(df_name, df_price)
                    df_name = df_name.join(df_price['close'])
                    print(df_name[:5])
                    corelation = df_name.corr()['close']['hold_interest']
                    weight_var += df_name['hold_var'].iloc[-1] * corelation / df_name['hold_total'].iloc[-1]
                print(code, weight_var, df_name.index[-1])
                action_signal, created = Signal.objects.update_or_create(code=code)
                action_signal.position = weight_var * 100
                action_signal.save()
            else:
                print(code, '--has error')
