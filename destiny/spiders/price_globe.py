# -*- coding: utf-8 -*-
import re

import scrapy
from django.db.models import Q
from myapp.models import *
from destiny.items import *
from scrapy.utils.project import get_project_settings
import pytz

tz = pytz.timezone('Asia/Shanghai')

settings = get_project_settings()


class PriceGlobeSpider(scrapy.Spider):
    name = "price_globe"
    allowed_domains = ["sinajs.cn"]
    start_urls = (
        'http://hq.sinajs.cn/?list=hf_CT,hf_NID,hf_PBD,hf_SND,hf_ZSD,hf_AHD,hf_CAD,hf_S,hf_W,hf_C,hf_BO,hf_SM,hf_TRB,hf_HG,hf_NG,hf_CL,hf_SI,hf_GC,hf_LHC,hf_OIL,hf_XAU,hf_XAG,hf_XPT,hf_XPD',
    )
    custom_settings = {
        'ITEM_PIPELINES': {
            # 'destiny.pipelines.DestinyPipeline': 100
        },
        'DEFAULT_REQUEST_HEADERS': {
            'Referer': 'http://www.baidu.com'
        },
    }

    def parse(self, response):
        # print(response.body)
        # pattern = 'var hq_str_hf_SI="16.030,-0.3729,16.030,16.040,16.060,15.990,09:33:32,16.090,16.010,179,0,0,2016-12-20,COMEX白银";'
        # pattern = 'ar hq_str_([A-Z]{1:2}\d4)="豆一1705,145954,4186,4227,4163,4198,4213,4216,4217,4204,4206,1,2,216242,149034,'
        # pattern = 'avar hq_str_([\w_]+)="((?:[\d.]+,)+)'
        pattern = 'var hq_str_hf_([A-Z]+)="((?:[^,]+,)+([^,"]+))'
        # pattern = 'var hq_str_hf_([A-Z]+)='

        for line in response.body.splitlines()[1:-1]:
            line_string = line.decode('gbk')
            print(line_string)
            result = re.search(pattern, line_string)
            print(result.group(0))
            code = result.group(1)
            string_match = result.group(2)
            code_zh = result.group(3)
            print(code_zh)

            final = re.findall(r'([^,]+),', string_match)  # or r'\.([\w-]+)' to exclude periods
            print(final)

            price, created = Priceglobe.objects.update_or_create(code=code, pub_date=final[12], pub_time=final[6])

            price.code = code
            price.new = final[0]
            price.wave = final[1]
            price.buy = final[2]
            price.sell = final[3]
            price.high = final[4]
            price.low = final[5]
            # price.pub_time = final[6]
            price.settle = final[7]
            price.open = final[8]
            price.position = final[9]
            # price.pub_date = final[12]
            price.codezh = code_zh
            price.save()

            # print(result.group(0))
            # print(result.group(1))
            # print(result.group(2))
            # print(result.group(3))
            # print(final)
            # lineResult = libLAPFF.parseLine(line)
            # df = pd.read_json(response.url, orient=None, typ='frame', dtype=True, convert_axes=True, convert_dates=True,
            #                   keep_default_dates=True, numpy=False, precise_float=False, date_unit=None)
            # df = df[:100].iloc[::-1]
            # df = pd.DataFrame(
            #     {'date': df[0], 'open': df[1].astype(float), 'high': df[2].astype(float), 'low': df[3].astype(float),
            #      'close': df[4].astype(float), 'volume': df[5]})
            # df[df['volume'] == 0] = numpy.nan
            # df = df.dropna()
            # mysignal = signal_investing_5m(df)
            # if mysignal:
            #     item = signal_investing_item()
            #     item['code'] = response.meta['code']
            #     item['period'] = 'day'
            #     item['channel'] = '#general'
            #     item['time'] = df.iloc[-1]['date']
            #     item['signalcci'] = mysignal['cci']
            #     item['signalmacd'] = mysignal['macd']
            #     item['signalkdj'] = mysignal['kdj']
            #     item['s60'] = mysignal['s60']
            #     item['mean60'] = mysignal['mean60']
            #     item['last_close'] = mysignal['last_close']
            #     item['title'] = u'高频信号'
            #     yield item
