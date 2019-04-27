import scrapy

import stalker.items as items
from stalker.parser.user import get_user_id_from_detail_page, get_username_from_detail_page_url


def parse(response: scrapy.http.Response) -> items.UserItem:
    user_item = response.meta['user']

    user_item["user_id"] = get_user_id_from_detail_page(response)
    user_item["username"] = get_username_from_detail_page_url(response.url)
    user_item["avatar"] = response.css(".u img::attr(src)").extract_first("")
    statistics = response.css(".tip2")
    user_item["weibo_amount"] = int(statistics.re_first(r"(?<=微博\[)\d+(?=\])", 0))
    user_item["follow_amount"] = int(statistics.re_first(r"(?<=关注\[)\d+(?=\])", 0))
    user_item["follower_amount"] = int(statistics.re_first(r"(?<=粉丝\[)\d+(?=\])", 0))

    return user_item
