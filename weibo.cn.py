from scrapy import cmdline

if __name__ == '__main__':
    cmdline.execute([
        # 'scrapy', 'crawl', 'm.weibo.cn',
        'scrapy', 'crawl', 'weibo.cn',
    ])
