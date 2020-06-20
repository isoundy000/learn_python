#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6


class AchievementTableSystem(object):
    """成就系统"""
    def __init__(self, table, player):
        self.table = table
        self.player = player
        self.achieveTasks = []
        self.holdAssetTasks = []