# -*- coding: utf-8 -*-
import datetime
import scrapy
import pandas as pd
from destiny import indicator
from destiny.items import *
from myapp.models import Investingset
from scrapy.utils.project import get_project_settings

settings = get_project_settings()


class InvestingdataSpider(scrapy.Spider):
    msgbody = ''
    name = "investing_data"
    allowed_domains = ["investing.com"]
    start_urls = (
        'http://www.investing.com/commodities/',
    )
    custom_settings = {
        'ITEM_PIPELINES': {
            'destiny.pipelines.DestinyPipeline': 100
        },
        'DEFAULT_REQUEST_HEADERS': {
            'Referer': 'http://www.investing.com'
        }
    }
    leadurl = 'http://www.investing.com'

    # def __init__(self, msg_cc='', *args, **kwargs):
    #     # self.msg_cc = "280037713@qq.com"
    #     self.msg_cc = "linmuhai@sina.com"
    #     # self.msg_cc = "465613067@qq.com"
    #
    #     super(scrapy.Spider, self).__init__(*args, **kwargs)

    def parse(self, response):
        qs = Investingset.objects.all()
        for p in qs:
            yield scrapy.Request(p.url, meta={'code': p.name, 'codezh': p.namezh, 'url': p.url},
                                 callback=self.parseItem)

    def parseItem(self, response):
        trs = response.xpath('/html/body/div[5]/section/div[9]/table[1]/tbody/tr')
        if len(trs) > 20:
            trs.reverse()
            df = pd.DataFrame()
            for tr in trs:
                row = tr.xpath('./td/text()').extract()
                if row[5] == '-':
                    row[5] = 0
                elif row[5][-1:] == 'K':
                    row[5] = float(row[5][:-1]) * 1000
                elif row[5][-1:] == 'M':
                    row[5] = float(row[5][:-1]) * 1000 * 1000
                dateobj = datetime.datetime.strptime(row[0], '%b %d, %Y')
                date = dateobj.strftime('%Y-%m-%d')
                df = df.append({'date': date, 'close': float(row[1]), 'open': float(row[2]), 'high': float(row[3]),
                                'low': float(row[4]), 'volume': float(row[5])}, ignore_index=True)
            now_date = df.iloc[-1]['date']
            if not df.empty:
                item = DestinyItem()
                item['code'] = response.meta['codezh']
                macd = indicator.get_macd(df)
                kdj = indicator.get_kdj(df)
                rsi = indicator.get_rsi(df)
                cci = indicator.get_cci(df)
                item['macd'] = sum(macd.values())
                item['kdj'] = sum(kdj.values())
                item['rsi'] = sum(rsi.values())
                item['cci'] = sum(cci.values())
                yield item


                # mysignal = signal(df)
                # if mysignal:
                #     item = signal_item()
                #     item['code'] = response.meta['codezh']
                #     item['period'] = 'day'
                #     item['channel'] = '#globe_market'
                #     item['time'] = now_date
                #     item['signalcci'] = mysignal['cci']
                #     item['last_close'] = df.iloc[-1]['close']
                #     # item['s60'] = mysignal['s60']
                #     # item['mean60'] = df['close'].mean()
                #     item['title'] = u'外盘信号'
                #     yield item
        else:
            print(response.meta['url'])
            print('error')
