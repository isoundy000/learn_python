#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/4
"""
Created by hhx on 17/6/14.
目前： 回馈赛、宝箱购买
有前置任务的活动
后置任务和前置任务一起的进度相关连（前置任务 完成显示后续任务 前置任务进度减去目标值是后续任务的当前进度）
支持任务重复  （重复任务进度是  总进度减目标值是第二次重复任务时的进度）
"""

import time

from freetime.util import log as ftlog
from newfish.entity.fishactivity.fish_activity import FishActivity, ActivityState, ActivityErrorCode, TaskType
from newfish.entity import util, module_tip, weakdata
from newfish.entity.config import FISH_GAMEID
from newfish.entity.chest import chest_system
from newfish.entity.redis_keys import WeakData


class FrontTaskActivity(FishActivity):

    def _initData(self, userId, activityId, inTable):
        super(FrontTaskActivity, self)._initData(userId, activityId, inTable)
        self.taskReceiveNum = {}