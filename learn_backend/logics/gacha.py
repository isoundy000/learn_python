#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import random
import time
import bisect
import itertools

import game_config
from lib.utils import real_rand
from lib.utils import weight_choice
from logics.gift import add_gift
from models.guild_gvg import GuildReward
from lib.utils import generate_rank_score
from return_msg_config import i18n_msg


class Gacha(object):
    """
    gacha logic class
    """
    def __init__(self, user, g_id):
        self.g_id = int(g_id)
        self.user = user
        self.good_item_cards = []

