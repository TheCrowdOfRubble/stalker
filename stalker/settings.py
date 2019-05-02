# -*- coding: utf-8 -*-

# Scrapy settings for stalker project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'stalker'

SPIDER_MODULES = ['stalker.spiders']
NEWSPIDER_MODULE = 'stalker.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 128

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.1
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 64
CONCURRENT_REQUESTS_PER_IP = 64

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'stalker.middlewares.StalkerSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'stalker.middlewares.StalkerDownloaderMiddleware': 543,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
    # 'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,

    'stalker.middlewares.BadResponseDropperMiddleware': 50,
    'stalker.middlewares.RandomAccountMiddleware': 100,
    'stalker.middlewares.RandomHttpProxyMiddleware': 110,
    'stalker.middlewares.RandomUserAgentMiddleware': 120,
    # 'scrapy.extensions.closespider.CloseSpider': 500,

    'stalker.middlewares.HTTPLoggerMiddleware': 999,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'stalker.pipelines.PersistencePipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 1
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 10
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 64
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = True

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600
HTTPCACHE_DIR = '/tmp/'
# HTTPCACHE_IGNORE_HTTP_CODES = [500, 501, 502, 503, 504, 403, 404]
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# log
# LOG_ENABLED = False
# LOG_LEVEL = 'INFO'
LOG_LEVEL = 'WARNING'

# DEPTH_LIMIT = 1

# DEPTH_PRIORITY = -1

# CLOSESPIDER_PAGECOUNT = 1000

# Retry when proxies fail
RETRY_TIMES = 3

# Retry on most error codes since proxies fail for different reasons
RETRY_HTTP_CODES = [500, 503, 504, 400, 403, 404, 408, 418]

IGNORE_URLS = [
    'https://passport.weibo.cn',
    'https://login.sina.com.cn',
]

# 每个人的历史微博与微博评论最多翻几页
MAX_PAGE_VISIT = 5

DB_DRIVER = 'MySQLdb'
DB_NAME = 'weibo'
DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = 'rootroot'
DB_CHARSET = 'utf8mb4'
DB_MIN_POOL_SIZE = 50
DB_MAX_POOL_SIZE = 300
DB_USE_UNICODE = True

WEIBO_INSERT_SQL = (
    'INSERT INTO `weiboes` ('
        '`weibo_id`,'
        '`user_id`,'
        '`time`,'
        '`content`,'
        '`repost_amount`,'
        '`comment_amount`,'
        '`like_amount`,'
        '`origin_weibo_id`,'
        '`platform`,'
        '`create_time`,'
        '`modify_time`'
    ') VALUES ('
        '%s,'
        '%s,'
        '%s,'
        '%s,'
        '%s,'
        '%s,'
        '%s,'
        '%s,'
        '%s,'
        'now(),'
        'now()'
    ')'
)

WEIBO_UPDATE_SQL = (
    'UPDATE `weiboes`'
    ' SET '
        '`user_id` = %s,'
        '`time` = %s,'
        '`content` = %s,'
        '`repost_amount` = %s,'
        '`comment_amount` = %s,'
        '`like_amount` = %s,'
        '`origin_weibo_id` = %s,'
        '`platform` = %s,'
        '`modify_time` = now()'
    ' WHERE '
        '`weibo_id` = %s'
)

USER_INSERT_SQL = (
    'INSERT INTO `users` ('
       '`user_id`,'
       '`nickname`,'
       '`username`,'
       '`avatar`,'
       '`weibo_amount`,'
       '`follow_amount`,'
       '`follower_amount`,'
       '`gender`,'
       '`introduction`,'
       '`birthday`,'
       '`certification`,'
       '`certification_information`,'
       '`location`,'
       '`weibo_expert`,'
       '`sexual_orientation`,'
       '`relationship_status`,'
       '`create_time`,'
       '`modify_time`'
    ') VALUES ('
       '%s,'
       '%s,'
       '%s,'
       '%s,'
       '%s,'
       '%s,'
       '%s,'
       '%s,'
       '%s,'
       '%s,'
       '%s,'
       '%s,'
       '%s,'
       '%s,'
       '%s,'
       '%s,'
       'now(),'
       'now()'
    ')'
)

USER_UPDATE_SQL = (
    'UPDATE `users`'
    ' SET '
        '`nickname` = %s,'
        '`username` = %s,'
        '`avatar` = %s,'
        '`weibo_amount` = %s,'
        '`follow_amount` = %s,'
        '`follower_amount` = %s,'
        '`gender` = %s,'
        '`introduction` = %s,'
        '`birthday` = %s,'
        '`certification` = %s,'
        '`certification_information` = %s,'
        '`location` = %s,'
        '`weibo_expert` = %s,'
        '`sexual_orientation` = %s,'
        '`relationship_status` = %s,'
        '`modify_time` = now()'
    ' WHERE '
        '`user_id` = %s'
)
