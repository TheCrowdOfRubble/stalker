import re
import logging

import scrapy

import stalker.items as items
import parser.user.profile_page as profile_parser
import parser.user.detail_page as detail_parser


def parse(response: scrapy.http.Response) -> scrapy.http.Request:
    """
    输入用户详情页的响应，返回用户资料页的请求，最终异步生成 UserItem
    :param response: 用户详情页的响应
    :return: 用户资料页的请求
    """
    user_item = items.UserItem()
    user_item.set_all()
    response.meta['user'] = user_item

    user_item = detail_parser.parse(response)

    # 处理个人资料页
    return scrapy.Request(
        url="https://weibo.cn/%d/info" % user_item["user_id"],
        callback=profile_parser.parse,
        meta={"user": user_item},
        priority=666,  # 用户优先处理
    )


_user_id_pattern = re.compile(r'\/(\d+)\/info')
_user_id_url_pattern = re.compile(r'https://weibo.cn/(\d+)/info')
_username_pattern = re.compile(r'https://weibo.cn/(.+)\??')


def get_username_from_detail_page_url(url: str) -> str:
    """
    从用户详情页的 URL 得到 username
    :param url: https://weibo.cn/milnews https://weibo.cn/u/2960656557
    :return: "milnews" None
    """
    if url.startswith("https://weibo.cn/u/") or url.startswith("https://weibo.cn/n/"):
        username = None
    else:
        username = _username_pattern.match(url).group(1)
    return username


def get_user_id_from_profile_page_url(url: str) -> int:
    """
    从用户资料页的 URL(包括相对的) 得到 user_id
    :param url: https://weibo.cn/2960656557/info
    :return: 2960656557
    """
    if url.startswith('https://weibo.cn/'):
        matched = _user_id_url_pattern.match(url)
    else:
        matched = _user_id_pattern.match(url)
    if not matched:
        logging.error("GET USER_ID FAILED", url)
        return 0
    return int(matched.group(1))


def get_user_id_from_detail_page(response: scrapy.http.Response) -> int:
    """
    从用户详情页的响应中取出 user_id 来
    :param response:
    :return: user_id
    """
    user_profile_page_url = response.css(".ut>a:nth-of-type(2)::attr(href)").get()  # 「资料」超链接
    return get_user_id_from_profile_page_url(user_profile_page_url)
