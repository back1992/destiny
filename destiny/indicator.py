# -*- coding: utf-8 -*-
import talib


def get_macd(df):
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
def get_kdj(df):
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
def get_rsi(df):
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


# 通过RSI判断买入卖出
def get_cci(df):
    over = spur = turn = 0
    # 参数14  CCI(high, low, close, timeperiod=14)
    cci = talib.CCI(df['high'].values, df['low'].values, df['close'].values, timeperiod=14)
    # 18-19 慢速real，快速real
    # RSI>80为超买区，RSI<20为超卖区
    if cci[-1] < -100:
        over = -10
    elif cci[-1] > 100:
        over = 10
    else:
        if cci[-2] > 100:
            turn = -5
        elif cci[-2] < -100:
            turn = 5

    if cci[-2] > 0 > cci[-1]:
        spur = -1
    elif cci[-2] < 0 < cci[-1]:
        spur = 1

    return {'spur': spur, 'turn': turn, 'over': over}
