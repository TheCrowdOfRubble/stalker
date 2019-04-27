import scrapy

import stalker.items as items
import parser.user as user_parser


def get_user_detail_page_url(response: scrapy.http.Response) -> str:
    return response.xpath('//div[@class="c"][last()-2]/text()[last()]').re_first(r'(?<=手机版:)https://weibo.cn/.+', '')


def parse(response: scrapy.http.Response) -> str:
    user_item = response.meta['user']

    if user_item['username'] is None:
        user_detail_page_url = get_user_detail_page_url(response)
        user_item['username'] = user_parser.get_username_from_detail_page_url(user_detail_page_url)

    for profile in response.css(".c")[3].xpath("./text()"):
        key = profile.re_first(r'^.+(?=:|：)', "")
        value = profile.re_first(r'(?<=:|：).+$', "")
        if key == "" or key not in items.PROFILE_FIELD_CN_TO_EN:
            continue
        response.meta['user'][items.PROFILE_FIELD_CN_TO_EN[key]] = value
    return user_item
