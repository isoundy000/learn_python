#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from lib.db import ModelBase


class GuildReward(ModelBase):


    def __init__(self, uid=None):
        self.uid = uid
        self._attrs = {
            'gacha': 100
        }