# -*- coding: utf-8 -*-
import pandas as pd
from myapp.models import *
from destiny.items import *
from scrapy.utils.project import get_project_settings
from destiny.sm2 import sm

# from destiny.signal import *

settings = get_project_settings()


class ActionDailySpider(scrapy.Spider):
    name = "action_daily"
    allowed_domains = ["baidu.com"]
    start_urls = (
        'http://www.baidu.com/',
    )

    def __init__(self, msg_cc='', *args, **kwargs):
        # self.msg_cc = "280037713@qq.com"
        self.receiver = "13261871395@163.com"
        self.msg_cc = ""

        super(scrapy.Spider, self).__init__(*args, **kwargs)

    def parse(self, response):
        action = ''
        Signal.objects.update(action=0)
        df = Signal.objects.all().to_dataframe()
        df['signal'] = df['macd'] + df['kdj'] + df['rsi'] + df['cci']
        # df = df[df['position'] * df['trade'] > 0].sort_values(by=['trade'], ascending=[-1])
        df = df.sort_values(by=['trade'], ascending=[-1])
        print(df)
        for index, row in df.iterrows():
            code = Codeset.objects.get(codeen=row['code'])
            action_signal, created = Signal.objects.update_or_create(code=code)
            if row['trade'] <= 0 and row['signal'] < -5:
                action_signal.action = -1
                action += '<h3 STYLE="color:green;">做空 ' + code.codezh + '--' + code.maincontract + '</h3>'
                action += '<p style="color:green">强度：' + str(row['trade']) + ' 建仓指数： ' + str(row['position']) + '</p>'
                for index in ['macd', 'kdj', 'rsi', 'cci']:
                    if row[index] < 0:
                        action += '<p style="color:green">' + index + ':' + str(row[index]) + '</p>'
                    elif row[index] > 0:
                        action += '<p style="color:red">' + index + ':' + str(row[index]) + '</p>'
            elif row['trade'] > 0 and row['signal'] > 5:
                action_signal.action = 1
                action += '<h3 STYLE="color:red;">做多 ' + code.codezh + '--' + code.maincontract + '</h3>'
                action += '<p style="color:red">强度：' + str(row['trade']) + ' 建仓指数： ' + str(row['position']) + '</p>'
                for index in ['macd', 'kdj', 'rsi', 'cci']:
                    if row[index] < 0:
                        action += '<p style="color:green">' + index + ':' + str(row[index]) + '</p>'
                    elif row[index] > 0:
                        action += '<p style="color:red">' + index + ':' + str(row[index]) + '</p>'
            # else:
            #     action_signal.action = 0

            action_signal.save()
        sm("操作指令", action, self.receiver, self.msg_cc)
