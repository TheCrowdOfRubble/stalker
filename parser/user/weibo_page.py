import parser.weibo as weibo_parser


def parse_user_weibo_page(response):
    user_item = response.meta.get('user')
    for weibo in weibo_parser.parse(response, user_item):
        yield weibo
