#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import time
import copy

import game_config
from lib.db import ModelBase
from lib.utils import salt_generator


class Gem(ModelBase):

    _need_diff = ('_gem',)

    ATTR_DICT = {
        1: 'patk',
        2: 'matk',
        3: 'def',
        4: 'speed',
        5: 'hp',
        6: 'crit',
        7: 'hr',
        8: 'subhurt',
        9: 'dr',
        201: 'fire',
        202: 'water',
        203: 'wind',
        204: 'earth',
        301: 'fire_dfs',
        302: 'water_dfs',
        303: 'wind_dfs',
        304: 'earth_dfs',
    }

    def __init__(self, uid=None):
        pass