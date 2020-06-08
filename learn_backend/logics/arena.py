#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


class Arena(object):
    """
    竞技场 - 逻辑部分
    """
    def __init__(self, user):
        self.user = user
        self.arena = user.arena
        self.arena.refresh(user)

    def get_top_20(self, num=20, page=0):
        """
        竞技场 - 获取排行榜
        """


        return []