import requests
import transitions


def get_random_proxy():
    return "http://" + requests.get("http://127.0.0.1:5010/get/").content.decode('utf-8')


WEIBO_TYPE = ['开始状态', '无图原创', '复杂微博', '有图原创', '无图转发', '有图转发']

WEIBO_TRANSITIONS = [
    {'trigger': 'is_repost', 'source': '复杂微博', 'dest': '无图转发'},
    {'trigger': 'is_not_repost', 'source': '复杂微博', 'dest': '有图原创'},
]


class WeiboTransitions(object):
    def __init__(self, weibo_item, weibo):
        self.weibo_item = weibo_item
        self.selector = weibo

    def change_state_by_divs(self, count):
        print(count)
        if count == 1:
            self.to_无图原创()
        elif count == 2:
            self.to_复杂微博()
        else:
            self.to_有图转发()


def return_weibo_state_machine(weibo_item, weibo):
    weibo_type_machine = WeiboTransitions(weibo_item, weibo)
    transitions.Machine(weibo_type_machine, states=WEIBO_TYPE, transitions=WEIBO_TRANSITIONS,
                        initial=WEIBO_TYPE[0])
    return weibo_type_machine
