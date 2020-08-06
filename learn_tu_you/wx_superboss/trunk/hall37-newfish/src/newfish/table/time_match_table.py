#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/17

import time
import copy
import random
from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from freetime.core.timer import FTLoopTimer
from poker.entity.biz import bireport
from poker.entity.dao import onlinedata
from newfish.room.timematchctrl.utils import Logger
from newfish.table.table_base import FishTable
from newfish.entity.event import CatchEvent, EnterTableEvent
from newfish.player.time_match_player import FishTimeMatchPlayer
from newfish.entity import config, util
from newfish.entity.config import FISH_GAMEID, CHIP_KINDID
from newfish.entity.msg import GameMsg
from newfish.entity.fishgroup.buffer_fish_group import BufferFishGroup
from newfish.entity.fishgroup.multiple_fish_group import MultipleFishGroup



class MatchState:
    DEFAULT = 0
    READY = 1
    START = 2
    END = 3


class FishTimeMatchTable(FishTable):
    pass