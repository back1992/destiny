# -*- coding: utf-8 -*-
import datetime
import numpy
from django.core.cache import cache
import talib
from talib.abstract import *

yesterday = datetime.date.today() - datetime.timedelta(days=1)


def signal(df):
    return {'cci': signal_cci(df), 's60': signal_mean_quandl(df, df.shape[0])}


def signal_investing(df):
    try:
        last_date = df.iloc[-1]['date']
    except:
        print(df)
    result = {}
    # if last_date >= yesterday:
    if True:
        result['last_close'] = df["close"].iloc[-1]
        result['macd'], result['kdj'], macd_now, macd_last = signal_macd(df)
        result['amplitude'] = signal_amplitude(df)
        # cci need volume
        df[df['volume'] == 0] = numpy.nan
        df = df.dropna()
        if not df.empty:
            result['cci'] = signal_cci(df)
            if df.shape[0] >= 61:
                df = df[-61:]
                result['s60'], result['mean60'] = signal_mean(df)
        else:
            result['cci'] = 0
        print(result)
        return result
    else:
        return False


def signal_quandl(df):
    return signal_cci(df)


def signal_investing_5m(df):
    last_date = datetime.datetime.strptime(df.iloc[-1]['date'], '%Y-%m-%d %H:%M:%S').date()
    result = {}
    # if last_date >= yesterday:
    if True:
        result['last_close'] = df["close"].iloc[-1]
        result['macd'], result['kdj'], macd_now, macd_last = signal_macd(df)
        # cci need volume
        df[df['volume'] == 0] = numpy.nan
        result['cci'] = signal_cci(df)
        df = df.dropna()
        if not df.empty and df.shape[0] >= 61:
            df = df[-61:]
            result['s60'], result['mean60'] = signal_mean(df)
        print(result)
        return result
    else:
        return False


def signal_macd(df):
    macd, signal, hist = talib.MACD(df['close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
    macd_now = macd[-1] - signal[-1]
    macd_last = macd[-2] - signal[-2]
    slowk, slowd = talib.STOCH(df['high'].values,
                               df['low'].values,
                               df['close'].values,
                               fastk_period=5,
                               slowk_period=3,
                               slowk_matype=0,
                               slowd_period=3,
                               slowd_matype=0)

    # get the most recent value
    slowk = slowk[-1]
    slowd = slowd[-1]

    # If either the slowk or slowd are less than 10, the stock is
    # 'oversold,' a long position is opened if there are no shares
    # in the portfolio.
    if slowk < 10 or slowd < 10:
        print('buy kdj')
        signalkdj = 1

    # If either the slowk or slowd are larger than 90, the stock is
    # 'overbought' and the position is closed.
    elif slowk > 90 or slowd > 90:
        print('sell kdj')
        signalkdj = -1
    else:
        signalkdj = 0
    if macd_now > macd_last:
        signalmacd = 1
    else:
        signalmacd = -1
    return signalmacd, signalkdj, macd_now, macd_last


def signal_cci(df):
    # calculate CCI
    cci = CCI(df, timeperiod=14)
    if cci.iloc[-1] > 100:
        signalcci = 2
    elif cci.iloc[-1] < -100:
        signalcci = -2
    else:
        if cci.iloc[-2] >= 100:
            signalcci = -1
        elif cci.iloc[-2] < -100:
            signalcci = 1
        else:
            signalcci = 0
    return signalcci


def signal_mean(df):
    # calculate mean60
    volume = mean = price = {}
    df['close_x_volume'] = df.close * df.volume
    # df.loc[:'close_x_volume'] = df.close * df.volume
    volume['whole'] = df["volume"][1:61].sum()
    volume['whole_last'] = df["volume"][0:60].sum()
    mean['60'] = int(df["close_x_volume"][1:61].sum() / volume['whole'])
    mean['60_last'] = int(df["close_x_volume"][0:60].sum() / volume['whole_last'])
    price['last_close'] = df["close"].iloc[-1]
    price['last_close_last'] = df["close"].iloc[-2]
    if price['last_close'] > mean['60']:
        if price['last_close_last'] < mean['60_last']:
            s60 = 2
        else:
            s60 = 1
    else:
        if price['last_close_last'] > mean['60_last']:
            s60 = -2
        else:
            s60 = -1
    return s60, mean['60']


def signal_mean_quandl(df, period=60):
    # calculate mean60

    mean = df[-period:].close.mean()
    price = df["close"].iloc[-1]
    if price > mean:
        s60 = 2
    else:
        s60 = -2
    return s60


def signal_amplitude(df):
    # calculate amplitude use the high price minus lov price every day
    amplitude = {}
    df['amplitude'] = (df.high - df.low) / 2
    df['amplitude'] = df['amplitude'].astype(int)
    amplitude['max'] = df['amplitude'].astype(int).max()
    amplitude['min'] = df['amplitude'].astype(int).min()
    amplitude['mean'] = int(df['amplitude'].mean())
    ratio = df['amplitude'].mean() / df['close'].mean()
    amplitude['ratio'] = "{0:.2f}%".format(ratio * 100)
    return amplitude
