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


class HighFrequencySpider(scrapy.Spider):
    name = "high_frequency"
    allowed_domains = ["sinajs.cn"]
    start_urls = (
        'http://hq.sinajs.cn/list=M0,TA1705',
    )
    custom_settings = {
        'ITEM_PIPELINES': {
            'destiny.pipelines.InvestingCCIPipeline': 100
        },
        'EXTENSIONS': {
            # 'destiny.extensions.SinaCCIBeta5MSignal': 500,
        },
        'DEFAULT_REQUEST_HEADERS': {
            'Referer': 'http://finance.sina.com.cn'
        },
    }

    def __init__(self, msg_cc='', *args, **kwargs):
        self.msg_cc = ""
        super(scrapy.Spider, self).__init__(*args, **kwargs)

    def parse(self, response):
        values = Signal.objects.filter(~Q(trade=0)).values_list('code', flat=True)
        qs = Codeset.objects.filter(pk__in=list(values)).values_list('maincontract', flat=True)
        query_string = ','.join(filter(None, list(qs)))
        url = 'http://hq.sinajs.cn/list=' + query_string
        print(url)
        yield scrapy.Request(url, callback=self.parseItem)

    def parseItem(self, response):
        # print(response.body)
        # pattern = 'ar hq_str_([A-Z]{1:2}\d4)="豆一1705,145954,4186,4227,4163,4198,4213,4216,4217,4204,4206,1,2,216242,149034,'
        pattern = 'ar hq_str_(([A-Z]+)\d{4})="[^\d]+\d{4},((?:[\d.]+,)+)'

        for line in response.body.splitlines():
            line_string = line.decode('gbk')
            result = re.search(pattern, line_string)
            final = re.findall(r'([\d.]+),', result.group(3))  # or r'\.([\w-]+)' to exclude periods

            price = Pricefreq()
            codeen = result.group(2)

            price.code = Codeset.objects.get(codeen=codeen)
            price.open = final[1]
            price.high = final[2]
            price.low = final[3]
            price.lastclose = final[4]
            price.buy = final[5]
            price.sell = final[6]
            price.close = final[7]
            price.avg = final[8]
            price.settle = final[9]
            price.buyvolume = final[10]
            price.sellvolume = final[11]
            price.hold = final[12]
            price.volume = final[13]
            print(codeen, final)
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
