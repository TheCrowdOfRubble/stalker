import unittest
import datetime

test_cases = {
    '1分钟前': '',
    '3分钟前': '',
    '7分钟前': '',
    '30分钟前': '',
    '今天 16:33': datetime.datetime.now().strftime('%Y-%m-%d 16:33:00'),
    '04月26日 21:49': datetime.datetime.now().strftime('%Y-04-26 21:49:00'),
    '2018-07-19 12:25:48': '2018-07-19 12:25:48',
}


class TestTime(unittest.TestCase):
    def test_parse(self):
        pass
