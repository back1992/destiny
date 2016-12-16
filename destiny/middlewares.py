# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import random
import base64

from scrapy import signals

from myapp.models import Proxyip


class DestinySpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)



class RandomUserAgent(object):
    """Randomly rotate user agents based on a list of predefined ones"""

    def __init__(self, agents):
        self.agents = agents

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist('USER_AGENTS'))

    def process_request(self, request, spider):
        # print "**************************" + random.choice(self.agents)
        request.headers.setdefault('User-Agent', random.choice(self.agents))


class ProxyMiddleware(object):
    def process_request(self, request, spider):
        PROXIES = []
        qs = Proxyip.objects.all()
        for p in qs:
            PROXIES.append({'ip_port': str(p.ip) + ':' + str(p.port), 'user_pass': ''})
            # print(PROXIES)
            proxy = random.choice(PROXIES)
            if proxy['user_pass'] is not None:
                request.meta['proxy'] = "http://%s" % proxy['ip_port']
                encoded_user_pass = base64.b64encode(proxy['user_pass'].encode('utf-8'))
                request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass.decode('utf-8')
                print("**************ProxyMiddleware have pass************" + proxy['ip_port'])
            else:
                print("**************ProxyMiddleware no pass************" + proxy['ip_port'])
                request.meta['proxy'] = "http://%s" % proxy['ip_port']
                print("**************ProxyMiddleware no pass************")