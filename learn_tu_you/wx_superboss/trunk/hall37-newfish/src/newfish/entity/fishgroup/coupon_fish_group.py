#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/2

import time
import random

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from poker.entity.dao import gamedata
from hall.entity import hallvip
from newfish.entity import config, util
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData
from newfish.entity.event import EnterTableEvent, LeaveTableEvent


class CouponFishGroup(object):
    """
    奖券鱼鱼群
    """
    def __init__(self, table):
        self.table = table
        self._lastUtilAppearTime = int(time.time())
        pass