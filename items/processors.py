import urllib.parse
import datetime
import logging
import typing
import re

from scrapy.http.response.html import HtmlResponse
from scrapy.linkextractors import LinkExtractor
from scrapy.loader.processors import TakeFirst
from scrapy.utils.datatypes import MergeDict
from w3lib.html import remove_tags


def strip(text: str) -> str:
    return text.strip()


def remove_invisible_character(text: str, loader_context: MergeDict) -> typing.Union[None, str]:
    cleaned_text = text.strip(' \xa0')  # .replace('\xa0', '')
    if not cleaned_text:
        return None
    return cleaned_text


class GetFirstNumber:
    _find_int_pattern = re.compile(r'\d+')

    def __call__(self, text: str, loader_context: MergeDict) -> str:
        number = ''

        matched = self._find_int_pattern.search(text)
        if matched:
            number_string = matched.group()
            number = number_string

        return number


class GetDictFromProfile:
    _PROFILE_FIELD_CN_TO_EN = {
        "昵称": "nickname",
        "认证": "certification",
        "性别": "gender",
        "地区": "location",
        "生日": "birthday",
        "认证信息": "certification_information",
        "简介": "introduction",
        "性取向": "sexual_orientation",
        "感情状况": "relationship_status",
        "达人": "weibo_expert",

        "手机版": "username",  # 从「手机版:https://weibo.cn/yaochen」中取出 username
    }

    def __call__(self, text: str, loader_context: MergeDict):
        if not text:
            return None

        pairs = text.split(':', 1)  # 「简介:工作事宜请联络经纪人张蕾：runrunlei@126.com 😊」有 bug，所以英文冒号放在前
        if len(pairs) != 2:
            pairs = text.split('：', 1)  # 以防 https: 被割开
            if len(pairs) != 2:
                return None

        key_cn, value = pairs
        key_en = self._PROFILE_FIELD_CN_TO_EN.get(key_cn)
        if not key_en:
            return None

        return {key_en: value}


def get_username_from_user_detail_page_url(text: str):
    url_detail: urllib.parse.ParseResult = urllib.parse.urlparse(text)

    if url_detail.netloc != 'weibo.cn' or url_detail.path.startswith('/u/'):
        return None

    url_path_slice = url_detail.path.split('/', 2)
    if len(url_path_slice) < 2:
        logging.error('GET USERNAME FROM URL FAILED: %s', text)
        return None
    return url_path_slice[1]


class WeiboTimeParser:
    _time_delta = datetime.timedelta(days=1)

    _second_pattern = re.compile(r'\d+(?=秒前)')
    _minute_pattern = re.compile(r'\d+(?=分钟前)')
    _today_pattern = re.compile(r'今天 (\d+):(\d+)')
    _yesterday_pattern = re.compile(r'昨天 (\d+):(\d+)')
    _year_pattern = re.compile(r'(\d+)月(\d+)日 (\d+):(\d+)')
    _full_pattern = re.compile(r'(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})')

    @staticmethod
    def _get_today():
        return datetime.date.today().strftime("%Y-%m-%d %%s:%%s:00")

    def _get_yesterday(self):
        return (datetime.date.today() - self._time_delta).strftime("%Y-%m-%d %%s:%%s:00")

    @staticmethod
    def _get_this_year():
        return datetime.date.today().strftime("%Y-%%s-%%s %%s:%%s:00")

    # 不要弄成 static 的，必须和其他函数同形！
    def _get_time_from_second_pattern(self, matched):
        now = datetime.datetime.now()

        second = int(matched.group(0))
        delta = datetime.timedelta(seconds=second)
        return (now - delta).strftime("%Y-%m-%d %H:%M:%S")

    def _get_time_from_minute_pattern(self, matched):
        now = datetime.datetime.now()

        minute = int(matched.group(0))
        delta = datetime.timedelta(minutes=minute)
        return (now - delta).strftime("%Y-%m-%d %H:%M:%S")

    def _get_time_from_today_pattern(self, matched):
        return self._get_today() % (matched.group(1), matched.group(2))

    def _get_time_from_yesterday_pattern(self, matched):
        return self._get_yesterday() % (matched.group(1), matched.group(2))

    def _get_time_from_year_pattern(self, matched):
        return self._get_this_year() % (matched.group(1), matched.group(2), matched.group(3), matched.group(4))

    def _get_time_from_full_pattern(self, matched):
        return "%s-%s-%s %s:%s:%s" % (
            matched.group(1), matched.group(2), matched.group(3), matched.group(4), matched.group(5), matched.group(6))

    _patterns = {
        _second_pattern: _get_time_from_second_pattern,
        _minute_pattern: _get_time_from_minute_pattern,
        _today_pattern: _get_time_from_today_pattern,
        _yesterday_pattern: _get_time_from_yesterday_pattern,
        _year_pattern: _get_time_from_year_pattern,
        _full_pattern: _get_time_from_full_pattern,
    }

    def __call__(self, raw_datetime_string):
        for pattern in self._patterns:
            matched = pattern.match(raw_datetime_string)
            if matched:
                return self._patterns[pattern](self, matched)

        logging.error("WRONG WEIBO DATE %s", raw_datetime_string)
        return "0000-00-00 00:00:00"


class WeiboContentParser:
    @staticmethod
    def _get_content_from_repost_weibo(text: str) -> str:
        text_slice = text.split('\xa0', 1)  # 当某条微博十分干净，即无组图、无全文、无富媒体时，就会无 \xa0
        return text_slice[0]

    @staticmethod
    def _remove_repost_reason(text: str) -> str:
        return text[5:]

    @staticmethod
    def _remove_pinned_weibo(text: str) -> str:
        if not text.startswith('<div>[<span class="kt">置顶</span>]'):
            return text
        return text[33:]

    def __call__(self, weibo_loader) -> str:
        weibo_id: str = weibo_loader.get_output_value('weibo_id')
        origin_weibo_id: str = weibo_loader.get_output_value('origin_weibo_id')

        if not origin_weibo_id or weibo_id == origin_weibo_id:  # 原创微博
            content = weibo_loader.get_xpath(
                './div[1]',
                TakeFirst(), self._remove_pinned_weibo, remove_tags, self._get_content_from_repost_weibo, strip
            )
        else:  # 转发微博
            content = weibo_loader.get_xpath(
                './div[last()]',
                TakeFirst(), remove_tags, self._get_content_from_repost_weibo, self._remove_repost_reason
            )

        return content


class EmptyTo:
    def __init__(self, target=0):
        self.target = target

    def __call__(self, value, loader_context=None):
        if value:
            return value
        return self.target


class TagsExtractor:
    tags_extractor = LinkExtractor(allow=r'https://m.weibo.cn/search.+q%3D%23.+%23')

    def __call__(self, text):
        response = HtmlResponse(url="", encoding='utf-8', body=text)
        links = self.tags_extractor.extract_links(response)
        return list(map(lambda tag: tag.text[1:-1], links))


# functions
get_first_number = GetFirstNumber()
tags_extractor = TagsExtractor()
get_dict_from_profile = GetDictFromProfile()
get_weibo_content = WeiboContentParser()
parse_weibo_time = WeiboTimeParser()
