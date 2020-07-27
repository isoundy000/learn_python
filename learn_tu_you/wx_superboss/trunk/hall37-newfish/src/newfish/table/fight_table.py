#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/17
import time
import random
import copy

from freetime.util import log as ftlog
from freetime.core.lock import locked
from freetime.entity.msg import MsgPack
from freetime.core.timer import FTLoopTimer
from poker.entity.biz.exceptions import TYBizException
from poker.entity.dao import onlinedata
from poker.entity.dao import userdata
from poker.entity.biz import bireport
from poker.entity.game.tables.table_seat import TYSeat
from hall.entity import hallvip, datachangenotify
from newfish.entity import config
from newfish.entity.config import FISH_GAMEID
from newfish.table.table_base import FishTable
from newfish.entity import util
from newfish.entity.msg import GameMsg
from newfish.player.fight_player import FishFightPlayer
from newfish.entity.event import EnterTableEvent, LeaveTableEvent
from newfish.room.timematchctrl.utils import Logger
from newfish.entity import mail_system, fight_history
from newfish.entity.event import CatchEvent
from newfish.entity.fishactivity import fish_activity_system
from newfish.servers.room.rpc import room_remote




class FishFightTable(FishTable):
    """渔友竞技桌子"""
    pass