#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


class Reward(object):
    """奖励逻辑
    """
    def __init__(self, user):
        self.user = user
        self.reward = user.reward

