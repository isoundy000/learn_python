#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from logics.battle import Battle as zcBattle
from logics.search_treasure import active_data


def start(env):
    """
    this is not only a war
    """
    from logics.user import User as UserL
    tempBattle = zcBattle(UserL['yl'], UserL['zc'])
    return 0, tempBattle.start()


def challenge_info(env):
    """ 挑战信息, 用于前端展示挑战信息面板

    :param env:
    :return:
    """
    data = {
        'search_treasure': active_data(env.user),
    }
    return 0, data