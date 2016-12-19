# -*- coding: utf-8 -*-

# Scrapy settings for destiny project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
import os

BOT_NAME = 'destiny'

SPIDER_MODULES = ['destiny.spiders']
NEWSPIDER_MODULE = 'destiny.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'destiny (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'destiny.middlewares.DestinySpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'destiny.middlewares.MyCustomDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    'destiny.pipelines.SomePipeline': 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Setting up django's project full path.
import sys
curpath = os.getcwd()
print(curpath)
sys.path.insert(0, curpath + '/myweb')
# Setting up django's settings module name.
os.environ['DJANGO_SETTINGS_MODULE'] = 'myweb.settings'
# import django to load models(otherwise AppRegistryNotReady: Models aren't loaded yet):
import django

django.setup()

SIGNAL = {
    'cci': {
        2: '<span style="color:red;"> cci:买多  </span>',
        -2: '<span style="color:green;"> cci:卖空  </span>',
        0: '',
        1: '<span style="color:red;"> cci:买平  </span>',
        -1: '<span style="color:green;"> cci:卖平  </span>',
    },
    'macd': {
        1: '<span style="color:red;">MACD:buy  </span>',
        0: '',
        -1: '<span style="color:green;">MACD:sell  </span>',
    },
    'kdj': {
        1: '<span style="color:red;">KDJ:buy  </span>',
        0: '',
        -1: '<span style="color:green;">KDJ:sell  </span>',
    },
    's60': {
        2: u'<p style="background-color:red;">均线信号:买入  </p>',
        1: u'<p style="background-color:yellow;">均线信号:追高买多  </p>',
        0: '',
        -1: u'<p style="background-color:darkcyan;">均线信号:加仓卖空  </p>',
        -2: u'<p style="background-color:green;">均线信号:卖空  </p>',
    },
    'cciq': {
        2: u'<p style="background-color:red;">CCI信号:买多  </p>',
        1: u'<p style="background-color:yellow;">CCI信号:买平  </p>',
        0: '',
        -1: u'<p style="background-color:darkcyan;">CCI信号:卖平  </p>',
        -2: u'<p style="background-color:green;">CCI信号:卖空  </p>',
    },
}
