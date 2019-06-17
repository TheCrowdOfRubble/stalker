from typing import Callable, List, Any, Iterator, Union, Dict

from scrapy.http import Request, Response

from parse.url import WeiboUrl


class FetchItemsAndNext:
    def __init__(
            self,
            fetch_all: Callable[[Response], List],
            parse_single: Callable[[Any], Iterator[Union[Any, bool]]],
            callback: Callable[[Response], Any],
            meta: Dict = None
    ):
        self.fetch_all = fetch_all
        self.callback = callback
        self.parse_single = parse_single
        self.meta = meta

    def __call__(self, response: Response):
        items = self.fetch_all(response)
        for item in items:
            rtns = list(self.parse_single(item))

            for rtn in rtns[:-1]:
                yield rtn

            has_next = rtns[-1]
            if not has_next:
                break
        else:  # 没有遇见中间停住的情况，就读下一页
            url = WeiboUrl(response=response)
            next_url = next(url)

            if next_url:
                yield Request(
                    url=next_url,
                    callback=self.callback,
                    meta=self.meta,
                )
