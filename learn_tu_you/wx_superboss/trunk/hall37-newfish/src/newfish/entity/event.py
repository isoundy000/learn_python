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


class LevelUpEvent(UserEvent):
    """
    火炮等级/倍率提升事件
    """
    def __init__(self, userId, gameId, level, gunLevel, mode):
        super(LevelUpEvent, self).__init__(userId, gameId)
        # 玩家等级
        self.level = level
        # 火炮等级
        self.gunLevel = gunLevel
        # 经典/千炮
        self.gameMode = mode


class UserLevelUpEvent(UserEvent):
    """
    玩家等级提升事件
    """
    def __init__(self, userId, gameId, level):
        super(UserLevelUpEvent, self).__init__(userId, gameId)
        self.level = level


class UseSkillEvent(UserEvent):
    """
    使用技能事件
    """
    def __init__(self, userId, gameId, roomId, tableId, skillId, fpMultiple, chip=0):
        super(UseSkillEvent, self).__init__(userId, gameId)
        self.roomId = roomId
        self.tableId = tableId
        self.skillId = skillId
        self.chip = chip
        self.fpMultiple = fpMultiple


class EnterTableEvent(UserEvent):
    """
    进入桌子事件
    """
    def __init__(self, userId, gameId, roomId, tableId, seatId, reconnect=0):
        super(EnterTableEvent, self).__init__(userId, gameId)


class LeaveTableEvent(UserEvent):
    """
    离开桌子事件
    """
    def __init__(self, userId, gameId, roomId, tableId, seatId, enterTime=0):
        super(LeaveTableEvent, self).__init__(userId, gameId)
        self.roomId = roomId
        self.tableId = tableId
        self.seatId = seatId
        if enterTime:
            self.gameTime = int((time.time()) - enterTime) / 60
        else:
            self.gameTime = 0


class ChipChangeEvent(UserEvent):
    """
    金币变化事件
    """
    def __init__(self, userId, gameId, delta, final):
        super(ChipChangeEvent, self).__init__(userId, gameId)
        self.delta = delta
        self.final = final


class FishModuleTipEvent(UserEvent):
    """
    小红点变化事件
    """
    def __init__(self, userId, gameId, type, name, value):
        super(FishModuleTipEvent, self).__init__(userId, gameId)
        self.type = type
        self.name = name
        self.value = value


class SkillItemCountChangeEvent(UserEvent):
    """
    技能升级升星相关物品数量变化事件
    """
    def __init__(self, userId, gameId):
        super(SkillItemCountChangeEvent, self).__init__(userId, gameId)


class GunItemCountChangeEvent(UserEvent):
    """
    普通炮升级相关物品数量变化事件
    """
    def __init__(self, userId, gameId):
        super(GunItemCountChangeEvent, self).__init__(userId, gameId)


class SkillLevelUpEvent(UserEvent):
    """
    技能升级事件
    """
    def __init__(self, userId, gameId, skills, actionType):
        super(SkillLevelUpEvent, self).__init__(userId, gameId)
        self.skills = skills
        self.actionType = actionType   # 0:升级 1:升星


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


class SendMailEvent(UserEvent):
    """
    发送邮件事件
    """
    def __init__(self, userId, gameId, receiveUserId, reward):
        super(SendMailEvent, self).__init__(userId, gameId)
        self.receiveUserId = receiveUserId
        self.reward = reward


class ReceiveMailEvent(UserEvent):
    """
    收取邮件事件
    """
    def __init__(self, userId, gameId):
        super(ReceiveMailEvent, self).__init__(userId, gameId)


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
    def __init__(self, userId, gameId, itemId=None, itemCount=None, roomId=None):
        super(BulletChangeEvent, self).__init__(userId, gameId)
        self.itemId = itemId
        self.itemCount = itemCount
        self.roomId = roomId


class SuperbossPointChangeEvent(UserEvent):
    """
    超级boss积分变化事件
    """
    def __init__(self, userId, gameId, bigRoomId, point):
        super(SuperbossPointChangeEvent, self).__init__(userId, gameId)
        self.bigRoomId = bigRoomId
        self.point = point


class ActivityItemChangeEvent(UserEvent):
    """
    活动中道具变化事件（道具）
    """
    def __init__(self, userId, gameId, rewards=None):
        super(ActivityItemChangeEvent, self).__init__(userId, gameId)
        self.rewards = rewards







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


class ItemChangeEvent(UserEvent):
    """
    资产/道具变化事件
    :param type: 0：渔场外 1：渔场内
    """
    def __init__(self, userId, gameId, itemInfo, changed, type=0):
        super(ItemChangeEvent, self).__init__(userId, gameId)
        self.itemInfo = itemInfo
        self.changed = changed
        self.type = type


class AddGunSkinEvent(UserEvent):
    """
    皮肤炮增加事件
    """
    def __init__(self, userId, gameId, gunId, count, type, mode):
        super(AddGunSkinEvent, self).__init__(userId, gameId)
        self.gunId = gunId      # 炮ID
        self.count = count      # 炮的个数
        self.type = type        # 参数
        self.mode = mode        # 模式


class ComboEvent(UserEvent):
    """
    combo奖励 连击奖励
    """
    def __init__(self, userId, gameId, comboNum, chipNum):
        super(ComboEvent, self).__init__(userId, gameId)
        self.comboNum = comboNum        # 连击数
        self.chipNum = chipNum          # 金币数量


class FireEvent(UserEvent):
    """
    开火事件
    """
    def __init__(self, userId, gameId, roomId, tableId, wpId, fpMultiple, costChip=0, holdCoin=0):
        super(FireEvent, self).__init__(userId, gameId)
        self.roomId = roomId
        self.tableId = tableId
        self.wpId = wpId
        self.costChip = costChip
        self.holdCoin = holdCoin
        self.fpMultiple = fpMultiple


class UseCoolDownEvent(UserEvent):
    """
    使用冷却事件
    """
    def __init__(self, userId, gameId, roomId, tableId):
        super(UseCoolDownEvent, self).__init__(userId, tableId)
        self.roomId = roomId
        self.tableId = tableId


class NFChargeNotifyEvent(ChargeNotifyEvent):
    """
    充值通知事件
    """
    def __init__(self, userId, gameId, rmbs, diamonds, productId, clientId, isAddVipExp):
        super(NFChargeNotifyEvent, self).__init__(userId, gameId, rmbs, diamonds, productId, clientId)
        self.isAddVipExp = isAddVipExp


class RankOverEvent(UserEvent):
    """
    排行榜结算事件
    """
    def __init__(self, userId, gameId, rankId, rankType, rank, params=None):
        super(RankOverEvent, self).__init__(userId, gameId)
        self.rankId = rankId
        self.rankType = rankType
        self.rank = rank
        self.params = params








class ItemMonitorEvent(UserEvent):
    """
    道具检测事件
    """
    def __init__(self, userId, gameId, changed, changeEventId):
        super(ItemMonitorEvent, self).__init__(userId, gameId)
        self.changed = changed
        self.changeEventId = changeEventId


class PrizeWheelSpinEvent(UserEvent):
    """
    渔场转盘转动事件
    """
    def __init__(self, userId, gameId, roomId):
        super(PrizeWheelSpinEvent, self).__init__(userId, gameId)
        self.roomId = roomId


class NetIncomeChangeEvent(UserEvent):
    """
    渔场净收益变化事件
    """
    def __init__(self, userId, gameId, count, roomId=0):
        super(NetIncomeChangeEvent, self).__init__(userId, gameId)
        self.count = count
        self.roomId = roomId













class JoinGrandPrixEvent(UserEvent):
    """
    参加大奖赛事件
    """
    def __init__(self, userId, gameId, roomId):
        super(JoinGrandPrixEvent, self).__init__(userId, gameId)
        self.roomId = roomId


class FinishGrandPrixEvent(UserEvent):
    """
    完成大奖赛事件
    """
    def __init__(self, userId, gameId, roomId, grandPrixFinalPoint):
        super(FinishGrandPrixEvent, self).__init__(userId, gameId)
        self.roomId = roomId
        self.grandPrixFinalPoint = grandPrixFinalPoint


class ProductBuyEvent(UserEvent):
    """
    商品购买事件
    """
    def __init__(self, userId, gameId, productId, clientId, buyCount):
        super(ProductBuyEvent, self).__init__(userId, gameId)
        self.productId = productId
        self.clientId = clientId
        self.buyCount = buyCount


class BuyInspireGift(UserEvent):
    """
    购买鼓舞礼包事件
    """
    def __init__(self, userId, gameId, teamId, ratio, remainTime):
        super(BuyInspireGift, self).__init__(userId, gameId)
        self.teamId = teamId
        self.ratio = ratio
        self.remainTime = remainTime


class HitPoseidonEvent(UserEvent):
    """
    击中波塞冬事件
    """
    def __init__(self, userId, gameId, count):
        super(HitPoseidonEvent, self).__init__(userId, gameId)
        self.count = count


class ChangeGunLevelEvent(UserEvent):
    """
    切换火炮等级事件
    """
    def __init__(self, userId, gameId, roomId, gLev):
        super(ChangeGunLevelEvent, self).__init__(userId, gameId)
        self.roomId = roomId
        self.gLev = gLev

