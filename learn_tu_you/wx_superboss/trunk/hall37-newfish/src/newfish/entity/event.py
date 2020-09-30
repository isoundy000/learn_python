# -*- coding=utf-8 -*-
"""
Created by lichen on 16/1/12.
"""

import time

from poker.entity.events.tyevent import UserEvent
from poker.entity.events.tyevent import ChargeNotifyEvent
from newfish.entity.config import CLASSIC_MODE


class CatchEvent(UserEvent):
    """
    捕获事件
    """
    def __init__(self, userId, gameId, roomId, tableId, fishTypes, wpId, gainChip, fpMultiple, catch=None, gain=None,
                 resetTime=0, gunSkinMul=1, gunX=1, gameMode=CLASSIC_MODE, catchFishMultiple=None):
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
        self.gunX = gunX
        self.catchFishMultiple = catchFishMultiple


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
        self.isFinishRedTask = isFinishRedTask
        self.fpMultiple = fpMultiple


class GunLevelUpEvent(UserEvent):
    """
    火炮等级/倍率提升事件
    """
    def __init__(self, userId, gameId, level, gunLevel, mode):
        super(GunLevelUpEvent, self).__init__(userId, gameId)
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


class UseSkillItemEvent(UserEvent):
    """
    使用技能道具事件
    """
    def __init__(self, userId, gameId, roomId, tableId, kindId):
        super(UseSkillItemEvent, self).__init__(userId, gameId)
        self.roomId = roomId
        self.tableId = tableId
        self.kindId = kindId


class UseSmiliesEvent(UserEvent):
    """
    使用表情事件
    """
    def __init__(self, userId, gameId, roomId, tableId, smilieId):
        super(UseSmiliesEvent, self).__init__(userId, gameId)
        self.smilieId = smilieId


class OpenChestEvent(UserEvent):
    """
    打开背包中的宝箱事件（已废弃）
    """
    def __init__(self, userId, gameId, chestId, atOnce):
        super(OpenChestEvent, self).__init__(userId, gameId)
        self.chestId = chestId
        self.atOnce = atOnce


class ShopBuyEvent(UserEvent):
    """
    购买商品事件
    """
    def __init__(self, userId, gameId, productId, buyType, itemId, shopType):
        super(ShopBuyEvent, self).__init__(userId, gameId)
        self.productId = productId
        self.buyType = buyType
        self.itemId = itemId
        self.shopType = shopType


class GiftBuyEvent(UserEvent):
    """
    购买礼包事件
    """
    def __init__(self, userId, gameId, productId, buyType, giftId):
        super(GiftBuyEvent, self).__init__(userId, gameId)
        self.productId = productId
        self.buyType = buyType
        self.giftId = giftId


class BuyChestEvent(UserEvent):
    """
    购买宝箱事件
    """
    def __init__(self, userId, gameId, chestId, buyType, price):
        super(BuyChestEvent, self).__init__(userId, gameId)
        self.chestId = chestId
        self.buyType = buyType
        self.price = price


class BulletBuyEvent(UserEvent):
    """
    购买招财珠事件
    """
    def __init__(self, userId, gameId, itemId, count):
        super(BulletBuyEvent, self).__init__(userId, gameId)
        self.itemId = itemId
        self.count = count


class WinCmpttTaskEvent(UserEvent):
    """
    夺宝赛获奖事件
    """
    def __init__(self, userId, gameId, roomId, tableId):
        super(WinCmpttTaskEvent, self).__init__(userId, gameId)
        self.roomId = roomId
        self.tableId = tableId


class WinNcmpttTaskEvent(UserEvent):
    """
    限时任务获奖事件
    """
    def __init__(self, userId, gameId, roomId, tableId):
        super(WinNcmpttTaskEvent, self).__init__(userId, gameId)
        self.roomId = roomId
        self.tableId = tableId


class WinBonusTaskEvent(UserEvent):
    """
    奖金赛获奖事件
    """
    def __init__(self, userId, gameId, roomId, tableId, rank):
        super(WinBonusTaskEvent, self).__init__(userId, gameId)
        self.roomId = roomId
        self.tableId = tableId
        self.rank = rank


class EnterTableEvent(UserEvent):
    """
    进入桌子事件
    """
    def __init__(self, userId, gameId, roomId, tableId, seatId, reconnect=0):
        super(EnterTableEvent, self).__init__(userId, gameId)
        self.roomId = roomId
        self.tableId = tableId
        self.seatId = seatId
        self.reconnect = reconnect


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
            self.gameTime = int(time.time() - enterTime) / 60
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


class TreasureItemCountChangeEvent(UserEvent):
    """
    宝藏升级相关物品数量变化事件
    """
    def __init__(self, userId, gameId):
        super(TreasureItemCountChangeEvent, self).__init__(userId, gameId)


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


class MatchOverEvent(UserEvent):
    """
    回馈赛结束事件
    """
    def __init__(self, userId, gameId, bigRoomId, rank):
        super(MatchOverEvent, self).__init__(userId, gameId)
        self.bigRoomId = bigRoomId
        self.rank = rank


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


class MatchGiveUpEvent(UserEvent):
    """
    回馈赛放弃事件
    """
    def __init__(self, userId, gameId, roomId):
        super(MatchGiveUpEvent, self).__init__(userId, gameId)
        self.roomId = roomId


class MatchRewardEvent(UserEvent):
    """
    回馈赛结算发奖事件
    """
    def __init__(self, userId, gameId, roomId, rank, rewards):
        super(MatchRewardEvent, self).__init__(userId, gameId)
        self.roomId = roomId
        self.rank = rank
        self.rewards = rewards


class DailyTaskFinishEvent(UserEvent):
    """
    完成单个每日任务事件
    """
    def __init__(self, userId, gameId, taskId, taskLevel):
        super(DailyTaskFinishEvent, self).__init__(userId, gameId)
        self.taskId = taskId
        self.taskLevel = taskLevel


class DailyTaskRewardEvent(UserEvent):
    """
    领取单个每日任务奖励事件
    """
    def __init__(self, userId, gameId, taskId, taskLevel):
        super(DailyTaskRewardEvent, self).__init__(userId, gameId)
        self.taskId = taskId
        self.taskLevel = taskLevel


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


class GetActivityRewardEvent(UserEvent):
    """
    领取活动奖励事件
    """
    def __init__(self, userId, gameId, activityId, taskId, rewards):
        super(GetActivityRewardEvent, self).__init__(userId, gameId)
        self.activityId = activityId
        self.taskId = taskId
        self.rewards = rewards


class GetAchievementTaskRewardEvent(UserEvent):
    """
    领取荣耀任务奖励事件
    """
    def __init__(self, userId, gameId, taskId, honorId, level):
        super(GetAchievementTaskRewardEvent, self).__init__(userId, gameId)
        self.taskId = taskId
        self.honorId = honorId
        self.level = level


class AchievementLevelUpEvent(UserEvent):
    """
    荣耀任务升级事件
    """
    def __init__(self, userId, gameId, level):
        super(AchievementLevelUpEvent, self).__init__(userId, gameId)
        self.level = level


class GetHonorEvent(UserEvent):
    """
    获得称号事件
    """
    def __init__(self, userId, gameId, honorId):
        super(GetHonorEvent, self).__init__(userId, gameId)
        self.honorId = honorId


class AddCharmEvent(UserEvent):
    """
    魅力值增加事件
    """
    def __init__(self, userId, gameId, charmNum):
        super(AddCharmEvent, self).__init__(userId, gameId)
        self.charmNum = charmNum


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


class GameTimeLuckyAddEvent(UserEvent):
    """
    玩家抽奖事件
    """
    def __init__(self, userId, gameId, coinNum):
        super(GameTimeLuckyAddEvent, self).__init__(userId, gameId)
        self.coinNum = coinNum


class OpenEggsEvent(UserEvent):
    """
    开启扭蛋事件
    """
    def __init__(self, userId, gameId, coinNum):
        super(OpenEggsEvent, self).__init__(userId, gameId)
        self.coinNum = coinNum


class GuideChangeEvent(UserEvent):
    """
    新手引导增加事件
    """
    def __init__(self, userId, gameId, isGuideOver):
        super(GuideChangeEvent, self).__init__(userId, gameId)
        self.isGuideOver = isGuideOver


class ComboEvent(UserEvent):
    """
    combo奖励 连击奖励
    """
    def __init__(self, userId, gameId, comboNum, chipNum):
        super(ComboEvent, self).__init__(userId, gameId)
        self.comboNum = comboNum        # 连击数
        self.chipNum = chipNum          # 金币数量


class RobberyBulletChangeEvent(UserEvent):
    """
    招财模式招财珠变化
    """
    def __init__(self, userId, gameId, kindId, count, cost):
        super(RobberyBulletChangeEvent, self).__init__(userId, gameId)
        self.kindId = kindId
        self.count = count
        self.cost = cost


class RobberyBulletProfitEvent(UserEvent):
    """
    招财模式结算时盈利金币数
    """
    def __init__(self, userId, gameId, coin):
        super(RobberyBulletProfitEvent, self).__init__(userId, gameId)
        self.coin = coin


class NewbieTaskCompleteEvent(UserEvent):
    """
    新手任务完成事件
    """
    def __init__(self, userId, gameId):
        super(NewbieTaskCompleteEvent, self).__init__(userId, gameId)


class StoreBuyEvent(UserEvent):
    """
    商城购买事件
    """

    def __init__(self, userId, gameId, actionType, productId):
        super(StoreBuyEvent, self).__init__(userId, gameId)
        self.actionType = actionType
        self.productId = productId


class TableTaskStartEvent(UserEvent):
    """
    渔场任务开始事件
    """

    def __init__(self, userId, gameId, tableId, taskId):
        super(TableTaskStartEvent, self).__init__(userId, gameId)
        self.tableId = tableId
        self.taskId = taskId


class TableTaskEndEvent(UserEvent):
    """
    渔场任务结束事件
    """

    def __init__(self, userId, gameId, tableId, taskId, isComplete, isLimitTime, rewards):
        super(TableTaskEndEvent, self).__init__(userId, gameId)
        self.tableId = tableId
        self.taskId = taskId
        self.isComplete = isComplete
        self.isLimitTime = isLimitTime
        self.rewards = rewards


class CheckinEvent(UserEvent):
    """
    签到事件
    """
    def __init__(self, userId, gameId, day, rewards):
        super(CheckinEvent, self).__init__(userId, gameId)
        self.day = day
        self.rewards = rewards


class NewSkillEvent(UserEvent):
    """
    获得新技能事件
    """
    def __init__(self, userId, gameId, skillId, eventId):
        super(NewSkillEvent, self).__init__(userId, gameId)
        self.skillId = skillId
        self.eventId = eventId


class RandomChestShareEvent(UserEvent):
    """
    随机宝箱分享弹出事件
    """
    def __init__(self, userId, gameId):
        super(RandomChestShareEvent, self).__init__(userId, gameId)


class ShareFinishEvent(UserEvent):
    """
    分享完成事件
    """
    def __init__(self, userId, gameId, shareId, typeId, shareMode):
        super(ShareFinishEvent, self).__init__(userId, gameId)
        self.shareId = shareId
        self.typeId = typeId
        self.shareMode = shareMode


class InvitedFinishEvent(UserEvent):
    """
    邀请完成事件
    """
    def __init__(self, userId, gameId):
        super(InvitedFinishEvent, self).__init__(userId, gameId)


class AddInvitedNewUserEvent(UserEvent):
    """
    添加新的邀请人
    """
    def __init__(self, userId, gameId, invitedUserId):
        super(AddInvitedNewUserEvent, self).__init__(userId, gameId)
        self.invitedUserId = invitedUserId


class UserVipExpChangeEvent(UserEvent):
    """
    用户vip经验值变化通知
    """
    def __init__(self, userId, gameId, toAddExp):
        super(UserVipExpChangeEvent, self).__init__(userId, gameId)
        self.toAddExp = toAddExp


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
        super(UseCoolDownEvent, self).__init__(userId, gameId)
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


class GainChestEvent(UserEvent):
    """
    领取宝箱奖励事件 需要的获取奖励的宝箱处理 目前只把需要的地方处理了一下
    """
    def __init__(self, userId, gameId, chestId, chestFrom):
        super(GainChestEvent, self).__init__(userId, gameId)
        self.chestFrom = chestFrom      # 渔场比赛获得
        self.chestId = chestId          # dropItem


class MainQuestSectionFinishEvent(UserEvent):
    """
    主线任务章节完成事件
    """
    def __init__(self, userId, gameId, sectionId, honorId):
        super(MainQuestSectionFinishEvent, self).__init__(userId, gameId)
        self.sectionId = sectionId                  # 章节ID
        self.honorId = honorId


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


class SlotMachineAddIntegralEvent(UserEvent):
    """
    老虎机活动积分增加事件
    """
    def __init__(self, userId, gameId, integral):
        super(SlotMachineAddIntegralEvent, self).__init__(userId, gameId)
        self.integral = integral


class MoneyTreeAddCountEvent(UserEvent):
    """
    摇钱树活动摇动次数增加事件
    """
    def __init__(self, userId, gameId, count):
        super(MoneyTreeAddCountEvent, self).__init__(userId, gameId)
        self.count = count


class NetIncomeChangeEvent(UserEvent):
    """
    渔场净收益变化事件
    """
    def __init__(self, userId, gameId, count, roomId=0):
        super(NetIncomeChangeEvent, self).__init__(userId, gameId)
        self.count = count
        self.roomId = roomId


class FestivalTurntableAddIntegralEvent(UserEvent):
    """
    节日转盘抽大奖活动积分增加事件
    """
    def __init__(self, userId, gameId, integral):
        super(FestivalTurntableAddIntegralEvent, self).__init__(userId, gameId)
        self.integral = integral


class PoseidonProfitAndLossEvent(UserEvent):
    """
    海皇来袭单轮Boss结算事件
    """
    def __init__(self, userId, gameId, coin):
        super(PoseidonProfitAndLossEvent, self).__init__(userId, gameId)
        self.coin = coin


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


class ConsumeVoucherEvent(UserEvent):
    """
    消耗代购券事件
    """
    def __init__(self, userId, gameId, count):
        super(ConsumeVoucherEvent, self).__init__(userId, gameId)
        self.count = count


class PlayMiniGame(UserEvent):
    """
    玩小游戏次数
    """
    def __init__(self, userId, gameId, count=1):
        super(PlayMiniGame, self).__init__(userId, gameId)
        self.count = count


class MiniGameBossExchange(UserEvent):
    """
    小游戏Boss兑换
    """
    def __init__(self, userId, gameId, count):
        super(MiniGameBossExchange, self).__init__(userId, gameId)
        self.count = count


class TreasureLevelUp(UserEvent):
    """
    宝藏升级事件
    """
    def __init__(self, userId, gameId, kindId, level):
        super(TreasureLevelUp, self).__init__(userId, gameId)
        self.kindId = kindId
        self.level = level