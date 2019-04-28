import datetime
import re

import utils

_today = datetime.date.today().strftime("%Y-%m-%d %%s:%%s:00")
_yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d %%s:%%s:00")
_this_year = datetime.date.today().strftime("%Y-%%s-%%s %%s:%%s:00")

_second_pattern = re.compile(r'\d+(?=秒前)')
_minute_pattern = re.compile(r'\d+(?=分钟前)')
_today_pattern = re.compile(r'今天 (\d+):(\d+)')
_yesterday_pattern = re.compile(r'昨天 (\d+):(\d+)')
_year_pattern = re.compile(r'(\d+)月(\d+)日 (\d+):(\d+)')
_full_pattern = re.compile(r'(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})')


def _get_time_from_second_pattern(matched):
    now = datetime.datetime.now()
    second = int(matched.group(0))
    delta = datetime.timedelta(seconds=second)
    return (now - delta).strftime("%Y-%m-%d %H:%M:%S")


def _get_time_from_minute_pattern(matched):
    now = datetime.datetime.now()
    minute = int(matched.group(0))
    delta = datetime.timedelta(minutes=minute)
    return (now - delta).strftime("%Y-%m-%d %H:%M:%S")


def _get_time_from_today_pattern(matched):
    return _today % (matched.group(1), matched.group(2))


def _get_time_from_yesterday_pattern(matched):
    return _yesterday % (matched.group(1), matched.group(2))


def _get_time_from_year_pattern(matched):
    return _this_year % (matched.group(1), matched.group(2), matched.group(3), matched.group(4))


def _get_time_from_full_pattern(matched):
    return "%s-%s-%s %s:%s:%s" % (matched.group(1), matched.group(2), matched.group(3), matched.group(4), matched.group(5), matched.group(6))


_patterns = {
    _second_pattern: _get_time_from_second_pattern,
    _minute_pattern: _get_time_from_minute_pattern,
    _today_pattern: _get_time_from_today_pattern,
    _yesterday_pattern: _get_time_from_yesterday_pattern,
    _year_pattern: _get_time_from_year_pattern,
    _full_pattern: _get_time_from_full_pattern,
}


def parse(raw_datetime_string):
    for pattern in _patterns:
        matched = pattern.match(raw_datetime_string)
        if matched:
            return _patterns[pattern](matched)
    utils.perror("WRONG WEIBO DATE", raw_datetime_string)
    return "0000-00-00 00:00:00"
