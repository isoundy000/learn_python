# -*- coding=utf-8 -*-
"""
Created by lichen on 2018/5/17.
"""

import random
import time
from itertools import islice

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from poker.entity.dao import gamedata
from newfish.entity import config
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData
from newfish.entity.task.task_base import TaskType
from newfish.entity.event import EnterTableEvent, LeaveTableEvent, TableTaskStartEvent


class NewbieFishGroup(object):
    """
    新手任务鱼群
    """
    def __init__(self, table):
        self.table = table
        self._generateNumOnce = 1               # 一次生成多少条
        self._normalFishGroupTimer = None       # 普通鱼群的定时器
        self._multipleGroupTimer = None         # 倍率定时器
        self._bombGroupTimer = None             # 炸弹鱼
        self._rainbowGroupTimer = None          # 彩虹鱼
        self._bossGroupTimer = None             # boss鱼
        self._playerCouponTimerDict = {}        # 奖券鱼
        self._playerBossTimerDict = {}          # boss鱼
        self._playerTerrorTimerDict = {}        # 特殊鱼
        self._playerTuitionTimerDict = {}       # 教学鱼
        self._playerSharkTimerDict = {}

        self._registerEvent()
        self._clear()
        self._nextNormalFishGroup()

    def _clear(self):
        pass

    def _clearPlayerTimer(self, userId):
        pass

    def _addNormalFishGroup(self):
        """
        add_group消息默认是下一个鱼阵开始前60s左右发送，每次调用add_group方法耗费时间一般为0.5s以内(包含对象创建和定时器延迟)
        长此以往会导致add_group消息在当前鱼阵结束后没有及时发送，需要修正时间
        """


    def _nextNormalFishGroup(self):
        """添加下一个鱼群"""
        self._addNormalFishGroup()


    def _dealEnterTable(self, event):
        """
        处理进入事件
        """

    def _dealLeaveTable(self, event):
        """
        处理离开事件
        """

    def _dealTableTaskStart(self, event):
        """
        处理渔场任务开始事件
        """


    def _registerEvent(self):
        """
        注册监听事件
        """
        from newfish.game import TGFish
        TGFish.getEventBus().subscribe(EnterTableEvent, self._dealEnterTable)
        TGFish.getEventBus().subscribe(LeaveTableEvent, self._dealLeaveTable)
        TGFish.getEventBus().subscribe(TableTaskStartEvent, self._dealTableTaskStart)