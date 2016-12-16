# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone
from django_pandas.managers import DataFrameManager


class Codeset(models.Model):
    codeen = models.CharField(max_length=200)
    codezh = models.CharField(max_length=200)
    sina = models.CharField(max_length=200, null=True)
    maincontract = models.CharField(max_length=200, null=True)
    sbreed = models.CharField(max_length=200, unique=True)
    # sbreed = models.CharField(max_length=200)
    # market = models.IntegerField()
    SHANGHAI = '1'
    DALIAN = '2'
    ZHENGZHOU = '3'
    ZHONGJIN = '9'
    MARKET_IN_CHOICES = (
        (SHANGHAI, '1'),
        (DALIAN, '2'),
        (ZHENGZHOU, '3'),
        (ZHONGJIN, '9'),
    )
    market = models.CharField(max_length=2,
                              choices=MARKET_IN_CHOICES,
                              )
    hassignal = models.BooleanField(default=False)
    nighttrade = models.BooleanField(default=True)
    hold = models.BooleanField(default=False)
    actived = models.BooleanField(default=True)
    pub_date = models.DateTimeField(default=timezone.now)

    # my_order = models.PositiveIntegerField(default=0, blank=False, null=True)

    # class Meta(object):
    #     ordering = ('my_order',)

    def __str__(self):
        return self.codeen
        # return self.codezh


class Quandlset(models.Model):
    ticker = models.CharField(max_length=20)
    source = models.CharField(max_length=20, default="CHRIS")
    exchange = models.CharField(max_length=10)
    name = models.CharField(max_length=20)
    namezh = models.CharField(max_length=20, null=True)
    months = models.CharField(max_length=20, null=True)
    quandlcode = models.CharField(max_length=20)
    depth = models.PositiveIntegerField(default=1)
    actived = models.BooleanField(default=True)
    pub_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Marketurl(models.Model):
    market = models.IntegerField()
    daily = models.CharField(max_length=200)
    minute = models.CharField(max_length=200)
    pub_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.market)


class Signal(models.Model):
    code = models.ForeignKey("Codeset")
    BUY = '1'
    NONE = '0'
    SELL = '-1'
    ACTION_IN_CHOICES = (
        (BUY, '1'),
        (NONE, '0'),
        (SELL, '-1'),
    )
    trade = models.CharField(max_length=2, choices=ACTION_IN_CHOICES, default=0)
    cci = models.CharField(max_length=2, choices=ACTION_IN_CHOICES, default=0)
    kdj = models.CharField(max_length=2, choices=ACTION_IN_CHOICES, default=0)
    macd = models.CharField(max_length=2, choices=ACTION_IN_CHOICES, default=0)
    strength = models.IntegerField(null=True)
    pub_date = models.DateTimeField(default=timezone.now)
    objects = DataFrameManager()

    def __str__(self):
        return u'%s ' % self.code.codeen


class Investingset(models.Model):
    name = models.CharField(max_length=200)
    namezh = models.CharField(max_length=200, null=True)
    url = models.URLField(null=True)
    category = models.CharField(max_length=200)
    actived = models.BooleanField(default=True)
    pub_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.name)


class Position(models.Model):
    code = models.ForeignKey("Codeset")
    tradeno = models.IntegerField(null=True)
    buyno = models.IntegerField(null=True)
    sellno = models.IntegerField(null=True)
    name = models.CharField(max_length=50)
    buyposition = models.IntegerField(default=0)
    buyvar = models.IntegerField(default=0)
    tradeposition = models.IntegerField(default=0)
    tradevar = models.IntegerField(default=0)
    sellposition = models.IntegerField(default=0)
    sellvar = models.IntegerField(default=0)
    # type = models.CharField(max_length=50)
    date = models.DateField(null=True)
    pub_date = models.DateTimeField(default=timezone.now)
    objects = DataFrameManager()

    def __str__(self):
        return str(self.code.codeen)

    class Meta:
        get_latest_by = "date"


class Price(models.Model):
    code = models.ForeignKey("Codeset")
    date = models.DateField(null=True)
    open = models.FloatField(null=True)
    high = models.FloatField(null=True)
    low = models.FloatField(null=True)
    close = models.FloatField(null=True)
    res = models.IntegerField(null=True)
    resnew = models.IntegerField(null=True)
    volume = models.IntegerField(null=True)
    pub_date = models.DateTimeField(default=timezone.now)
    objects = DataFrameManager()

    def __str__(self):
        return str(self.code.codeen)


class Pricefreq(models.Model):
    code = models.ForeignKey("Codeset")
    open = models.FloatField(null=True)
    high = models.FloatField(null=True)
    low = models.FloatField(null=True)
    lastclose = models.FloatField(null=True)
    buy = models.FloatField(null=True)
    sell = models.FloatField(null=True)
    close = models.FloatField(null=True)
    avg = models.FloatField(null=True)
    settle = models.FloatField(null=True)
    buyvolume = models.IntegerField(null=True)
    sellvolume = models.IntegerField(null=True)
    hold = models.IntegerField(null=True)
    volume = models.IntegerField(null=True)
    pub_date = models.DateTimeField(default=timezone.now)

    def time_seconds(self):
        # return self.pub_date.strftime("%d %b %Y %H:%M:%S")
        return timezone.localtime(self.pub_date).strftime("%m/%d %H:%M:%S")

    time_seconds.admin_order_field = 'timefield'
    time_seconds.short_description = 'Precise Time'
    objects = DataFrameManager()

    def __str__(self):
        return str(self.code.codeen)


class Ladon(models.Model):
    code = models.ForeignKey("Codeset")
    name = models.CharField(max_length=50)
    no = models.IntegerField(null=True)
    tradeno = models.IntegerField(null=True)
    holdvar = models.IntegerField(default=0)
    holdvarstrength = models.FloatField(default=0)
    corelation = models.DecimalField(null=True, decimal_places=2, max_digits=10)
    date = models.DateField(null=True)
    pub_date = models.DateTimeField(default=timezone.now)
    objects = DataFrameManager()

    def __str__(self):
        return str(self.name)


class Proxyip(models.Model):
    ip = models.GenericIPAddressField(null=True)
    port = models.PositiveIntegerField(null=True)
    area = models.CharField(max_length=10, null=True)
    type = models.CharField(max_length=10, null=True)
    speed = models.PositiveIntegerField(null=True)
    checktime = models.CharField(max_length=10, null=True)
