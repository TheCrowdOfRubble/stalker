import os
import glob
import random
import logging

# /run/media/baronhou/Data/Projects/python/a_crowd_of_rubble/stalker/stalker/utils/useragent
_BASE_PATH = os.path.dirname(os.path.realpath(__file__))

_user_agents = []

for ua_file in glob.glob(os.path.join(_BASE_PATH, 'List-of-user-agents', '*.txt')):
    with open(ua_file) as f:
        for line in f:
            line = line.strip(' \n')
            if line == '':
                continue
            _user_agents.append(line)


def get_random_useragent():
    return random.choice(_user_agents)


logging.info("UA加载完毕，共加载UA %d 个" % len(_user_agents))
