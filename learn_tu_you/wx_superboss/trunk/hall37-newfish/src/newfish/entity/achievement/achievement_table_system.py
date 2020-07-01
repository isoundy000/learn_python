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

    def _clearTimer(self):
        pass

    # 初始化用户成就任务
    def _initPlayerAchieveTasks(self, userId):
        pass




    def updateStateAndSave(self):
        if ftlog.is_debug():
            ftlog.debug("updateStateAndSave", self.achieveTasks)
        pass

    def refreshAchievementTask(self):
        pass

    def dealLeaveTable(self):
        """
        处理离开桌子
        """
        self.updateStateAndSave()
        self._clearTimer()