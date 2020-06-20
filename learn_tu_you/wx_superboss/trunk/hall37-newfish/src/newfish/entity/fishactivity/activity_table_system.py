#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/19


class ActivityTableSystem(object):

    def __init__(self, table, player):
        self.table = table
        self.player = player
        self.activityTasks = {}
        self.clientIdNum = 0
        self.acTemp = 0
        self.dayChangeTimer = None
        self._initDayChangeTimer()

    def _initDayChangeTimer(self):
        """
        初始化活动刷新定时器
        """
        if self.dayChangeTimer:
            self.dayChangeTimer.cancel()
            self.dayChangeTimer = None
        leftSeconds = pktimestamp.getCurrentDayLeftSeconds() + random.randint(1, 30)
        self.dayChangeTimer = FTLoopTimer(leftSeconds, 0, self.updateDayChangeAc)
        self.dayChangeTimer.start()