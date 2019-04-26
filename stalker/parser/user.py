import re

import scrapy

import stalker.items as items
import stalker.utils as utils


def parse(response: scrapy.http.Response) -> scrapy.http.Request:
    """
    生成 UserItem
    :param response:
    :return:
    """
    user_item = items.UserItem()
    user_item.set_all()

    user_item["user_id"] = get_user_id_from_detail_page(response)
    user_item["username"] = _get_username_from_detail_page_url(response.url)
    user_item["avatar"] = response.css(".u img::attr(src)").extract_first("")
    statistics = response.css(".tip2")
    user_item["weibo_amount"] = int(statistics.re_first(r"(?<=微博\[)\d+(?=\])", 0))
    user_item["follow_amount"] = int(statistics.re_first(r"(?<=关注\[)\d+(?=\])", 0))
    user_item["follower_amount"] = int(statistics.re_first(r"(?<=粉丝\[)\d+(?=\])", 0))

    # 处理个人资料页
    return scrapy.Request(
        url="https://weibo.cn/%d/info" % user_item["user_id"],
        callback=_parse_profile_page,
        meta={"user": user_item},
        priority=666,  # 用户优先处理
    )


def _parse_profile_page(response: scrapy.http.Response) -> items.UserItem:
    """
    处理用户资料页
    :param response:
    :return:
    """
    user_item = response.meta['user']
    for profile in response.css(".c")[3].xpath("./text()"):
        key = profile.re_first(r'^.+(?=:|：)', "")
        value = profile.re_first(r'(?<=:|：).+$', "")
        if key == "" or key not in items.PROFILE_FIELD_CN_TO_EN:
            continue
        response.meta['user'][items.PROFILE_FIELD_CN_TO_EN[key]] = value
    return user_item


_user_id_pattern = re.compile(r'\/(\d+)\/info')
_username_pattern = re.compile(r'https://weibo.cn/(.+)\??')


def _get_username_from_detail_page_url(url: str) -> str:
    """
    从个人微博页得到 username
    :param url: https://weibo.cn/milnews https://weibo.cn/u/2960656557
    :return: "milnews" None
    """
    if url.startswith("https://weibo.cn/u/") or url.startswith("https://weibo.cn/n/"):
        username = None
    else:
        username = _username_pattern.match(url).group(1)
    return username


def get_user_id_from_detail_page(response: scrapy.http.Response) -> int:
    """
    从用户详情页的资料URL中取出 user_id 来
    :param response:
    :return: user_id
    """
    user_profile_page_url = response.css(".ut>a:nth-of-type(2)::attr(href)").get()  # 「资料」超链接
    matched = _user_id_pattern.match(user_profile_page_url)
    if not matched:
        utils.perror("GET USER_ID FAILED", user_profile_page_url)
        return 0
    return int(matched.group(1))
