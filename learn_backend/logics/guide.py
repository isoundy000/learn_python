#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import game_config

"""
1: 进入游戏
2: 达到等级
3: 收复建筑
4: 收复关卡
5: 获得卡牌
6: 获得装备
7: 获得道具
"""

# TODO: 剩余的引导

# sort 2
def mark_guide_4_level_up(user, change_lvs=None):
    '''
    引导等级提升 达到等级
    :param user:
    :param change_lvs:
    :return:
    '''
    if change_lvs:
        for k, v in game_config.guide_team.iteritems():
            if v['open_sort'] == 2 and v['open_value'] in change_lvs:
                min_step = min(game_config.guide[k])
                user.user_m.do_guide(k, step=min_step, save=False)