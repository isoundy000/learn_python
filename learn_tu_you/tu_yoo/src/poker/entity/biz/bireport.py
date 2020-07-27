#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6
import struct
import time

import freetime.util.log as ftlog
from poker.entity.configure import gdata, pokerconf
from poker.entity.dao.daoconst import CHIP_TYPE_ALL, CHIP_TYPE_ITEM
from poker.util import timestamp, strutil
from poker.entity.dao import bidata, sessiondata
from poker.entity.biz import integrate
from datetime import datetime

_BILOGER = None
_CHIP_RECORD_TYPE = 1
_GAME_RECORD_TYPE = 4
_BI_LOG_SEQ_NUM = 0
_BI_LOG_SEQ_DATE = datetime.now().strftime('%Y_%m_%d')


def reportGameEvent(eventId, user_id, gameId, roomId, tableId, roundId, detalChip, state1, state2, cardlist, clientId, finalTableChip=0, finalUserChip=0,
                    arglist=[], argdict={}, logtag='game_event'):
    '''
    游戏牌桌阶段事件的HTTP远程BI汇报
    '''
    # fmt = "I I H I Q Q I q q q B B 20B"
    #        | | | | | | | | | | | | └- cardlist 当前事件操作的牌, 数字(0~54), 0xFF为无效
    #        | | | | | | | | | | | └- state2 当前事件操作的状态2(例如:托管,超时)
    #        | | | | | | | | | | └- state1 当前事件操作的状态1(例如:托管,超时)
    #        | | | | | | | | | └- finalUserChip 当前事件用户的最终所有金币数量
    #        | | | | | | | | └- finalTableChip 当前事件用户的最终桌子金币数量
    #        | | | | | | | └- detalChip 当前事件操作涉及的金币数量
    #        | | | | | | └- roundId 当前事件的游戏局ID(如果为比赛事件,即为比赛的ID, 如果为普通牌桌,即为牌局ID或时间戳)
    #        | | | | | └- tableId 游戏事件发生的房间桌子ID
    #        | | | | └- roomId 游戏事件发生的房间
    #        | | | └- clientId 客户端的clientId
    #        | | └- gameId 后端服务操作时使用的gameId
    #        | └- userId 事件产生的用户
    #        └- eventId 事件ID
    pass


def report(moduleName, *arglist, **argdict):
    pass


def getRoomOnLineUserCount(gameId, withShadowRoomInfo=0):
    '''
    重BI数据库中取得当前的游戏的所有的在线人数信息
    return allcount, counts, details
    allcount int，游戏内所有房间的人数的总和
    counts 字典dict，key为大房间ID（bigRoomId)，value为该大房间内的人数总和
    details 字典dict，key为房间实例ID（roomId），value为该放假内的人数
    此数据由每个GR，GT进程每10秒钟向BI数据库进行汇报一次
    '''
    allcount, counts, details, _, _, _ = bidata.getRoomOnLineUserCount(gameId, withShadowRoomInfo)
    return allcount, counts, details