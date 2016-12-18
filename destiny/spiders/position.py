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
        # 'DOWNLOADER_MIDDLEWARES': {
        #     #    'cnblogs.middlewares.MyCustomDownloaderMiddleware': 543,
        #     'destiny.middlewares.RandomUserAgent': 1,
        #     'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
        #     # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        #     'destiny.middlewares.ProxyMiddleware': 100,
        # },
        'USER_AGENTS': [
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
            "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
            "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
        ],

        'COOKIES_ENABLED': False,

        'DOWNLOAD_DELAY': 3,
        'RETRY_TIMES': 5,
    }

    def __init__(self, msg_cc='', *args, **kwargs):
        # self.msg_cc = "280037713@qq.com"
        self.msg_cc = ""
        # self.msg_cc = "linmuhai@sina.com"
        # self.msg_cc = "465613067@qq.com"

        super(scrapy.Spider, self).__init__(*args, **kwargs)

    # def parse(self, response):
    #     # date = Price.objects.aggregate(Max('date'))
    #     # print(date['date__max'])
    #     date = datetime.datetime.today().strftime('%Y-%m-%d')
    #     qs = Codeset.objects.filter(actived=True)
    #     for p in qs:
    #         url = 'http://data.futures.hexun.com/cccj.aspx?sBreed=' + p.sbreed + '&sContract=' + p.maincontract + '&sDate=' + date + '&sRank=2000'
    #         yield scrapy.Request(url, meta={'code': p.codeen, 'date': date, 'url': url},
    #                              callback=self.parsePage)


    def parse(self, response):
        Position.objects.all().delete()
        qs = Codeset.objects.filter(actived=True)
        dates_in_db = Price.objects.values('date').order_by('-date').distinct()[:60]
        # print(dates_in_db)
        for p in qs:
            for date_in_db in dates_in_db:
                date = date_in_db['date'].strftime('%Y-%m-%d')
                url = 'http://data.futures.hexun.com/cccj.aspx?sBreed=' + p.sbreed + '&sContract=' + p.maincontract + '&sDate=' + date + '&sRank=2000'
                yield scrapy.Request(url, meta={'code': p.codeen, 'date': date, 'url': url},
                                     callback=self.parsePage)

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
