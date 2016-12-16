# -*- coding: utf-8 -*-

import scrapy
from destiny.items import *
from destiny.sm import sm

receiver = '13261871395@163.com'


class ProxyIPListSpider(scrapy.Spider):
    name = "proxy_iplist"
    allowed_domains = ["xicidaili.com/"]
    start_urls = (
        'http://www.xicidaili.com/',
    )

    # def parse(self, response):
    #     # trs = response.xpath('//*[@id="ip_list"]/tbody/tr')
    #     trs = response.xpath('//tbody/tr')
    #     for tr in trs:
    #         print(tr.xpath('./td/text()').extarct_first())

    def start_requests(self):  # 作用：生成初始的request
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
        reqs = []  # 定义resqs(空集)

        # for i in range(1, 206):  # 设置变量：页码1到206
        # for i in range(1, 2):  # 设置变量：页码1到206
        url = "http://www.xicidaili.com/nn/%s" % 1
        req = scrapy.Request(url, headers=headers)
        reqs.append(req)  # 生成的request放到resqs中

        return reqs  # 返回reqs

        # def parse(self, response):
        #     table = response.xpath('//table[@id="ip_list"]')[0]
        #     trs = table.xpath('//tr')[1:]  # 去掉标题行
        #     items = []
        #     for tr in trs:
        #         pre_item = ProxyIPItem()
        #         pre_item['ip'] = tr.xpath('td[2]/text()').extract()[0]
        #         pre_item['port'] = tr.xpath('td[3]/text()').extract()[0]
        #         pre_item['position'] = tr.xpath('string(td[4])').extract()[0].strip()
        #         pre_item['type'] = tr.xpath('td[6]/text()').extract()[0]
        #         pre_item['speed'] = tr.xpath('td[7]/div/@title').re('\d+\.\d*')[0]
        #         pre_item['checktime'] = tr.xpath('td[10]/text()').extract()[0]
        #         items.append(pre_item)
        #         print(pre_item)
        #     return items

    def parse(self, response):
        Proxyip.objects.all().delete()
        # 提取每一行的xpath位置
        ip_list = response.xpath('//table[@id="ip_list"]')  # ip_list=xpath提取（table标签下的"ip_list"属性）

        trs = ip_list[0].xpath('tr')  # 变量trs=ip_list加入tr标签

        items = []  # 定义items空集

        for ip in trs[1:11]:  # ip的tr从[1以后开始]
            ip_address = ip.xpath('./td[2]/text()').extract_first()
            port = ip.xpath('./td[3]/text()').extract_first()
            checktime = ip.xpath('./td[10]/text()').extract_first()
            print(ip_address, port)
            ip_proxy = Proxyip()
            ip_proxy.ip = ip_address
            ip_proxy.port = port
            ip_proxy.checktime = checktime
            ip_proxy.save()

            # tds = ip.xpath('./td')
            # for td in tds:
            #     print(td.xpath('./text()').extract_first())
