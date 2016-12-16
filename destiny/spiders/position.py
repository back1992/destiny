# -*- coding: utf-8 -*-
import datetime
import scrapy
from destiny.items import *
from myapp.models import Codeset, Price, Position



class PositionSpider(scrapy.Spider):
    name = "position"
    allowed_domains = ["hexun.com"]
    start_urls = (
        'http://data.futures.hexun.com/',
    )

    custom_settings = {
        'ITEM_PIPELINES': {
            'destiny.pipelines.PositionListPipeline': 100,
        },
        'EXTENSIONS': {
            # 'destiny.extensions.SpiderOpenCloseLogging': 500,
        },
        # 'DEFAULT_REQUEST_HEADERS': {
        #     'Referer': 'http://localhost:8000'
        # }
    }

    def __init__(self, msg_cc='', *args, **kwargs):
        # self.msg_cc = "280037713@qq.com"
        self.msg_cc = ""
        # self.msg_cc = "linmuhai@sina.com"
        # self.msg_cc = "465613067@qq.com"

        super(scrapy.Spider, self).__init__(*args, **kwargs)

    def parse(self, response):
        # date = Price.objects.aggregate(Max('date'))
        # print(date['date__max'])
        date = datetime.datetime.today().strftime('%Y-%m-%d')
        qs = Codeset.objects.filter(actived=True)
        for p in qs:
            url = 'http://data.futures.hexun.com/cccj.aspx?sBreed=' + p.sbreed + '&sContract=' + p.maincontract + '&sDate=' + date + '&sRank=2000'
            yield scrapy.Request(url, meta={'code': p.codeen, 'date': date, 'url': url},
                                 callback=self.parsePage)

    #
    # def parse(self, response):
    #     Position.objects.all().delete()
    #     qs = Codeset.objects.filter(actived=True)
    #     dates_in_db = Price.objects.values('date').order_by('-date').distinct()[:60]
    #     # print(dates_in_db)
    #     for p in qs:
    #         for date_in_db in dates_in_db:
    #             date = date_in_db['date'].strftime('%Y-%m-%d')
    #             url = 'http://data.futures.hexun.com/cccj.aspx?sBreed=' + p.sbreed + '&sContract=' + p.maincontract + '&sDate=' + date + '&sRank=2000'
    #             yield scrapy.Request(url, meta={'code': p.codeen, 'date': date, 'url': url},
    #                                  callback=self.parsePage)

    def parsePage(self, response):
        tables = response.xpath('//table[@class="dou_table"]')
        types = {'0': 'trade', '1': 'buy', '2': 'sell'}
        for typeindex, typevalue in types.items():
            for tr in tables[int(typeindex)].xpath('./tr')[1:]:
                tds = tr.xpath('./td')
                code = Codeset.objects.get(codeen=response.meta['code'])
                date = response.meta['date']
                name = tds[1].xpath('./div/a/text()').extract_first()
                p, created = Position.objects.update_or_create(code=code, name=name, date=date)
                setattr(p, typevalue + 'no', tds[0].xpath('./text()').extract_first())
                setattr(p, typevalue + 'position', tds[2].xpath('./text()').extract_first())
                setattr(p, typevalue + 'var', tds[3].xpath('./text()').extract_first())
                p.save()
        date = response.meta['date']
        code = response.meta['code']

        page_index = response.xpath('//*[@id="mainbox"]/div[3]/div[15]/strong/text()').extract_first()
        if (page_index):
            leadurl = response.meta['url']
            totalpages = page_index.split('/')[1]
            for page in range(1, int(totalpages) + 1):
                url = leadurl + '&page=' + str(page)
                yield scrapy.Request(url, meta={'code': code, 'date': date, 'url': response.meta['url']},
                                     callback=self.parsePage)
