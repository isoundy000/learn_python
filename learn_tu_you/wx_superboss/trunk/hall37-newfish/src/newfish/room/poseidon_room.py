#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/11

import functools
import time
from datetime import datetime
from random import choice, randint
from collections import OrderedDict

import freetime.util.log as ftlog
from freetime.util.cron import FTCron
from freetime.entity.msg import MsgPack
from freetime.core.timer import FTLoopTimer
from freetime.util.log import getMethodName
import poker.util.timestamp as pktimestamp
from poker.protocol import router
from poker.entity.biz import bireport
from poker.entity.dao import daobase
from poker.entity.configure import gdata
from poker.entity.game.rooms.normal_room import TYNormalRoom
from hall.entity import hallvip
from newfish.entity import config, util
from newfish.entity.lotterypool import poseidon_lottery_pool
from newfish.entity.redis_keys import MixData
from newfish.entity.config import FISH_GAMEID, ELEC_TOWERID, TOWERIDS
from newfish.servers.table.rpc import table_remote
from newfish.servers.util.rpc import user_rpc
from newfish.entity.quick_start import FishQuickStart


class FishPoseidonRoom(TYNormalRoom):
    """
    捕鱼海皇来袭房间
    """

    def __init__(self, roomDefine):
        pass