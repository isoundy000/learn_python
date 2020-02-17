#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re

import settings
import game_config
from models.user import UnameUid, UidServer
from logics.user import User


REGIONS_MSG = {
    1: {'name': unicode('IOS正版', 'utf-8'), 'id': '2', 'hasServer': '1'},
    2: {'name': unicode('安卓/IOS越狱', 'utf-8'), 'id': '1', 'hasServer': '1'},
    3: {'name': unicode('dev', 'utf-8'), 'id': '3', 'hasServer': '1'},
    4: {'name': unicode('test', 'utf-8'), 'id': '4', 'hasServer': '1'},
}


ROELS_RE = {
    1: re.compile('^[a]\d{8,11}$').match,
    2: re.compile('^[g]\d{8,11}$').match,
    3: re.compile('^[agh]\d{8,11}$').match,
    4: re.compile('^[agh]\d{8,11}$').match,
}



def regions(env, *args, **kwargs):
    """ 获取游戏区列表

    :param env:
    :param args:
    :param kwargs:
    :return:
    """
    env_type = kwargs.get('env_type', 2)
    rs = REGIONS_MSG.get(env_type, REGIONS_MSG[2])

    return {'code': '0', 'regions': [rs]}


