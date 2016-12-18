# -*- coding: utf-8 -*-
import datetime

import pandas as pd
from myapp.models import *
from destiny.items import *
from scrapy.utils.project import get_project_settings
from datetime import datetime, time
import pytz

tz = pytz.timezone('Asia/Shanghai')
settings = get_project_settings()


class Price5mSpider(scrapy.Spider):
    name = "price_5m"
    period = '5m'
    allowed_domains = ["*"]
    # marketurl = Marketurl.objects.get(market=0).minute
    # print(marketurl)
    # marketurl = Marketurl.objects.filter(market=0)
    # print(marketurl)

    now = datetime.now(tz)
    now_time = now.time()
    print(now_time)
    if now_time >= time(9, 00) and now_time <= time(11, 30):
        print('day')
        open_time = "09:05:00"
        qs = Codeset.objects.filter(actived=True)
    elif now_time >= time(13, 30) and now_time <= time(15, 00):
        print('aftenoon')
        open_time = "13:35:00"
        qs = Codeset.objects.filter(actived=True)
    else:
        print('night')
        qs = Codeset.objects.filter(nighttrade=True, actived=True)
    open_time = "21:05:00"
    start_urls = (
        'http://stock2.finance.sina.com.cn/futures/api/json.php/%s%s?symbol=%s' % (
            "IndexService.getInnerFuturesMiniKLine", '5m',
            code.maincontract)
        for code in qs)

    def parse(self, response):
        df = pd.read_json(response.url, orient=None, typ='frame', dtype=True, convert_axes=True, convert_dates=True,
                          keep_default_dates=True, numpy=False, precise_float=False, date_unit=None)
        print(df[:5])

        #     for code in qs:
        #         period = '5'
        #         url = 'http://stock2.finance.sina.com.cn/futures/api/json.php/' + marketurl[0][
        #             'minute'] + period + 'm?symbol=' + code.maincontract
        #         yield scrapy.Request(url, callback=self.parseItem)
        #
        # def parseItem(self, response):
        #     df = pd.read_json(response.url, orient=None, typ='frame', dtype=True, convert_axes=True, convert_dates=True,
        #                       keep_default_dates=True, numpy=False, precise_float=False, date_unit=None)
        #     print(df)
        #     # df = df[:100].iloc[::-1]
        #     # df = pd.DataFrame(
        #     #     {'date': df[0], 'open': df[1].astype(float), 'high': df[2].astype(float), 'low': df[3].astype(float),
        #     #      'close': df[4].astype(float), 'volume': df[5]})
        #     #
        #     # def parseItem(self, response):
        #     #     # df = pd.read_json(response.url, orient=None, typ='frame', dtype=True, convert_axes=True, convert_dates=True,
        #     #     #                   keep_default_dates=True, numpy=False, precise_float=False, date_unit=None)
        #     #     df = pd.read_json(response.url)
        #     #     df = pd.DataFrame({'date': df[0], 'open': df[1], 'high': df[2], 'low': df[3], 'close': df[4], 'volume': df[5]})
        #     #     # df.set_index('date', inplace=True)
        #     #     df.set_index('date')
        #
        #     # df['res'] = df['close'] - df['close'].shift()
        #     # df = df[-5:]
        #     # df_records = df.to_dict('records')
        #     # print(df_records)
        #     # code = response.meta['code']
        #     # model_instances = [Price5m(
        #     #     code=code,
        #     #     # date=record['date'],
        #     #     date=datetime.strptime(record['date'], '%Y-%m-%d'),
        #     #     open=record['open'],
        #     #     high=record['high'],
        #     #     low=record['low'],
        #     #     close=record['close'],
        #     #     res=record['res'],
        #     #     volume=record['volume'],
        #     # ) for record in df_records]
        #     #
        #     # Price5m.objects.bulk_create(model_instances)
