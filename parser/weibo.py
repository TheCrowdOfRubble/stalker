import urllib.parse

import scrapy

import stalker.items as items
import utils as utils
import parser.time as time_parser
import parser.utils.page_count as page_count_parser
import stalker.settings as settings


def parse(response: scrapy.http.Response, user_item: dict):
    for weibo in response.xpath('//div[@class="c"][@id]'):
        weibo_item = items.WeiboItem()
        weibo_item['user_id'] = user_item['user_id']
        weibo_item['origin_weibo_id'], weibo_item['weibo_id'], weibo_item['content'] = _get_id_and_content(weibo)

        additional = weibo.css('.ct::text')
        weibo_item['time'] = time_parser.parse(additional.re_first(r'.+(?=[\xA0])', utils.get_datetime()))
        weibo_item['platform'] = additional.re_first(r'(?<=来自).+', '')

        statistics = weibo.xpath('.//div[last()]/a/text()')
        weibo_item["repost_amount"] = int(statistics.re_first(r"(?<=赞\[)\d+(?=\])", 0))
        weibo_item["comment_amount"] = int(statistics.re_first(r"(?<=转发\[)\d+(?=\])", 0))
        weibo_item["like_amount"] = int(statistics.re_first(r"(?<=评论\[)\d+(?=\])", 0))

        yield weibo_item

        if weibo_item["repost_amount"] > 0:
            yield scrapy.Request(
                url="https://weibo.cn/repost/" + weibo_item['weibo_id'],
                callback=_parse_weibo_details,
                meta={'random': True}
            )
        if weibo_item["comment_amount"] > 0:
            yield scrapy.Request(
                url="https://weibo.cn/comment/" + weibo_item['weibo_id'],
                callback=_parse_weibo_details,
                meta={'random': True}
            )
        if weibo_item["like_amount"] > 0:
            yield scrapy.Request(
                url="https://weibo.cn/attitude/" + weibo_item['weibo_id'],
                callback=_parse_weibo_details,
                meta={'random': True}
            )


def _get_id_and_content(weibo: scrapy.selector) -> (str, str, str):
    weibo_ids = weibo.xpath('./*/a[@class="cc"]/@href').re(r"(?<=https://weibo.cn/comment/).+(?=\?)", "")

    if len(weibo_ids) == 1:  # 原创微博
        origin_weibo_id = ""
        weibo_id = weibo_ids[0]

        parts = weibo.xpath('./div').css('::text').getall()
        content = _selector_parts_to_string(parts)
    else:  # 转发微博
        origin_weibo_id = weibo_ids[0]
        weibo_id = weibo_ids[1]

        if weibo.xpath("count(.//div)").get() == '2.0':  # 无图转发
            parts = weibo.xpath('./div[2]').css('::text').getall()
        else:  # 有图转发
            parts = weibo.xpath('./div[3]').css('::text').getall()
        content = _selector_parts_to_string(parts[1:])

    return origin_weibo_id, weibo_id, content


def _parse_weibo_details(response):
    _get_more_users(response)  # 处理第一页

    page_count = page_count_parser.parse(response)
    for page in range(2, min(page_count, settings.MAX_PAGE_VISIT)):  # 从第二页开始
        yield scrapy.Request(url=urllib.parse.urljoin(response.url, "?page=%d" % page), callback=_get_more_users)


def _get_more_users(response):
    users = response.xpath(
        "//div[@class='c'][preceding-sibling::div[@class='pms'] and following-sibling::div[@class='pa']]/a[1][not(contains(@href, '/repost/hot') or contains(@href, '/comment/hot'))]/@href").getall()
    for elem in users:
        yield scrapy.Request(url=urllib.parse.urljoin("https://weibo.cn", elem), priority=666)  # 用户优先处理


def _selector_parts_to_string(parts: list) -> str:
    string = ''.join(parts)

    return string[:string.index('\xa0')]
