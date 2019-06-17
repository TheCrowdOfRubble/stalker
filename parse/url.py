from typing import Dict, Union
from urllib.parse import ParseResult, urlparse, parse_qsl, urlencode
import logging

from scrapy.http import Response

from utils import settings
from utils import get_page_amount


class WeiboUrl:
    parse_result: ParseResult
    query: Dict
    max_page: int

    def __init__(self, url: str = '', response: Response = None) -> type(None):
        if not url and not response:
            logging.critical('NO URL AND NO RESPONSE')
            return
        elif not url:  # url 优先级比 response 高
            url = response.url

        self.parse_result = urlparse(url)
        self.query = dict(parse_qsl(self.parse_result.query, keep_blank_values=True))
        self.max_page = settings['MAX_PAGE_VISIT']
        if response:
            self.max_page = min(get_page_amount(response), self.max_page)

        if 'page' not in self.query:
            self.query['page'] = 1
        else:
            self.query['page'] = int(self.query['page'])
            if self.query['page'] < 1:
                self.query['page'] = 1

    def get_page_id(self) -> int:
        return self.query['page']

    def __next__(self) -> Union[str, type(None)]:
        self.query['page'] += 1
        if self.query['page'] > self.max_page:  # [1, max_page]
            return None

        url_components = ParseResult(
            scheme=self.parse_result.scheme,
            netloc=self.parse_result.netloc,
            path=self.parse_result.path,
            params=None,
            query=urlencode(self.query),
            fragment=self.parse_result.fragment,
        )

        return url_components.geturl()
