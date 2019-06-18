# -*- coding: utf-8 -*-

# Scrapy settings for stalker project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import os

BOT_NAME = 'stalker'

SPIDER_MODULES = ['stalker.spiders']
NEWSPIDER_MODULE = 'stalker.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 77

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.1
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 77
CONCURRENT_REQUESTS_PER_IP = 77

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# LOG
LOG_LEVEL = 'INFO'

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# HTTP Proxy
HTTP_PROXY_URL = 'http://111.231.14.117:15510/'

# 使用代理的几率
CHANCE_OF_USE_PROXY = 37  # N / 100
if os.environ.get('DEV'):
    CHANCE_OF_USE_PROXY = 100

# 最多翻页数
MAX_PAGE_VISIT = 20

# 深度
DEPTH_LIMIT = 10

IGNORE_URLS = [
    'https://passport.weibo.cn',
    'https://login.sina.com.cn',
]

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'stalker.middlewares.StalkerSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'stalker.middlewares.StalkerDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'stalker.pipelines.PersistencePipeline': 298,
    'stalker.pipelines.WeiboItemExportToRedisPipeline': 300,
}
if os.environ.get('DEV'):
    ITEM_PIPELINES = {
        'stalker.pipelines.LoggerPipeline': 300,
    }

# BAD HTTP CODES
BAD_HTTP_CODES = [500, 502, 503, 504, 522, 524, 400, 403, 408, 418]

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
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
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 1800
HTTPCACHE_DIR = '/tmp/'
HTTPCACHE_IGNORE_HTTP_CODES = BAD_HTTP_CODES
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# RETRY
RETRY_HTTP_CODES = BAD_HTTP_CODES
RETRY_TIMES = 5

# Enables scheduling storing requests queue in redis.
# SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# Ensure all spiders share same duplicates filter through redis.
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"  # 由外部控制，整点删除去重 key

# Default requests serializer is pickle, but it can be changed to any module
# with loads and dumps functions. Note that pickle is not compatible between
# python versions.
# Caveat: In python 3.x, the serializer must return strings keys and support
# bytes as values. Because of this reason the json or msgpack module will not
# work by default. In python 2.x there is no such issue and you can use
# 'json' or 'msgpack' as serializers.
# SCHEDULER_SERIALIZER = "scrapy_redis.picklecompat"

# Don't cleanup redis queues, allows to pause/resume crawls.
# SCHEDULER_PERSIST = True

# Schedule requests using a priority queue. (default)
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue'

# Alternative queues.
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.FifoQueue'
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.LifoQueue'

# Max idle time to prevent the spider from being closed when distributed crawling.
# This only works if queue class is SpiderQueue or SpiderStack,
# and may also block the same time when your spider start at the first time (because the queue is empty).
# SCHEDULER_IDLE_BEFORE_CLOSE = 10

# The item pipeline serializes and stores the items in this redis key.
REDIS_ITEMS_KEY = 'weibo:weibo_mq'

# The items serializer is by default ScrapyJSONEncoder. You can use any
# importable path to a callable object.
# REDIS_ITEMS_SERIALIZER = 'json.dumps'

# Specify the host and port to use when connecting to Redis (optional).
# REDIS_HOST = 'localhost'
# REDIS_PORT = 6379

# Specify the full Redis URL for connecting (optional).
# If set, this takes precedence over the REDIS_HOST and REDIS_PORT settings.
REDIS_URL = 'redis://:P@55w0rd!.redis.baronhou@111.231.14.117:63240'

# Custom redis client parameters (i.e.: socket timeout, etc.)
# REDIS_PARAMS  = {}
# Use custom redis client class.
# REDIS_PARAMS['redis_cls'] = 'myproject.RedisClient'

# If True, it uses redis' ``SPOP`` operation. You have to use the ``SADD``
# command to add URLs to the redis queue. This could be useful if you
# want to avoid duplicates in your start urls list and the order of
# processing does not matter.
# REDIS_START_URLS_AS_SET = True # 不需要去重，因为数据库自带查重

# Default start urls key for RedisSpider and RedisCrawlSpider.
# REDIS_START_URLS_KEY = '%(name)s:start_urls'

# Use other encoding than utf-8 for redis.
# REDIS_ENCODING = 'latin1'

# MySQLdb
DB_DRIVER = 'MySQLdb'
DB_NAME = 'weibo'
DB_HOST = '111.231.14.117'
DB_PORT = 43990
DB_USER = 'root'
DB_PASSWORD = 'P@55w0rd!.mysql.baronhou'
DB_CHARSET = 'utf8mb4'
DB_MIN_POOL_SIZE = 1
DB_MAX_POOL_SIZE = 10
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
