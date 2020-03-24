#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import new
import time
import copy
import weakref
import random
import game_config

from lib.utils import merge_dict
from lib.utils.debug import print_log






def map_battle_user(fight_id, fight_config, sort=1):
    """# battle_user: docstring
    args:
        user_config:    ---    arg
    returns:
        0    ---
    """
    if sort == 1:
        enemy_config = game_config.enemy_all
    else:
        enemy_config = game_config.afterlife_enemy