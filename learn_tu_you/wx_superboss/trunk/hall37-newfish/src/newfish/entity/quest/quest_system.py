#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/8

import time

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.events.tyevent import EventUserLogin
from newfish.entity import weakdata
from newfish.entity.config import FISH_GAMEID
from newfish.entity.quest import daily_quest, main_quest
from newfish.entity.event import CatchEvent, GameTimeEvent, LevelUpEvent, \
    OpenChestEvent, BuyChestEvent, UseSkillEvent, UseSmiliesEvent, \
    WinCmpttTaskEvent, WinNcmpttTaskEvent, WinBonusTaskEvent, EnterTableEvent, \
    StoreBuyEvent, TableTaskEndEvent, ShareFinishEvent, CheckinEvent, UseCoolDownEvent, \
    FireEvent, ItemChangeEvent, GainChestEvent, RobberyBulletProfitEvent, \
    SkillLevelUpEvent, AchievementLevelUpEvent


def refreshQuestData(userId):
    """
    重置每日任务存档
    """
    daily_quest.refreshDailyQuestData(userId)


def getQuestInfo(userId, clientId):
    """
    获取玩家每日任务数据
    """
    resetTime = weakdata.getDayFishData(userId, "resetTime")
    if not resetTime:
        weakdata.setDayFishData(userId, "resetTime", int(time.time()))
        refreshQuestData(userId)                                            # 重置每日任务存档
    dailyQuestData = daily_quest.getDailyQuestData(userId)                  # 获取玩家每日任务数据
    mainQuestData = main_quest.getMainQuestData(userId, clientId)           # 获取主线任务数据
    mo = MsgPack()
    mo.setCmd("task")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("action", "update")
    mo.setResult("dailyTask", dailyQuestData)
    mo.setResult("mainTask", mainQuestData)
    router.sendToUser(mo, userId)


def _triggerCatchEvent(event):
    """触发捕鱼事件"""
    daily_quest.triggerCatchEvent(event)
    main_quest.triggerCatchEvent(event)


def _triggerGameTimeEvent(event):
    """触发游戏时长事件"""
    daily_quest.triggerGameTimeEvent(event)


def _triggerLevelUpEvent(event):
    """火炮等级提升事件"""
    daily_quest.triggerLevelUpEvent(event)
    main_quest.triggerLevelUpEvent(event)


def _triggerOpenChestEvent(event):
    """开启宝箱事件"""
    daily_quest.triggerOpenChestEvent(event)


def _triggerBuyChestEvent(event):
    """购买宝箱事件"""
    daily_quest.triggerBuyChestEvent(event)


def _triggerUseSkillEvent(event):
    """使用技能事件"""
    daily_quest.triggerUseSkillEvent(event)
    main_quest.triggerUseSkillEvent(event)


def _triggerUseSmiliesEvent(event):
    """使用表情事件"""
    daily_quest.triggerUseSmiliesEvent(event)


def _triggerWinCmpttTaskEvent(event):
    """夺宝赛获奖事件"""
    daily_quest.triggerWinCmpttTaskEvent(event)
    main_quest.triggerWinCmpttTaskEvent(event)


def _triggerWinNcmpttTaskEvent(event):
    """限时任务获奖事件"""
    daily_quest.triggerWinNcmpttTaskEvent(event)


def _triggerWinBonusTaskEvent(event):
    """奖金赛获奖事件"""
    daily_quest.triggerWinBonusTaskEvent(event)


def _triggerEnterTableEvent(event):
    """进入渔场事件"""
    daily_quest.triggerEnterTableEvent(event)
    main_quest.triggerEnterTableEvent(event)


def _triggerStoreBuyEvent(event):
    """商城购买事件"""
    daily_quest.triggerStoreBuyEvent(event)


def _triggerTableTaskEndEvent(event):
    """渔场任务结束事件"""
    daily_quest.triggerTableTaskEndEvent(event)


def _triggerShareFinishEvent(event):
    """分享完成事件"""
    daily_quest.triggerShareFinishEvent(event)


def _triggerCheckinEvent(event):
    """签到事件"""
    daily_quest.triggerCheckinEvent(event)


def _triggerUseCoolDownEvent(event):
    """使用冷却事件"""
    daily_quest.triggerUseCoolDownEvent(event)


def _triggerFireEvent(event):
    """开火事件"""
    daily_quest.triggerFireEvent(event)


def _triggerItemChangeEvent(event):
    """道具/资产变化事件"""
    main_quest.triggerItemChangeEvent(event)


def _triggerGainChestEvent(event):
    """宝箱奖励事件"""
    main_quest.triggerGainChestEvent(event)


def _triggerRobberyBulletProfitEvent(event):
    """单次招财模式赢取招财珠对应金币数"""
    main_quest.triggerRobberyBulletProfitEvent(event)


def _triggerUserLoginEvent(event):
    """触发登陆事件"""
    main_quest.triggerUserLoginEvent(event)


def _triggerSkillLevelUpEvent(event):
    """技能升级事件"""
    main_quest.triggerSkillLevelUpEvent(event)


def _triggerAchievementLevelUpEvent(event):
    main_quest.triggerAchievementLevelUpEvent(event)


def incrRecharge(userId, rmbs):
    daily_quest.incrRecharge(userId, rmbs)


_inited = False


def initialize():
    ftlog.info("newfish quest_system initialize begin")
    global _inited
    if not _inited:
        _inited = True
        # 每日任务系统初始化
        daily_quest.initialize()
        from newfish.game import TGFish
        TGFish.getEventBus().subscribe(CatchEvent, _triggerCatchEvent)
        TGFish.getEventBus().subscribe(GameTimeEvent, _triggerGameTimeEvent)
        TGFish.getEventBus().subscribe(LevelUpEvent, _triggerLevelUpEvent)
        TGFish.getEventBus().subscribe(OpenChestEvent, _triggerOpenChestEvent)
        TGFish.getEventBus().subscribe(BuyChestEvent, _triggerBuyChestEvent)
        TGFish.getEventBus().subscribe(UseSkillEvent, _triggerUseSkillEvent)
        TGFish.getEventBus().subscribe(UseSmiliesEvent, _triggerUseSmiliesEvent)
        TGFish.getEventBus().subscribe(WinCmpttTaskEvent, _triggerWinCmpttTaskEvent)
        TGFish.getEventBus().subscribe(WinNcmpttTaskEvent, _triggerWinNcmpttTaskEvent)
        TGFish.getEventBus().subscribe(WinBonusTaskEvent, _triggerWinBonusTaskEvent)
        TGFish.getEventBus().subscribe(EnterTableEvent, _triggerEnterTableEvent)
        TGFish.getEventBus().subscribe(StoreBuyEvent, _triggerStoreBuyEvent)
        TGFish.getEventBus().subscribe(TableTaskEndEvent, _triggerTableTaskEndEvent)
        TGFish.getEventBus().subscribe(ShareFinishEvent, _triggerShareFinishEvent)
        TGFish.getEventBus().subscribe(CheckinEvent, _triggerCheckinEvent)
        TGFish.getEventBus().subscribe(UseCoolDownEvent, _triggerUseCoolDownEvent)
        TGFish.getEventBus().subscribe(FireEvent, _triggerFireEvent)
        TGFish.getEventBus().subscribe(ItemChangeEvent, _triggerItemChangeEvent)
        TGFish.getEventBus().subscribe(GainChestEvent, _triggerGainChestEvent)
        TGFish.getEventBus().subscribe(RobberyBulletProfitEvent, _triggerRobberyBulletProfitEvent)
        TGFish.getEventBus().subscribe(EventUserLogin, _triggerUserLoginEvent)
        TGFish.getEventBus().subscribe(SkillLevelUpEvent, _triggerSkillLevelUpEvent)
        TGFish.getEventBus().subscribe(AchievementLevelUpEvent, _triggerAchievementLevelUpEvent)
    ftlog.info("newfish quest_system initialize end")