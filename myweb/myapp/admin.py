# -*- coding: utf-8 -*-
from django.contrib import admin
# from adminsortable2.admin import SortableAdminMixin

# Register your models here.
from .models import *


def make_holded(modeladmin, request, queryset):
    queryset.update(hold=True)


make_holded.short_description = "Mark selected code as holded"


def make_unholded(modeladmin, request, queryset):
    queryset.update(hold=False)


def make_actived(modeladmin, request, queryset):
    queryset.update(actived=True)


make_actived.short_description = "Mark selected code as actived"


def make_unactived(modeladmin, request, queryset):
    queryset.update(actived=False)


make_unactived.short_description = "Mark selected code as unactived"


def make_nighttrade(modeladmin, request, queryset):
    queryset.update(nighttrade=True)


make_nighttrade.short_description = "Mark night trade"


def make_unnighttrade(modeladmin, request, queryset):
    queryset.update(nighttrade=False)


make_unnighttrade.short_description = "Mark none night trade"


class CodesetAdmin(admin.ModelAdmin):
    # fieldsets = [
    #     (None, {'fields': ['codeen']}),
    #     (None, {'fields': ['codezh']}),
    #     ('交易市场', {'fields': ['market']}),
    #     ('新浪代码', {'fields': ['sina']}),
    #     ('主力合约', {'fields': ['maincontract']}),
    #     ('Date information', {'fields': ['pub_date']}),
    #     ('持仓', {'fields': ['hold']}),
    #     ('sBreed', {'fields': ['sbreed']}),
    #     ('激活', {'fields': ['actived']}),
    #     ('夜盘', {'fields': ['nighttrade']}),
    # ]
    # list_display = ['codeen', 'codezh', 'market', 'sina', 'maincontract', 'sbreed', 'hold', 'nighttrade', 'actived']
    list_display = [f.name for f in Codeset._meta.fields if f.name != "id" and f.name != "pub_date"]
    # list_filter = (
    #     ('code', admin.RelatedOnlyFieldListFilter),
    # )
    actions = [make_holded, make_unholded, make_nighttrade, make_unnighttrade]


admin.site.register(Codeset, CodesetAdmin)


class MarketurlAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Marketurl._meta.fields if field.name != "id" and field.name != "pub_date"]


admin.site.register(Marketurl, MarketurlAdmin)


class QuandlsetAdmin(admin.ModelAdmin):
    # list_display = ['name', 'namezh', 'symbol', 'exchange', 'actived']
    list_display = [f.name for f in Quandlset._meta.fields if f.name != "id" and f.name != "pub_date"]
    actions = [make_actived, make_unactived]


admin.site.register(Quandlset, QuandlsetAdmin)


class SignalAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Signal._meta.fields if f.name != "id"]


admin.site.register(Signal, SignalAdmin)


class InvestingsetAdmin(admin.ModelAdmin):
    list_display = ['name', 'namezh', 'category', 'url', 'actived']


admin.site.register(Investingset, InvestingsetAdmin)


class PriceAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Price._meta.fields if f.name != "id" and f.name != "pub_date"]
    list_filter = (
        ('code', admin.RelatedOnlyFieldListFilter),
    )


admin.site.register(Price, PriceAdmin)


class Price5mAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Price5m._meta.fields if f.name != "id" and f.name != "pub_date"]
    list_filter = (
        ('code', admin.RelatedOnlyFieldListFilter),
    )


admin.site.register(Price5m, Price5mAdmin)


class PriceFreqAdmin(admin.ModelAdmin):
    # list_display = ['code', 'pub_date', 'open', 'high', 'low', 'close', 'volume']
    list_display = [field.name for field in Pricefreq._meta.fields if field.name != "id" and field.name != "pub_date"]
    list_display.append('time_seconds', )
    list_filter = (
        ('code', admin.RelatedOnlyFieldListFilter),
    )


admin.site.register(Pricefreq, PriceFreqAdmin)


class PriceGlobeAdmin(admin.ModelAdmin):
    # list_display = ['code', 'pub_date', 'open', 'high', 'low', 'close', 'volume']
    list_display = [field.name for field in Priceglobe._meta.fields if
                    field.name != "id" and field.name != "pub_time" and field.name != "code"]
    list_display.append('time_seconds', )
    list_filter = (
        'code',
    )


admin.site.register(Priceglobe, PriceGlobeAdmin)


class PositionAdmin(admin.ModelAdmin):
    list_display = ['code', 'date', 'name', 'tradeno', 'tradeposition', 'tradevar', 'buyno', 'buyposition', 'buyvar',
                    'sellno', 'sellposition', 'sellvar']
    # list_display = ['code', 'date', 'name']
    list_filter = (
        ('code', admin.RelatedOnlyFieldListFilter),
        # ('name', admin.RelatedOnlyFieldListFilter),
    )


admin.site.register(Position, PositionAdmin)


class LadonAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'tradeno', 'holdvar', 'holdvarstrength', 'corelation', 'no', 'date']
    list_filter = (
        ('code', admin.RelatedOnlyFieldListFilter),
    )


admin.site.register(Ladon, LadonAdmin)


class ProxyIPAdmin(admin.ModelAdmin):
    list_display = ['ip', 'port', 'checktime']


admin.site.register(Proxyip, ProxyIPAdmin)
