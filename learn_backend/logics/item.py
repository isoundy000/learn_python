#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import random
import game_config
from lib.utils import weight_choice
from logics.gift import add_gift


class Item(object):

    def __init__(self, user):
        """
        道具类
        """
        self.user = user

    def sell(self, item_id, num):
        pass