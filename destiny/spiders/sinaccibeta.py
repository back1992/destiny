# -*- coding: utf-8 -*-
import datetime

import numpy
import pandas as pd
import scrapy
from myapp.models import *
from destiny.items import *
from scrapy.utils.project import get_project_settings

from destiny.signal import signal_investing

settings = get_project_settings()


class SinaccibetaSpider(scrapy.Spider):
    name = "sinaccibeta"
    allowed_domains = ["finance.sina.com.cn"]
    start_urls = (
        'http://stock2.finance.sina.com.cn/',
    )
    custom_settings = {
        'ITEM_PIPELINES': {
            'destiny.pipelines.InvestingCCIPipeline': 100
        },
        'EXTENSIONS': {
            # 'destiny.extensions.SinaCCIBeta5MSignal': 500,
        },
        'DEFAULT_REQUEST_HEADERS': {
            # 'Referer': 'http://finance.sina.com.cn'
        },
        # 'DOWNLOADER_MIDDLEWARES': {
        #     #    'cnblogs.middlewares.MyCustomDownloaderMiddleware': 543,
        #     'destiny.middlewares.RandomUserAgent': 1,
        #     'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
        #     # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        #     'destiny.middlewares.ProxyMiddleware': 100,
        # },
        'USER_AGENTS': [
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
            "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
            "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
        ],

        'COOKIES_ENABLED': False,

        'DOWNLOAD_DELAY': 3,
        'RETRY_TIMES': 5,

    }

    def __init__(self, msg_cc='', *args, **kwargs):
        # self.msg_cc = "280037713@qq.com"
        # self.msg_cc = "linmuhai@sina.com"
        # self.msg_cc = "465613067@qq.com"
        self.msg_cc = ""

        super(scrapy.Spider, self).__init__(*args, **kwargs)

    def parse(self, response):
        marketurl = Marketurl.objects.values()
        Price.objects.all().delete()
        qs = Codeset.objects.filter(actived=True)
        for p in qs:
            if p.market == 9:
                url = 'http://stock2.finance.sina.com.cn/futures/api/json.php/' + marketurl[1][
                    'daily'] + '?symbol=' + p.maincontract
            else:
                url = 'http://stock2.finance.sina.com.cn/futures/api/json.php/' + marketurl[0][
                    'daily'] + '?symbol=' + p.maincontract
            print(url)
            yield scrapy.Request(url, meta={'code': p, 'contract': p.maincontract, 'market': p.market,
                                            'dont_redirect': True,
                                            'handle_httpstatus_list': [302]},
                                 callback=self.parseItem, dont_filter=True)

    def parseItem(self, response):
        df = pd.read_json(response.url, orient=None, typ='frame', dtype=True, convert_axes=True, convert_dates=True,
                          keep_default_dates=True, numpy=False, precise_float=False, date_unit=None)
        df = pd.DataFrame(
            {'date': df[0], 'open': df[1].astype(float), 'high': df[2].astype(float), 'low': df[3].astype(float),
             'close': df[4].astype(float), 'volume': df[5]})
        # df['res'] = df['close'] - df['open']
        # df_new = df['res']
        # df_new.index = df['res'].index - 1
        # df['resnew'] = df_new
        # df['resnew'].iloc[-1] = 0

        df['res'] = df['close'] - df['close'].shift()
        df['resnew'] = df['res'].shift(-1)

        df['resnew'].iloc[-1] = 0
        df = df[-61:]
        df_records = df.to_dict('records')
        code = response.meta['code']
        model_instances = [Price(
            code=code,
            # date=record['date'],
            date=datetime.datetime.strptime(record['date'], '%Y-%m-%d'),
            open=record['open'],
            high=record['high'],
            low=record['low'],
            close=record['close'],
            res=record['res'],
            resnew=record['resnew'],
            volume=record['volume'],
        ) for record in df_records]

        Price.objects.bulk_create(model_instances)

        df[df['volume'] == 0] = numpy.nan
        df = df.dropna()
        mysignal = signal_investing(df)
        if mysignal:
            item = signal_investing_item()
            item['code'] = code.codezh + ' ' + code.maincontract
            item['period'] = 'day'
            item['channel'] = '#general'
            item['time'] = df.iloc[-1]['date']
            # item['time'] = datetime.strptime(df.iloc[-1]['date'], '%Y-%m-%d')
            item['signalcci'] = mysignal['cci']
            item['signalmacd'] = mysignal['macd']
            item['signalkdj'] = mysignal['kdj']
            item['amplitude'] = mysignal['amplitude']
            item['s60'] = mysignal['s60']
            item['mean60'] = mysignal['mean60']
            item['last_close'] = mysignal['last_close']
            item['title'] = u'新版内盘信号'
            yield item
