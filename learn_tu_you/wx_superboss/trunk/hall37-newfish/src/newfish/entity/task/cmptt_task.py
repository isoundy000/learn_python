#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/16
import random
import time
import copy

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from freetime.core.timer import FTLoopTimer
from newfish.entity.config import FISH_GAMEID, PEARL_KINDID, COUPON_KINDID
from newfish.entity.msg import GameMsg
from newfish.entity import config, util
from newfish.entity.timer import FishTableTimer
from newfish.servers.util.rpc import user_rpc
from newfish.entity import change_notify
from newfish.entity import drop_system
from newfish.entity.chest import chest_system
from newfish.entity.task.table_task_base import TableMatchTask


class CmpttTask(TableMatchTask):
    """
    竞争性任务(夺宝赛)
    """
    def __init__(self, table, taskName, taskInterval):
        super(CmpttTask, self).__init__(table, taskName, taskInterval)
        self._reload()

    def _reload(self):
        pass

    def clear(self):
        pass

    def sendCmpttTaskInfo(self):
        pass