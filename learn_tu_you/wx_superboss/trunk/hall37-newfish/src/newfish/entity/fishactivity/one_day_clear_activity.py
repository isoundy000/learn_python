#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/4
"""
目前： 招财赢大奖
"""
from freetime.util import log as ftlog
from newfish.entity.fishactivity.fish_activity import ActivityState, ActivityType
from newfish.entity.fishactivity.front_task_activity import FrontTaskActivity
from newfish.entity import util, weakdata
from newfish.entity import config


class OneDayClearActivity(FrontTaskActivity):
    """
    招财赢大奖（ActivityType：30）
    """

    def _initData(self, userId, activityId, inTable):
        super(OneDayClearActivity, self)._initData(userId, activityId, inTable)
        self.isCleared = weakdata.getDayFishData(userId, activityId, 0)
        if self.isCleared == 0:
            ftlog.debug("OneDayClearActivity_initData")
            self.isCleared = 1
            weakdata.setDayFishData(self.userId, self.activityId, 1)
        if self.activityType == ActivityType.OneDayClearAc:
            self.timeDesc = " "
        else:
            if self.activityConfig["effectiveTime"]:
                self.timeDesc = config.getMultiLangTextConf("ID_ACTIVITY_TIME_DESC_2", lang=self.lang) % \
                                (self.getTimeDescStr(self.activityConfig["effectiveTime"]["start"]),
                                self.getTimeDescStr(self.activityConfig["effectiveTime"]["end"]))
            else:
                self.timeDesc = " "