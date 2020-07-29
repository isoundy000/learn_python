#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/17
import time

from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from poker.entity.dao import gamedata
from poker.entity.configure import gdata
from newfish.entity.msg import GameMsg
from newfish.entity import config, util, change_notify, weakdata
from newfish.entity.lotterypool import poseidon_lottery_pool
from newfish.entity.config import FISH_GAMEID, TOWERIDS
from newfish.player.multiple_player import FishMultiplePlayer
from newfish.room.poseidon_room import Tower
from newfish.entity.redis_keys import GameData, WeakData
from newfish.servers.util.rpc import user_rpc


class FishPoseidonPlayer(FishMultiplePlayer):

    pass