#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6


import time

from poker.entity.events.tyevent import UserEvent
from poker.entity.events.tyevent import ChargeNotifyEvent
from newfish.entity.config import CLASSIC_MODE


class CatchEvent(UserEvent):
    """
    捕获事件
    """
    def __init__(self, userId, gameId, roomId, tableId, fishTypes, wpId, gainChip, fpMultiple, catch=None, gain=None,
                 resetTime=0, gunSkinMul=1, gameMode=CLASSIC_MODE):
        super(CatchEvent, self).__init__(userId, gameId)
        self.roomId = roomId
        self.tableId = tableId
        self.fishTypes = fishTypes
        self.wpId = wpId
        self.gainChip = gainChip
        self.fpMultiple = fpMultiple
        self.catch = catch
        self.gain = gain
        self.resetTime = resetTime
        self.gunSkinMul = gunSkinMul
        self.gameMode = gameMode


class GameTimeEvent(UserEvent):
    """
    游戏时长事件
    """
    def __init__(self, userId, gameId, roomId, tableId, fishPool, gameTime, fpMultiple, isFinishRedTask=False):
        super(GameTimeEvent, self).__init__(userId, gameId)
        self.roomId = roomId
        self.tableId = tableId
        self.fishPool = fishPool
        self.gameTime = gameTime
        self.fpMultiple = fpMultiple
        self.isFinishRedTask = isFinishRedTask


class EnterTableEvent(UserEvent):
    """
    进入桌子事件
    """
    def __init__(self, userId, gameId, roomId, tableId, seatId, reconnect=0):
        super(EnterTableEvent, self).__init__(userId, gameId)




class LeaveTableEvent(UserEvent):
    pass



class ChipChangeEvent(UserEvent):
    """
    金币变化事件
    """
    def __init__(self, userId, gameId, delta, final):
        super(ChipChangeEvent, self).__init__(userId, gameId)
        self.delta = delta
        self.final = final


class CheckLimitTimeGiftEvent(UserEvent):
    """
    检查限时礼包事件
    """
    def __init__(self, userId, gameId, level, chip, fishPool, clientId):
        super(CheckLimitTimeGiftEvent, self).__init__(userId, gameId)
        self.level = level
        self.chip = chip
        self.fishPool = fishPool
        self.clientId = clientId


class StarfishChangeEvent(UserEvent):
    """
    海星数量变化事件
    """
    def __init__(self, userId, gameId, count, roomId=0):
        super(StarfishChangeEvent, self).__init__(userId, gameId)
        self.count = count
        self.roomId = roomId


class BulletChangeEvent(UserEvent):
    """
    招财珠数量变化事件
    """
    def __int__(self, userId, gameId, itemId=None, itemCount=None, roomId=None):
        super(BulletChangeEvent, self).__init__(userId, gameId)
        self.itemId = itemId
        self.itemCount = itemCount
        self.roomId = roomId


class MatchWinloseEvent(UserEvent):
    """
    回馈赛胜负事件
    """
    def __init__(self, userId, gameId, matchId, isGroup, isWin, rank, signinUserCount, rewards, luckyValue):
        super(MatchWinloseEvent, self).__init__(userId, gameId)
        self.matchId = matchId
        self.isGroup = isGroup
        self.isWin = isWin
        self.rank = rank
        self.signinUserCount = signinUserCount
        self.rewards = rewards
        self.luckyValue = luckyValue


class FireEvent(UserEvent):
    """
    开火事件
    """
    def __int__(self, userId, gameId, roomId, tableId, wpId, fpMultiple, costChip=0, holdCoin=0):
        super(FireEvent, self).__init__(userId, gameId)
        self.roomId = roomId
        self.tableId = tableId
        self.wpId = wpId
        self.costChip = costChip
        self.holdCoin = holdCoin
        self.fpMultiple = fpMultiple


class NetIncomeChangeEvent(UserEvent):
    """
    渔场净收益变化事件
    """
    def __init__(self, userId, gameId, count, roomId=0):
        super(NetIncomeChangeEvent, self).__init__(userId, gameId)
        self.count = count
        self.roomId = roomId


class ChangeGunLevelEvent(UserEvent):
    """
    切换火炮等级事件
    """
    def __init__(self, userId, gameId, roomId, gLev):
        super(ChangeGunLevelEvent, self).__init__(userId, gameId)
        self.roomId = roomId
        self.gLev = gLev

