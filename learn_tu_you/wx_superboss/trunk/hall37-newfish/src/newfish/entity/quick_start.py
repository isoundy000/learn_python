#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6

import time

from freetime.util import log as ftlog
from freetime.util.log import getMethodName
from poker.entity.game.quick_start import BaseQuickStart
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.dao import onlinedata, userchip, gamedata
from poker.entity.configure import gdata, pokerconf
from poker.entity.game.rooms.room_mixin import TYRoomMixin
from poker.util import strutil
from newfish.entity import config, util, weakdata
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData, WeakData


class FishQuickStartDispatcher(object):
    """
    按clientId分发快速开始请求
    """
    @classmethod
    def dispatchQuickStart(cls, msg, userId, gameId, roomId, tableId, clientId, kindId):
        return FishQuickStart.onCmdQuickStart(msg, userId, gameId, roomId, tableId, clientId, kindId)


class FishQuickStart(BaseQuickStart):
    ENTER_ROOM_REASON_OK = 0
    ENTER_ROOM_REASON_LESS_LEVEL = 1        # 等级过低
    ENTER_ROOM_REASON_INNER_ERROR = 2       # 内部错误
    ENTER_ROOM_REASON_MAINTENANCE = 3       # 系统维护
    ENTER_ROOM_REASON_ROOM_ID_ERROR = 4     # 房间错误
    ENTER_ROOM_REASON_VERSION_DISABLE = 5   # 版本过低
    ENTER_ROOM_REASON_TIME_LIMIT = 6        # 未到开放时间
    ENTER_ROOM_REASON_LESS_FEES = 7         # 钥匙不够
    ENTER_ROOM_REASON_STATE_ERROR = 8       # 在线状态错误
    ENTER_ROOM_REASON_LESS_BULLET = 9       # 招财珠不够
    ENTER_ROOM_REASON_SEAT_FULL = 10        # 座位已满
    ENTER_ROOM_REASON_LESS_VIP = 11         # VIP等级不够
    ENTER_ROOM_REASON_LESS_COIN = 12        # 金币不足
    ENTER_ROOM_REASON_EXCESSIVE_LOSS = 13   # 亏损过多
    ENTER_ROOM_REASON_NOT_OPEN = 14         # 房间暂未开放

    @classmethod
    def onCmdQuickStart(cls, msg, userId, gameId, roomId, tableId, clientId, kindId):
        """UT server中处理来自客户端的quick_start请求
        Args:
            msg
                cmd : quick_start
                if roomId == 0:
                    表示快速开始，服务器为玩家选择房间，然后将请求转给GR

                if roomId > 0 and tableId == 0 :
                    表示玩家选择了房间，将请求转给GR

                if roomId > 0 and tableId == roomId * 10000 :
                    表示玩家在队列里断线重连，将请求转给GR

                if roomId > 0 and tableId > 0:
                    if onlineSeatId > 0:
                        表示玩家在牌桌里断线重连，将请求转给GT
                    else:
                        表示玩家选择了桌子，将请求转给GR
        """