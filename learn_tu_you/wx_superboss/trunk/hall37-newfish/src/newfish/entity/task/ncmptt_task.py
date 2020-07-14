#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/13

import random
import time
import copy

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from newfish.entity.config import FISH_GAMEID
from newfish.entity.msg import GameMsg
from newfish.entity import config
from newfish.entity import util
from newfish.entity.timer import FishTableTimer
from newfish.entity import change_notify
from newfish.entity import drop_system
from newfish.entity.chest import chest_system
from newfish.entity.task.table_task_base import TableMatchTask, TaskState


class NcmpttTask(TableMatchTask):
    """
    非竞争性任务(限时任务)
    """
    def __init__(self, table, taskName, taskInterval):
        super(NcmpttTask, self).__init__(table, taskName, taskInterval)
        self._reload()

    def _reload(self):
        pass





