# -*- coding: utf-8 -*-

import quandl
from destiny import indicator
from datetime import date, datetime
import pytz
import slackweb
from myapp.models import Quandlset
from destiny.items import *
from scrapy.utils.project import get_project_settings

settings = get_project_settings()

today = date.today()
# day_before_yesterday = datetime.date.today() - datetime.timedelta(days=3)
quandl.ApiConfig.api_key = "taJyZN8QXqj2Dj8SNr6Z"
quandl.ApiConfig.api_version = '2015-04-09'
slack = slackweb.Slack(url="https://hooks.slack.com/services/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")
utc = pytz.UTC


class QuandldataSpider(scrapy.Spider):
    name = "quandl_data"
    allowed_domains = ["www.baidu.com"]
    start_urls = (
        'http://www.baidu.com',
    )
    custom_settings = {
        'ITEM_PIPELINES': {
            'destiny.pipelines.DestinyPipeline': 100
        },
        'EXTENSIONS': {
            # 'destiny.extensions.QuandlCCISignal': 600,
        },
        'DEFAULT_REQUEST_HEADERS': {
            'Referer': 'http://www.baidu.com'
        }
    }

    # def __init__(self, msg_cc='', *args, **kwargs):
    #     # self.msg_cc = "280037713@qq.com"
    #     self.msg_cc = "linmuhai@sina.com"
    #     # self.msg_cc = "465613067@qq.com"
    #     # self.msg_cc = ""
    #
    #     super(scrapy.Spider, self).__init__(*args, **kwargs)

    def parse(self, response):
        qs = Quandlset.objects.filter(actived=True)
        for p in qs:
            symbol = p.quandlcode + "1"
            p.actived = True
            p.save()
            try:
                df = quandl.get(symbol)[-80:]
                print(df)
            except:
                print("error")
                print(symbol)
                continue
            if 'Last' in df.columns:
                df = df.rename(
                    columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Last': 'close'})
            elif 'Close' in df.columns:
                df = df.rename(
                    columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'})
            elif 'Settle' in df.columns:
                df = df.rename(
                    columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Settle': 'close'})
            else:
                p.actived = False
                p.save()
                continue
            # item = DestinyItem()
            # item['code'] = p.namezh + ' ' + p.exchange + ' ' + p.name
            # item['period'] = 'day'
            # item['channel'] = '#general'
            # item['time'] = df.index[-1].strftime('%Y-%m-%d')
            # item['signalcci'] = signal_quandl(df)
            # item['last_close'] = df['close'][df.index[-1]]
            # item['title'] = u'全球市场扫描'
            # yield item

            item = DestinyItem()
            item['title'] = 'sleepless money'
            item['code'] = p.namezh + ' ' + p.exchange + ' ' + p.name
            macd = indicator.get_macd(df)
            kdj = indicator.get_kdj(df)
            rsi = indicator.get_rsi(df)
            cci = indicator.get_cci(df)
            item['macd'] = sum(macd.values())
            item['kdj'] = sum(kdj.values())
            item['rsi'] = sum(rsi.values())
            item['cci'] = sum(cci.values())
            yield item
