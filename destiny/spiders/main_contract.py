# -*- coding: utf-8 -*-
import re
import scrapy
from destiny.items import *
from myapp.models import Codeset, Price, Position
from destiny.sm2 import sm


class MainContractSpider(scrapy.Spider):
    name = "main_contract"
    allowed_domains = ["vip.stock.finance.sina.com.cn"]
    start_urls = (
        # 'http://quote.futures.hexun.com/price.aspx?market=all&type=zhuli',
        'http://vip.stock.finance.sina.com.cn/quotes_service/view/js/qihuohangqing.js',
        # 'http://quote.futures.hexun.com/EmbPrice.aspx?market=3&type=all',
    )

    def __init__(self, msg_cc='', *args, **kwargs):
        self.receiver = "13261871395@163.com"

        super(scrapy.Spider, self).__init__(*args, **kwargs)

    def parse(self, response):
        qs = Codeset.objects.all()
        for code in qs:
            url = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQFuturesData?page=1&num=5&sort=position&asc=0&node=' + code.sina + '&base=futures'
            yield scrapy.Request(url, meta={'code': code}, callback=self.parsePage)

    def parsePage(self, response):
        text = response.body.decode("gbk")
        try:
            m = re.findall("symbol\:\"([A-Z]+\d+)\"", text, re.MULTILINE)
            code = response.meta['code']
            if m[0].endswith('0'):
                code.maincontract = m[1]
            else:
                code.maincontract = m[0]
            code.save()
            # sm(code.codezh + " 主力合约调整为： " + maincontract, '', self.receiver, self.msg_cc)
            # print(m[1])
        except:
            print(response.meta['code'], 'error')
