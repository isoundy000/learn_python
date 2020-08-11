#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/30
# 荣耀任务系统，对应achievement task配置.

import time
import json

from datetime import datetime
from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.dao import gamedata, daobase
from newfish.entity import util, config, module_tip
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData
from newfish.entity.achievement import fish_achievement_task
from newfish.entity.achievement.fish_achievement_task import FishAchievementTask, AchieveType
from newfish.entity.achievement.achievement_level import AchievementLevel
from newfish.entity.event import WinCmpttTaskEvent, \
    WinBonusTaskEvent, MatchOverEvent, SkillLevelUpEvent, \
    StarfishChangeEvent, MatchGiveUpEvent, RankOverEvent, GainChestEvent, LevelUpEvent, EnterTableEvent
from newfish.entity.honor import honor_system


def getAllTaskInfo(userId, honorId):
    """
    获取所有任务数据
    """
    achievementConfigs = config.getAchievementTaskInfo(str(honorId))
    if not achievementConfigs:
        return []
    taskInfos = []
    for _, taskConfig in achievementConfigs.iteritems():
        # 任务类
        taskClass = FishAchievementTask(userId, taskConfig)
        # 获取数据
        taskInfo = taskClass.getTaskInfo()
        taskInfos.append(taskInfo)
    taskInfos.sort(key=lambda info: info["taskId"])
    return taskInfos




















def doGetAllAchievementTasks(userId, honorId):
    """
    获取所有成就任务
    """
    message = MsgPack()
    message.setCmd("achievement_tasks")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    if isLimitLevel(userId):
        message.setResult("code", 7)
        router.sendToUser(message, userId)
        return
    message.setResult("code", 0)
    tasks = getAllTaskInfo(userId, honorId)
    message.setResult("achievementTasks", tasks)
    message.setResult("honorId", honorId)
    router.sendToUser(message, userId)













def isLimitLevel(userId):
    """荣耀等级限制"""
    userLevel = util.getUnlockCheckLevel(userId)
    if userLevel < config.getCommonValueByKey("achievementOpenLevel"):
        return True
    return False





















_inited = False


def initialize():
    global _inited
    if not _inited:
        _inited = True
        ftlog.debug("newfish achievement_system_new initialize begin")
        from poker.entity.events.tyevent import EventUserLogin
        from newfish.game import TGFish
        TGFish.getEventBus().subscribe(WinCmpttTaskEvent, _triggerWinCmpttTaskEvent)        # 夺宝赛获奖事件
        TGFish.getEventBus().subscribe(WinBonusTaskEvent, _triggerWinCmpttTaskEvent)        # 奖金赛获奖事件
        TGFish.getEventBus().subscribe(MatchOverEvent, _triggerMatchOverEvent)              # 回馈赛结束事件
        TGFish.getEventBus().subscribe(EnterTableEvent, _triggerEnterTableEvent)            # 进入牌桌事件
        TGFish.getEventBus().subscribe(SkillLevelUpEvent, _triggerSkillLevelUpEvent)        # 技能升级事件
        TGFish.getEventBus().subscribe(StarfishChangeEvent, _triggerStarfishChangeEvent)    # 海星改变事件
        TGFish.getEventBus().subscribe(MatchGiveUpEvent, _triggerGiveUpMatchEvent)          # 放弃比赛
        TGFish.getEventBus().subscribe(EventUserLogin, _triggerUserLoginEvent)              # 用户登录事件
        TGFish.getEventBus().subscribe(RankOverEvent, _triggerRankOverEvent)                # 排行榜结算时间
        TGFish.getEventBus().subscribe(GainChestEvent, _triggerGainChestEvent)              # 获取宝箱事件
        TGFish.getEventBus().subscribe(LevelUpEvent, _triggerLevelUpEvent)                  # 等级升级

    ftlog.debug("newfish achievement_system_new initialize end")