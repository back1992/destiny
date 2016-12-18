# -*- coding: utf-8 -*-
import pandas as pd
from myapp.models import *
from destiny.items import *
from scrapy.utils.project import get_project_settings
from destiny.sm2 import sm

from destiny.signal import *
import talib
from talib.abstract import *
import numpy as np

# from talib.abstract import *

settings = get_project_settings()


class PriceDailySignalSpider(scrapy.Spider):
    name = "price_daily_signal"
    allowed_domains = ["baidu.com"]
    start_urls = (
        'http://www.baidu.com/',
    )
    custom_settings = {
        'ITEM_PIPELINES': {
            # 'destiny.pipelines.InvestingCCIPipeline': 100
        },

    }

    def __init__(self, msg_cc='', *args, **kwargs):
        # self.msg_cc = "280037713@qq.com"
        self.receiver = "13261871395@163.com"
        self.msg_cc = ""

        super(scrapy.Spider, self).__init__(*args, **kwargs)

    def parse(self, response):
        Signal.objects.all().delete()
        codes = Codeset.objects.filter(actived=True)
        # codes = Codeset.objects.filter(codeen='A')
        for code in codes:
            qs = Price.objects.filter(code=code).order_by('date')
            df = qs.to_dataframe(index='date')
            macd = self.get_macd(df)
            kdj = self.get_kdj(df)
            rsi = self.get_rsi(df)
            signal = Signal()
            signal.code = code
            signal.macd = sum(macd.values())
            signal.kdj = sum(kdj.values())
            signal.rsi = sum(rsi.values())
            signal.save()
        signal_msg = self.send_signal()
        sm("最新版内盘信号", signal_msg, self.receiver, self.msg_cc)

    def get_macd(self, df):
        spur = turn = hist = 0
        dif, dea, macd = talib.MACD(df['close'].values, fastperiod=12, slowperiod=26,
                                    signalperiod=9)
        # print(dif, dea, macd)
        #  1. DIFF、DEA均为正，DIFF向上突破DEA，买入信号。 2. DIFF、DEA均为负，DIFF向下跌破DEA，卖出信号。
        # DIF上穿DEA
        if dif[-2] > 0 and dea[-2] > 0:
            if dif[-2] < dea[-2] and dif[-1] > dea[-1]:
                spur = 10

        # dif下穿dea
        if dif[-2] < 0 and dea[-2] < 0:
            if dif[-2] > dea[-2] and dif[-1] < dea[-1]:
                spur = -10

        ma5 = talib.MA(dea, timeperiod=5, matype=0)
        ma10 = talib.MA(dea, timeperiod=10, matype=0)
        ma20 = talib.MA(dea, timeperiod=20, matype=0)

        # 3.DEA线与K线发生背离，行情反转信号。
        if df['close'].iloc[-1] >= df['close'].iloc[-2] >= df['close'].iloc[-3]:  # K线上涨
            if ma5[-1] <= ma10[-1] <= ma20[-1]:  # DEA下降
                turn = -1

        if df['close'].iloc[-1] <= df['close'].iloc[-2] <= df['close'].iloc[-3]:  # K线下降
            if ma5[-1] >= ma10[-1] >= ma20[-1]:  # DEA上涨
                turn = 1

        # 4.分析MACD柱状线，由负变正，买入信号。
        if macd[-1] > 0 and macd[-2] < 0:
            hist = 5
        # 由正变负，卖出信号
        if macd[-1] < 0 and macd[-2] > 0:
            hist = -5
        return {'spur': spur, 'turn': turn, 'hist': hist}

    # 通过KDJ判断买入卖出
    def get_kdj(self, df):
        kover = dover = spur = turn = 0
        # 参数9,3,3
        slowk, slowd = talib.STOCH(df['high'].values, df['low'].values, df['close'].values,
                                   fastk_period=9, slowk_period=3, slowk_matype=0, slowd_period=3,
                                   slowd_matype=0)  # K,D

        slow_kma5 = talib.MA(slowk, timeperiod=5, matype=0)
        slow_kma10 = talib.MA(slowk, timeperiod=10, matype=0)
        slow_kma20 = talib.MA(slowk, timeperiod=20, matype=0)
        slow_dma5 = talib.MA(slowd, timeperiod=5, matype=0)
        slow_dma10 = talib.MA(slowd, timeperiod=10, matype=0)
        slow_dma20 = talib.MA(slowd, timeperiod=20, matype=0)
        # 16-17 K,D
        # 1.K线是快速确认线——数值在90以上为超买，数值在10以下为超卖；D大于80时，行情呈现超买现象。D小于20时，行情呈现超卖现象。
        if slowk[-1] >= 90:
            kover = -3
        elif slowk[-1] <= 10:
            kover = 3
        if slowd[-1] >= 80:
            dover = -3
        elif slowd[-1] <= 20:
            dover = 3

        # 2.上涨趋势中，K值大于D值，K线向上突破D线时，为买进信号。#待修改
        if df['close'].iloc[-1] >= df['close'].iloc[-2]:
            if slowk[-1] > slowd[-1] and slowk[-2] < slowd[-2]:
                spur = 10
        # 下跌趋势中，K小于D，K线向下跌破D线时，为卖出信号。#待修改
        if df['close'].iloc[-1] <= df['close'].iloc[-2]:
            if slowk[-1] < slowd[-1] and slowk[-2] > slowd[-2]:
                spur = -10

        # 3.当随机指标与股价出现背离时，一般为转势的信号。
        if df['close'].iloc[-1] >= df['close'].iloc[-2] >= df['close'].iloc[-3]:  # K线上涨
            if (slow_kma5[-1] <= slow_kma10[-1] <= slow_kma20[-1]) or (
                            slow_dma5[-1] <= slow_dma10[-1] <= slow_dma20[-1]):  # K,D下降
                turn = -1
        if df['close'].iloc[-1] <= df['close'].iloc[-2] <= df['close'].iloc[-3]:  # K线下降
            if (slow_kma5[-1] >= slow_kma10[-1] >= slow_kma20[-1]) or (
                            slow_dma5[-1] >= slow_dma10[-1] >= slow_dma20[-1]):  # K,D上涨
                turn = 1

        return {'kover': kover, 'dover': dover, 'spur': spur, 'turn': turn}

    # 通过RSI判断买入卖出
    def get_rsi(self, df):
        over = spur = spur50 = turn = 0
        # 参数14,5
        slowreal = talib.RSI(df['close'].values, timeperiod=14)
        fastreal = talib.RSI(df['close'].values, timeperiod=5)
        slowrealMA5 = talib.MA(slowreal, timeperiod=5, matype=0)
        slowrealMA10 = talib.MA(slowreal, timeperiod=10, matype=0)
        slowrealMA20 = talib.MA(slowreal, timeperiod=20, matype=0)
        fastrealMA5 = talib.MA(fastreal, timeperiod=5, matype=0)
        fastrealMA10 = talib.MA(fastreal, timeperiod=10, matype=0)
        fastrealMA20 = talib.MA(fastreal, timeperiod=20, matype=0)
        # 18-19 慢速real，快速real
        # RSI>80为超买区，RSI<20为超卖区
        if slowreal[-1] > 80 or fastreal[-1] > 80:
            over = -2
        elif slowreal[-1] < 20 or fastreal[-1] < 20:
            over = 2

        # RSI上穿50分界线为买入信号，下破50分界线为卖出信号
        if (slowreal[-2] <= 50 and slowreal[-1] > 50) or (fastreal[-2] <= 50 and fastreal[-1] > 50):
            spur50 = 4
        if (slowreal[-2] >= 50 and slowreal[-1] < 50) or (fastreal[-2] >= 50 and fastreal[-1] < 50):
            spur50 = -4

        # RSI掉头向下为卖出讯号，RSI掉头向上为买入信号
        if df['close'].iloc[-1] >= df['close'].iloc[-2] >= df['close'].iloc[-3]:  # K线上涨
            if (slowrealMA5[-1] <= slowrealMA10[-1] <= slowrealMA20[-1]) or (
                            fastrealMA5[-1] <= fastrealMA10[-1] <= fastrealMA20[-1]):  # RSI下降
                turn = -1
        if df['close'].iloc[-1] <= df['close'].iloc[-2] <= df['close'].iloc[-3]:  # K线下降
            if (slowrealMA5[-1] >= slowrealMA10[-1] >= slowrealMA20[-1]) or (
                            fastrealMA5[-1] >= fastrealMA10[-1] >= fastrealMA20[-1]):  # RSI上涨
                turn = 1

        # 慢速线与快速线比较观察，若两线同向上，升势较强；若两线同向下，跌势较强；若快速线上穿慢速线为买入信号；若快速线下穿慢速线为卖出信号
        if fastreal[-1] > slowreal[-1] and fastreal[-2] <= slowreal[-2]:
            spur = 10
        if fastreal[-1] < slowreal[-1] and fastreal[-2] >= slowreal[-2]:
            spur = -10
        return {'spur': spur, 'spur50': spur50, 'turn': turn, 'over': over}

    def send_signal(self):
        signal = ''
        df = Signal.objects.all().to_dataframe()
        df['signal'] = df['macd'] + df['kdj'] + df['rsi'] + df['cci']
        df = df[df['signal'] != 0].sort_values(by=['signal'], ascending=[-1])
        print(df)
        for index, row in df.iterrows():
            if row['signal'] <= 0:
                signal += '<h3 STYLE="color:green;">做空 ' + row['code'] + '强度：' + str(row['signal'])
                '</h3>'
            else:
                signal += '<h3 STYLE="color:red;">做多 ' + row['code'] + '强度：' + str(row['signal'])
                '</h3>'
            signal += '<p>' + '  macd:' + str(row['macd']) + '  macd:' + str(row['kdj']) + '  kdj:' + str(
                row['macd']) + '  rsi:' + str(row[
                                                  'rsi']) + '  cci:' + \
                      str(row['cci']) + '</p>'
        return signal




        # # 日志记录
        # def Write_Blog(strinput, Dist):
        #     TODAY = datetime.date.today()
        #     CURRENTDAY = TODAY.strftime('%Y-%m-%d')
        #     TIME = time.strftime("%H:%M:%S")
        #     # 写入本地文件
        #     fp = open(Dist + 'blog.txt', 'a')
        #     fp.write('------------------------------\n' + CURRENTDAY + " " + TIME + " " + strinput + '  \n')
        #     fp.close()
        #     time.sleep(1)
        #
        # df = Get_Stock_List()
        # Dist = 'E:\\08 python\\Output\\'
        # df = Get_TA(df, Dist)
        # Output_Csv(df, Dist)
        # time.sleep(1)
        # Close_machine()
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #








        #         print(df)
        #         signal = {}
        #         signal['macd'], signal['kdj'], macd_now, macd_last = signal_macd(df)
        #         signal['cci'] = signal_cci(df)
        #         signal['s60'], signal['mean60'] = signal_mean(df)
        #         print(signal)
        #         signal_msg += '<h3>' + code.codezh + ' ' + code.maincontract + '</h3>'
        #         signal_msg += '<h4>' + str(df.index[-1]) + ' : ' + u'  收盘价: ' + str(df["close"].iloc[-1])
        #         signal_msg += u'---60天均价: ' + str(signal['mean60']) + '\n'
        #         signal_msg += '</h4>\n'
        #         signal_msg += settings.get('SIGNAL')['s60'][signal['s60']] + '\n'
        #         signal_msg += settings.get('SIGNAL')['kdj'][signal['kdj']]
        #         signal_msg += settings.get('SIGNAL')['cci'][signal['cci']]
        # print(signal_msg)
        # sm(u'新版内盘信号', signal_msg, self.receiver, self.msg_cc)
