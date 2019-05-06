from typing import Callable, List, Tuple

from scrapy.http import Request, Response

from stalker.parse.url import WeiboUrl


class FetchItemsAndNext:
    fetch: Callable[[Response], Tuple[List, bool]]

    def __init__(self, fetch: Callable[[Response], Tuple[List, bool]], callback: Callable):
        self.fetch = fetch
        self.callback = callback

    def __call__(self, response: Response):
        items, has_next = self.fetch(response)
        for item in items:
            yield {'user': item}

        url = WeiboUrl(response=response)
        next_url = next(url)

        if has_next and next_url:
            yield Request(
                url=next_url,
                callback=self.callback,
                meta=response.meta,
            )
