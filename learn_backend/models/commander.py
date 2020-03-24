#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import random
import game_config
import settings

from lib.db import ModelBase
from lib.utils import generate_rank_score


def lv_num_to_score(lv, num=1):
    '''
    等级数转积分
    :param lv:
    :param num:
    :return:
    '''
    return lv * 10000 + num


def score_to_lv_num(score):
    '''
    积分转等级和道具数量
    :param score:
    :return:
    '''
    lv, item_num = divmod(score, 10000)
    return lv, item_num


class Commander(ModelBase):
    """
    统帅技能
    """

    ROB_LEVEL_RANGE = 20
    ATTRS_MAPPINGS = {
        1: 'patk',
        2: 'matk',
        3: 'def',
        4: 'speed',
        5: 'hp',
        6: 'hp2',
        7: 'hp3',
        8: 'firedfs',
        9: 'waterdfs',
        10: 'winddfs',
        11: 'earthdfs',
        201: 'fire',
        202: 'water',
        203: 'wind',
        204: 'earth',
        301: 'fire_dfs',
        302: 'water_dfs',
        303: 'wind_dfs',
        304: 'earth_dfs',
    }

    def __init__(self, uid):
        """
        初始化
        """
        self.uid = uid
        self._attrs = {
            'attrs': {},
            'super_commander': {}
        }
        for attr in self.ATTRS_MAPPINGS.values():
            self._attrs['attrs'][attr] = {'lv': 0, 'exp': 0}

        super(Commander, self).__init__(self.uid)