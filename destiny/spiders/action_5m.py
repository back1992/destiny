# -*- coding: utf-8 -*-
import pandas as pd
from django.db.models import Q
from myapp.models import *
from destiny.items import *
from scrapy.utils.project import get_project_settings
from datetime import datetime, time
import pytz
from destiny import indicator

tz = pytz.timezone('Asia/Shanghai')

settings = get_project_settings()

df_codes = Signal.objects.filter(~Q(action=0)).to_dataframe(fieldnames=['action'], index='code')


# print(df_codes)


# qs = Codeset.objects.filter(codeen__in=df_codes.index)
# qs = Codeset.objects.filter(nighttrade=True, codeen__in=df_codes.index)
# qs = Codeset.objects.filter(nighttrade=True).filter(codeen__in=df_codes.index)
# print(qs)


class Action5MSpider(scrapy.Spider):
    name = "action_5m"
    allowed_domains = ["*"]

    now = datetime.now(tz)
    now_time = now.time()
    # if now_time >= time(9, 00) and now_time <= time(11, 30):
    #     print('day')
    #     open_time = "09:05:00"
    #     qs = Codeset.objects.filter(codeen__in=df_codes.index)
    # elif now_time >= time(13, 30) and now_time <= time(15, 00):
    #     print('aftenoon')
    #     open_time = "13:35:00"
    #     qs = Codeset.objects.filter(codeen__in=df_codes.index)
    # elif now_time >= time(21, 00) and now_time <= time(11, 30):
    #     print('night')
    #     qs = Codeset.objects.filter(nighttrade=True, codeen__in=df_codes.index)
    #     open_time = "21:05:00"
    # else:
    #     # qs = Codeset.objects.filter(actived=True)
    #     qs = Codeset.objects.filter(nighttrade=True, codeen__in=df_codes.index)
    haihai = ['V', 'TA', 'J', 'I', 'SR', 'BU']
    # qs = Codeset.objects.filter(codeen__in=df_codes.index)
    qs = Codeset.objects.filter(codeen__in=haihai)

    if qs:
        start_urls = (
            'http://stock2.finance.sina.com.cn/futures/api/json.php/%s%s?symbol=%s' % (
                "IndexService.getInnerFuturesMiniKLine", '30m',
                code.maincontract)
            for code in qs)
    else:
        start_urls = []
    custom_settings = {
        'ITEM_PIPELINES': {
            'destiny.pipelines.DestinyPipeline': 100,
        },
    }

    def parse(self, response):
        codeen = response.url.split('=')[-1][:-4]
        code = Codeset.objects.get(codeen=codeen)
        df = pd.read_json(response.url)
        df = pd.DataFrame(
            {'date': df[0], 'open': df[1].astype('float'), 'high': df[2].astype('float'), 'low': df[3].astype('float'),
             'close': df[4].astype('float'), 'volume': df[5]})
        df = df.set_index('date').sort_index(ascending=[1])
        item = DestinyItem()
        item['title'] = 'high frequency action'
        item['code'] = code.codezh + '--' + code.maincontract
        macd = indicator.get_macd(df)
        kdj = indicator.get_kdj(df)
        rsi = indicator.get_rsi(df)
        cci = indicator.get_cci(df)
        item['macd'] = sum(macd.values())
        item['kdj'] = sum(kdj.values())
        item['rsi'] = sum(rsi.values())
        item['cci'] = sum(cci.values())
        yield item
