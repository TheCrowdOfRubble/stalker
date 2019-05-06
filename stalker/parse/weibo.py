from scrapy.http import Response

import stalker.items as items


def parse(response: Response):
    user_item = response.meta.get('user_item')
    min_time = response.meta.get('min_time')

    beyond = not bool(min_time)  # 未设置 oldest_weibo_datetime 字段就直接设为 True
    for weibo in response.xpath('//div[@class="c"][contains(@id, "M_")]'):
        weibo_loader = items.WeiboLoader(selector=weibo)

        weibo_loader.add_value('user_id', user_item['user_id'])

        weibo_loader.add_xpath('weibo_id', './@id')

        weibo_loader.add_xpath('time', './div[last()]/span[@class="ct"]/text()')

        weibo_loader.add_xpath('like_amount', './div[last()]/a[last()-3]/text()')
        weibo_loader.add_xpath('repost_amount', './div[last()]/a[last()-2]/text()')
        weibo_loader.add_xpath('comment_amount', './div[last()]/a[last()-1]/text()')

        weibo_loader.add_xpath(
            'origin_weibo_id',
            './*/a[@class="cc"]/@href',
            re=r'(?<=https://weibo.cn/comment/).+(?=\?)'
        )

        weibo_loader.add_value('content', get_weibo_content(weibo_loader))

        weibo_loader.add_xpath('platform', './div[last()]/span[@class="ct"]/text()', re=r'(?<=来自).+')

        weibo_item = weibo_loader.load_item()
        yield weibo_item
