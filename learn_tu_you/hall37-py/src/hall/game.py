#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/22
import json

from freetime.entity.msg import MsgPack
from poker.entity.biz import bireport
from poker.entity.configure import gdata
from poker.entity.dao import userdata, gamedata
from poker.entity.events.tyevent import EventHeartBeat, ChargeNotifyEvent
from poker.entity.events.tyeventbus import globalEventBus
from poker.entity.game.game import TYGame
from poker.protocol import router
from poker.util import strutil

import freetime.util.log as ftlog
import hall.client_ver_judge as client_ver_judge
from hall.entity import hallmoduledefault, halllocalnotification, hall_third_sdk_switch, \
    halldomains, hall_game_update, hall_login_reward, hall_item_exchange, hall_friend_table, \
    hall_statics, hall_joinfriendgame, hall_jiguang_jpush, hall_robot_user
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.todotask import TodoTaskIssueStartChip
import poker.util.timestamp as pktimestamp


class TGHall(TYGame):
    pass