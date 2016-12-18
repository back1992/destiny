# -*- coding: utf-8 -*-
import pandas as pd
from myapp.models import *
from destiny.items import *
from scrapy.utils.project import get_project_settings
from destiny.sm2 import sm

from destiny.signal import *
import talib as ta
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
        signal_msg = ''
        codes = Codeset.objects.filter(actived=True)
        # codesxz  = ['FG', ]
        for code in codes[:3]:
            qs = Price.objects.filter(code=code).order_by('date')[:61]
            if not qs or len(qs) < 61:
                print(code, 'error')
            else:
                df = qs.to_dataframe(index='date')

                operate_array1 = []
                operate_array2 = []
                operate_array3 = []

                try:
                    operate1 = self.get_macd(df)
                    operate2 = self.get_kdj(df)
                    operate3 = self.get_rsi(df)
                    operate_array1.append(operate1)  # round(df.iat[(dflen-1),16],2)
                    operate_array2.append(operate2)
                    operate_array3.append(operate3)
                    df['MACD'] = pd.Series(operate_array1, index=df.index)
                    df['KDJ'] = pd.Series(operate_array2, index=df.index)
                    df['RSI'] = pd.Series(operate_array3, index=df.index)
                    print(df)
                except:
                    print('error')
                    pass

    # 通过MACD判断买入卖出
    def get_macd(df):
        # 参数12,26,9
        macd, macdsignal, macdhist = MACD(df['close'], fastperiod=12, slowperiod=26,
                                          signalperiod=9)

        signal_ma5 = MA(macdsignal, timeperiod=5, matype=0)
        signal_ma10 = MA(macdsignal, timeperiod=10, matype=0)
        signal_ma20 = MA(macdsignal, timeperiod=20, matype=0)
        # 13-15xz  DIFF  DEA  DIFF-DEA
        df['macd'] = pd.Series(macd, index=df.index)  # DIFF
        df['macdsignal'] = pd.Series(macdsignal, index=df.index)  # DEA
        df['macdhist'] = pd.Series(macdhist, index=df.index)  # DIFF-DEA
        print(df)
        dflen = df.shape[0]
        ma_len = len(signal_ma5)
        operate = 0
        # 2个数组 1.DIFF、DEA均为正，DIFF向上突破DEA，买入信号。 2.DIFF、DEA均为负，DIFF向下跌破DEA，卖出信号。
        # 待修改
        if df.iat[(dflen - 1), 13] > df.iat[(dflen - 1), 14] > 0 and df.iat[(dflen - 2), 13] <= df.iat[(dflen - 2), 14]:
            operate += 10  # 买入
        elif df.iat[(dflen - 1), 14] < 0 and df.iat[(dflen - 1), 13] == df.iat[(dflen - 2), 14]:
            operate -= 10  # 卖出

        # 3.DEA线与K线发生背离，行情反转信号。
        if df.iat[(dflen - 1), 7] >= df.iat[(dflen - 1), 8] >= df.iat[(dflen - 1), 9]:  # K线上涨
            if signal_ma5[ma_len - 1] <= signal_ma10[ma_len - 1] <= signal_ma20[ma_len - 1]:  # DEA下降
                operate -= 1
        elif df.iat[(dflen - 1), 7] <= df.iat[(dflen - 1), 8] <= df.iat[(dflen - 1), 9]:  # K线下降
            if signal_ma5[ma_len - 1] >= signal_ma10[ma_len - 1] >= signal_ma20[ma_len - 1]:  # DEA上涨
                operate += 1

        # 4.分析MACD柱状线，由负变正，买入信号。
        if df.iat[(dflen - 1), 15] > 0 and dflen > 30:
            for i in range(1, 26):
                if df.iat[(dflen - 1 - i), 15] <= 0:  #
                    operate += 5
                    break
                    # 由正变负，卖出信号
        if df.iat[(dflen - 1), 15] < 0 and dflen > 30:
            for i in range(1, 26):
                if df.iat[(dflen - 1 - i), 15] >= 0:  #
                    operate -= 5
                    break

        return operate

    # 通过KDJ判断买入卖出
    def get_kdj(df):
        # 参数9,3,3
        slowk, slowd = ta.STOCH(np.array(df['high']), np.array(df['low']), np.array(df['close']),
                                fastk_period=9, slowk_period=3, slowk_matype=0, slowd_period=3,
                                slowd_matype=0)

        slow_kma5 = ta.MA(slowk, timeperiod=5, matype=0)
        slow_kma10 = ta.MA(slowk, timeperiod=10, matype=0)
        slow_kma20 = ta.MA(slowk, timeperiod=20, matype=0)
        slow_dma5 = ta.MA(slowd, timeperiod=5, matype=0)
        slow_dma10 = ta.MA(slowd, timeperiod=10, matype=0)
        slow_dma20 = ta.MA(slowd, timeperiod=20, matype=0)
        # 16-17 K,D
        df['slowk'] = pd.Series(slowk, index=df.index)  # K
        df['slowd'] = pd.Series(slowd, index=df.index)  # D
        dflen = df.shape[0]
        ma_len = len(slow_kma5)
        operate = 0
        # 1.K线是快速确认线——数值在90以上为超买，数值在10以下为超卖；D大于80时，行情呈现超买现象。D小于20时，行情呈现超卖现象。
        if df.iat[(dflen - 1), 16] >= 90:
            operate -= 3
        elif df.iat[(dflen - 1), 16] <= 10:
            operate += 3

        if df.iat[(dflen - 1), 17] >= 80:
            operate -= 3
        elif df.iat[(dflen - 1), 17] <= 20:
            operate += 3

        # 2.上涨趋势中，K值大于D值，K线向上突破D线时，为买进信号。#待修改
        if df.iat[(dflen - 1), 16] > df.iat[(dflen - 1), 17] and df.iat[(dflen - 2), 16] <= df.iat[
            (dflen - 2), 17]:
            operate += 10
        # 下跌趋势中，K小于D，K线向下跌破D线时，为卖出信号。#待修改
        elif df.iat[(dflen - 1), 16] < df.iat[(dflen - 1), 17] and df.iat[(dflen - 2), 16] >= df.iat[
            (dflen - 2), 17]:
            operate -= 10

        # 3.当随机指标与股价出现背离时，一般为转势的信号。
        if df.iat[(dflen - 1), 7] >= df.iat[(dflen - 1), 8] >= df.iat[(dflen - 1), 9]:  # K线上涨
            if (slow_kma5[ma_len - 1] <= slow_kma10[ma_len - 1] <= slow_kma20[ma_len - 1]) or (
                            slow_dma5[ma_len - 1] <= slow_dma10[ma_len - 1] <= slow_dma20[ma_len - 1]):  # K,D下降
                operate -= 1
        elif df.iat[(dflen - 1), 7] <= df.iat[(dflen - 1), 8] <= df.iat[(dflen - 1), 9]:  # K线下降
            if (slow_kma5[ma_len - 1] >= slow_kma10[ma_len - 1] >= slow_kma20[ma_len - 1]) or (
                            slow_dma5[ma_len - 1] >= slow_dma10[ma_len - 1] >= slow_dma20[ma_len - 1]):  # K,D上涨
                operate += 1

        return operate

    # 通过RSI判断买入卖出
    def get_rsi(df):
        # 参数14,5
        slowreal = ta.RSI(np.array(df['close']), timeperiod=14)
        fastreal = ta.RSI(np.array(df['close']), timeperiod=5)
        slowrealMA5 = ta.MA(slowreal, timeperiod=5, matype=0)
        slowrealMA10 = ta.MA(slowreal, timeperiod=10, matype=0)
        slowrealMA20 = ta.MA(slowreal, timeperiod=20, matype=0)
        fastrealMA5 = ta.MA(fastreal, timeperiod=5, matype=0)
        fastrealMA10 = ta.MA(fastreal, timeperiod=10, matype=0)
        fastrealMA20 = ta.MA(fastreal, timeperiod=20, matype=0)
        # 18-19 慢速real，快速real
        df['slowreal'] = pd.Series(slowreal, index=df.index)  # 慢速real 18
        df['fastreal'] = pd.Series(fastreal, index=df.index)  # 快速real 19
        dflen = df.shape[0]
        ma_len = len(slowrealMA5)
        operate = 0
        # RSI>80为超买区，RSI<20为超卖区
        if df.iat[(dflen - 1), 18] > 80 or df.iat[(dflen - 1), 19] > 80:
            operate -= 2
        elif df.iat[(dflen - 1), 18] < 20 or df.iat[(dflen - 1), 19] < 20:
            operate += 2

        # RSI上穿50分界线为买入信号，下破50分界线为卖出信号
        if (df.iat[(dflen - 2), 18] <= 50 and df.iat[(dflen - 1), 18] > 50) or (
                        df.iat[(dflen - 2), 19] <= 50 and df.iat[(dflen - 1), 19] > 50):
            operate += 4
        elif (df.iat[(dflen - 2), 18] >= 50 and df.iat[(dflen - 1), 18] < 50) or (
                        df.iat[(dflen - 2), 19] >= 50 and df.iat[(dflen - 1), 19] < 50):
            operate -= 4

        # RSI掉头向下为卖出讯号，RSI掉头向上为买入信号
        if df.iat[(dflen - 1), 7] >= df.iat[(dflen - 1), 8] >= df.iat[(dflen - 1), 9]:  # K线上涨
            if (slowrealMA5[ma_len - 1] <= slowrealMA10[ma_len - 1] <= slowrealMA20[ma_len - 1]) or (
                            fastrealMA5[ma_len - 1] <= fastrealMA10[ma_len - 1] <= fastrealMA20[ma_len - 1]):  # RSI下降
                operate -= 1
        elif df.iat[(dflen - 1), 7] <= df.iat[(dflen - 1), 8] <= df.iat[(dflen - 1), 9]:  # K线下降
            if (slowrealMA5[ma_len - 1] >= slowrealMA10[ma_len - 1] >= slowrealMA20[ma_len - 1]) or (
                            fastrealMA5[ma_len - 1] >= fastrealMA10[ma_len - 1] >= fastrealMA20[ma_len - 1]):  # RSI上涨
                operate += 1

        # 慢速线与快速线比较观察，若两线同向上，升势较强；若两线同向下，跌势较强；若快速线上穿慢速线为买入信号；若快速线下穿慢速线为卖出信号
        if df.iat[(dflen - 1), 19] > df.iat[(dflen - 1), 18] and df.iat[(dflen - 2), 19] <= df.iat[
            (dflen - 2), 18]:
            operate += 10
        elif df.iat[(dflen - 1), 19] < df.iat[(dflen - 1), 18] and df.iat[(dflen - 2), 19] >= df.iat[
            (dflen - 2), 18]:
            operate -= 10
        return operate



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
