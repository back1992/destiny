# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from django.db.models import F
from django.db.models import Max
from destiny.sm2 import sm

import slackweb
import re
from scrapy.utils.project import get_project_settings
from myapp.models import Codeset, Price, Position

settings = get_project_settings()
slack = slackweb.Slack(url="https://hooks.slack.com/services/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")

TAG_RE = re.compile(r'<[^>]+>')


def remove_tags(text):
    return TAG_RE.sub('', text)


class DestinyPipeline(object):
    def process_item(self, item, spider):
        return item


class PositionListPipeline(object):
    def __init__(self):
        self.name_list = ["永安期货", "混沌天成"]
        self.receiver = "13261871395@163.com"
        try:
            self.last_date = Position.objects.all().aggregate(Max('date'))['date__max']
        except:
            raise ValueError('no position data in db')

    def process_item(self, item, spider):
        pass

    def close_spider(self, spider):
        self.last_date = Position.objects.all().aggregate(Max('date'))['date__max']
        for name in self.name_list:
           self.position_flag(name, self.last_date, spider.msg_cc)

    def position_flag(self, name, date, cc=''):
        signal = ''
        positions = Position.objects.filter(name=name, date=date).annotate(
            hold_interest=F('buyposition') - F('sellposition'),
            hold_var=F('buyvar') - F('sellvar'),
            strength_interest=(F('buyposition') - F('sellposition')) * 100 / (F('buyposition') + F('sellposition')),
            # strength_var=F('hold_var') * 100 / (F('buyposition') + F('sellposition'))
            strength_var=(F('buyvar') - F('sellvar')) * 100 / (F('buyposition') + F('sellposition'))
        ).order_by(
            'strength_interest')
        for p in positions:
            signal += '<h3>' + p.code.codezh + ' ' + p.code.maincontract + '</h3>\n'
            signal += u'<p>多单仓位: ' + str(p.buyposition) + u'  多头排名: ' + str(p.buyno) + u'   仓位变化: ' + str(
                p.buyvar) + '</p>'
            signal += u'<p>空单仓位: ' + str(p.sellposition) + u'  空头排名: ' + str(p.sellno) + u'   仓位变化: ' + str(
                p.sellvar) + '</p>'
            if p.hold_interest > 0:
                signal += u'<p style="color:red;">净多仓位: ' + str(p.hold_interest) + '</p>'
                signal += u'<p style="color:red;">持仓强度 多: ' + str(p.strength_interest) + '</p>'
            else:
                signal += u'<p style="color:green;">净空仓位: ' + str(p.hold_interest) + '</p>'
                signal += u'<p style="color:green;">持仓强度 空: ' + str(p.strength_interest) + '</p>'
            if p.hold_var > 0:
                signal += u'<p style="color:red;">交易方向 多: ' + str(p.hold_var) + '</p>'
                signal += u'<p style="color:red;">交易强度 多: ' + str(p.strength_var) + '</p>'
            else:
                signal += u'<p style="color:green;">交易方向 空: ' + str(p.hold_var) + '</p>'
                signal += u'<p style="color:green;">交易强度 空: ' + str(p.strength_var) + '</p>'
        if signal:
            sm(name + "主力合约持仓指数 " + date.strftime('%Y-%m-%d'), signal, self.receiver, cc)







