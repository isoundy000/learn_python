# -*- coding=utf-8 -*-
"""
Created by hhx on 17/10/10.
荣耀任务系统，对应achievement task配置.
"""

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
from newfish.entity.event import WinCmpttTaskEvent, WinBonusTaskEvent, MatchOverEvent, SkillLevelUpEvent, \
    StarfishChangeEvent, MatchGiveUpEvent, RankOverEvent, GainChestEvent, GunLevelUpEvent, EnterTableEvent, PrizeWheelSpinEvent, \
    MainQuestSectionFinishEvent
from newfish.entity.achievement.achievement_level import TaskState
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


def receiveTaskReward(userId, taskId):
    """
    领取荣耀任务奖励
    """
    # 分组信息
    if isLimitLevel(userId):
        return 7, None, None, None
    if not util.isFinishAllNewbieTask(userId):
        return 6, None, None, None
    honorId = int(taskId) / 100
    tasksConf = config.getAchievementTaskInfo(str(honorId))
    if not tasksConf or not tasksConf.get(str(taskId)):
        return 99, None, None, None

    curLevel = honor_system.getHonor(userId, honorId)[1]
    code = 0
    totalExp = 0
    level = 0
    # 当前的任务信息
    for level in xrange(1, int(taskId) % 100 + 1):
        taskId = honorId * 100 + level
        taskConf = tasksConf.get(str(taskId))
        if not tasksConf:
            continue
        # 为了兼容老玩家数据,需要从第一个任务开始检测.
        if level <= curLevel and taskConf["type"] != AchieveType.CompleteMainQuestSection:
            continue
        taskClass = FishAchievementTask(userId, taskConf)
        # 领取奖励
        code, exp_ = taskClass.receiveTaskReward(taskConf["Id"])
        if code != 0:
            continue
        totalExp += exp_
    if code == 0:
        if honorId:
            # 发送增加称号事件
            # 称号升级.
            from newfish.entity.event import GetAchievementTaskRewardEvent
            from newfish.game import TGFish
            event = GetAchievementTaskRewardEvent(userId, FISH_GAMEID, taskId, honorId, level)
            TGFish.getEventBus().publishEvent(event)
        if totalExp:   # 增加经验值
            levelClass = AchievementLevel(userId)
            levelClass.addAchievementExp(totalExp)

        # 更新小红点和进度
        updateAchievementModuleTips(userId, True)
    return code, honorId, level, totalExp


def doGetAllAchievementInfo(userId):
    """
    获取所有成就信息
    """
    achLevelClass = AchievementLevel(userId)
    message = MsgPack()
    message.setCmd("achievement_info")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    if isLimitLevel(userId):                                                                    # 等级限制
        message.setResult("code", 7)
        router.sendToUser(message, userId)
        return
    message.setResult("code", 0)
    message.setResult("achLevel", achLevelClass.getAchieveLevel())
    message.setResult("achExp", achLevelClass.getAchieveExp())
    message.setResult("achTotalExp", achLevelClass.getAchieveTotalExp())
    message.setResult("achLevelRewardInfo", achLevelClass.getCurAchievementLevelReward())
    honorList = honor_system.getHonorList(userId, True, [1, 2])                                 # 获取所有的勋章
    honorIds = module_tip.getTipValue(userId, module_tip.findModuleTip("achievement"))          # 荣耀任务是否闪烁
    for honorInfo in honorList:
        tasks = config.getAchievementTaskInfo(str(honorInfo["honorId"]))
        honorInfo["totalLevel"] = len(tasks.keys()) if tasks else 0
        honorInfo["isHasRed"] = str(honorInfo["honorId"]) in honorIds or int(honorInfo["honorId"]) in honorIds
    message.setResult("honors", honorList)
    router.sendToUser(message, userId)


def doGetAchievelLevelInfos(userId):
    """获取成就等级信息"""
    achLevelClass = AchievementLevel(userId)
    message = MsgPack()
    message.setCmd("achievement_level_info")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    if isLimitLevel(userId):
        message.setResult("code", 7)
        router.sendToUser(message, userId)
        return
    message.setResult("code", 0)
    message.setResult("levelInfos", achLevelClass.getAllLevelInfos())
    router.sendToUser(message, userId)


def doGetAllAchievementTasks(userId, honorId):
    """
    获取荣誉任务中一个称号的信息
    """
    message = MsgPack()
    message.setCmd("achievement_tasks")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    if isLimitLevel(userId):
        message.setResult("code", 7)
        router.sendToUser(message, userId)
        return
    if not util.isFinishAllNewbieTask(userId):
        message.setResult("code", 7)
        router.sendToUser(message, userId)
        return
    message.setResult("code", 0)
    tasks = getAllTaskInfo(userId, honorId)                                 # 勋章Id
    message.setResult("achievementTasks", tasks)                            # 里面的成就任务
    message.setResult("honorId", honorId)
    router.sendToUser(message, userId)


def doReceiveTaskReward(userId, taskId):
    """
    称号任务奖励领取
    """
    message = MsgPack()
    message.setCmd("achievement_tasks_reward")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    code, honorId, level, totalExp = receiveTaskReward(userId, taskId)
    message.setResult("code", code)
    if code == 0:
        # 当前完成进度
        message.setResult("taskId", taskId)
        message.setResult("exp", totalExp)
        message.setResult("achievementTasks", getAllTaskInfo(userId, honorId))
    router.sendToUser(message, userId)


def doReceiveAchieveLevelRewards(userId, level):
    """
    称号等级奖励领取
    """
    achLevelClass = AchievementLevel(userId)
    message = MsgPack()
    message.setCmd("achievement_level_reward")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    if isLimitLevel(userId):
        message.setResult("code", 7)
    else:
        code, rewards = achLevelClass.receiveLevelReward(level)
        message.setResult("code", code)
        if code == 0:
            # 当前完成进度
            message.setResult("achLevelRewardInfo", achLevelClass.getCurAchievementLevelReward())
            message.setResult("rewards", rewards)
            updateAchievementModuleTips(userId)
    router.sendToUser(message, userId)


def getAchievementAllTask(userId):
    """
    获取所有荣耀任务
    """
    if isLimitLevel(userId):
        return None
    return config.getAchievementConf().get("tasks")


def updateAchievementModuleTips(userId, isRefresh=False):
    """更新成就小红点"""
    module_tip.resetModuleTipEvent(userId, "achievement")
    taskConfigs = getAchievementAllTask(userId)
    if not taskConfigs:
        return
    achLevel = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.achievementLevel)
    receiveLevelState = daobase.executeUserCmd(userId, "HGET", fish_achievement_task.getTaskKey(userId), "levelReceived")
    if not receiveLevelState:
        if achLevel > 1:
            module_tip.addModuleTipEvent(userId, "achievement", 1)
    else:
        receiveLevelState = json.loads(receiveLevelState)
        maxLevel = max(set(receiveLevelState))
        if achLevel > maxLevel:
            module_tip.addModuleTipEvent(userId, "achievement", 1)

    levelMap, starMap = {}, {}
    if isRefresh:
        levelMap, starMap = fish_achievement_task.getSkillMaxLevel(userId)
    honorIds = []
    for honorId, configs in taskConfigs.iteritems():
        for _, taskConf in configs.iteritems():
            taskClass = FishAchievementTask(userId, taskConf)
            if isRefresh:
                if taskConf["type"] == AchieveType.SkillUp:  # 技能最高级
                    targetInfo = taskConf["target"]
                    if "star" in targetInfo:
                        taskClass.updateProgress(starMap[int(targetInfo["star"])])
                    elif "condition" in targetInfo:
                        taskClass.updateProgress(levelMap[int(targetInfo["condition"])])
            if taskClass.isComplete():
                honorIds.append(int(honorId))
    if honorIds:
        module_tip.addModuleTipEvent(userId, "achievement", honorIds)


def isLimitLevel(userId):
    """荣耀等级限制"""
    userLevel = util.getUserLevel(userId)
    if userLevel < config.getCommonValueByKey("achievementOpenLevel"):
        return True
    return False


def _updateSkillProgress(userId):
    """更新技能数据"""
    achConfigs = getAchievementAllTask(userId)
    if not achConfigs:
        return
    levelMap, starMap = fish_achievement_task.getSkillMaxLevel(userId)
    honorIds = []
    for honorId, tasksConf in achConfigs.iteritems():
        for _, conf in tasksConf.iteritems():
            taskClass = FishAchievementTask(userId, conf)
            if conf["type"] == AchieveType.SkillUp:  # 技能最高级
                targetInfo = conf["target"]
                if "star" in targetInfo:
                    taskClass.updateProgress(starMap[int(targetInfo["star"])])
                elif "condition" in targetInfo:
                    taskClass.updateProgress(levelMap[int(targetInfo["condition"])])
            if taskClass.isComplete():
                honorIds.append(int(honorId))
    if honorIds:
        module_tip.addModuleTipEvent(userId, "achievement", honorIds)


def _triggerStateChange(event):
    """触发状态改变 更新成就小红点"""
    updateAchievementModuleTips(event.userId)


# # 宝藏争夺赛
# def _triggerWinCmpttTaskEvent(event):
#     _winCmpttTaskEvent(event)
#
#
# def _winCmpttTaskEvent(event):
#     userId = event.userId
#     achConfigs = getAchievementAllTask(userId)
#     if not achConfigs:
#         return
#     for honorId, tasksConf in achConfigs.iteritems():
#         for _, conf in tasksConf.iteritems():
#             if conf["type"] == AchieveType.CmpttWinNum:  # 比赛获得胜利
#                 taskClass = FishAchievementTask(userId, conf)
#                 if taskClass.addProgress(1):
#                     module_tip.addModuleTipEvent(userId, "achievement", int(honorId))


# 进行多少次转盘转动
def _triggerPrizeWheelSpinEvent(event):
    userId = event.userId
    achConfigs = getAchievementAllTask(userId)
    if not achConfigs:
        return
    for honorId, tasksConf in achConfigs.iteritems():
        for _, conf in tasksConf.iteritems():
            if conf["type"] == AchieveType.LevelPrizeWheelNum:                          # 轮盘次数
                taskClass = FishAchievementTask(userId, conf)
                if taskClass.addProgress(1):
                    module_tip.addModuleTipEvent(userId, "achievement", int(honorId))


# 比赛结束
def _triggerMatchOverEvent(event):
    _matchOverEvent(event)


def _matchOverEvent(event):
    userId = event.userId
    rank = event.rank
    roomId = event.bigRoomId
    achConfigs = getAchievementAllTask(userId)
    if not achConfigs:
        return
    for honorId, tasksConf in achConfigs.iteritems():
        for _, conf in tasksConf.iteritems():
            if conf["type"] == AchieveType.TotalRankMatch:          # 回馈赛累计排名
                taskClass = FishAchievementTask(userId, conf)
                if rank <= conf["target"]["top"] and taskClass.addProgress(1):
                    module_tip.addModuleTipEvent(userId, "achievement", int(honorId))


def _triggerEnterTableEvent(event):
    """进入招财模式渔场"""
    if event.reconnect:
        return
    roomId, isMatch = util.getBigRoomId(event.roomId)
    _EnterRoomEvent(event.userId, roomId, isMatch)


def _EnterRoomEvent(userId, roomId, isMath):
    achConfigs = getAchievementAllTask(userId)
    if not achConfigs:
        return
    for honorId, tasksConf in achConfigs.iteritems():
        for _, conf in tasksConf.iteritems():
            if conf["type"] == AchieveType.JoinMatch and isMath:            # 参加比赛多少场
                targetRoomId = conf["target"].get("roomId")
                if not targetRoomId or targetRoomId == roomId:
                    taskClass = FishAchievementTask(userId, conf)
                    if taskClass.addProgress(1):
                        module_tip.addModuleTipEvent(userId, "achievement", int(honorId))
            elif conf["type"] == AchieveType.EnterRobbery:                  # 参加招财模式多少次
                if util.getRoomTypeName(roomId) == config.FISH_ROBBERY:     # 获取房间名
                    taskClass = FishAchievementTask(userId, conf)
                    if taskClass.addProgress(1):
                        module_tip.addModuleTipEvent(userId, "achievement", int(honorId))


# 排行榜结束
def _triggerRankOverEvent(event):
    _RankOverEvent(event)


def _RankOverEvent(event):
    userId = event.userId
    rank = event.rank
    rankId = event.rankId
    achConfigs = getAchievementAllTask(userId)
    if not achConfigs:
        return
    for honorId, tasksConf in achConfigs.iteritems():
        for _, conf in tasksConf.iteritems():
            if conf["type"] == AchieveType.TotalRankRobbery:        # 比赛获得胜利
                targetInfo = conf.get("target")
                if int(rankId) == int(targetInfo.get("rankId")):
                    taskClass = FishAchievementTask(userId, conf)
                    if taskClass.addProgress(1):
                        module_tip.addModuleTipEvent(userId, "achievement", int(honorId))


def _triggerGainChestEvent(event):
    """领取周宝箱"""
    _gainChestEvent(event)


def _gainChestEvent(event):
    from newfish.entity.chest.chest_system import ChestFromType
    userId = event.userId
    chestFrom = event.chestFrom
    achConfigs = getAchievementAllTask(userId)
    if not achConfigs:
        return
    for honorId, tasksConf in achConfigs.iteritems():
        for _, conf in tasksConf.iteritems():
            if conf["type"] == AchieveType.ReceiveWeekChest:            # 领取周宝箱
                if chestFrom == ChestFromType.Daily_Quest_Week_Chest:
                    taskClass = FishAchievementTask(userId, conf)
                    if taskClass.addProgress(1):
                        module_tip.addModuleTipEvent(userId, "achievement", int(honorId))


def _triggerLevelUpEvent(event):
    """技能提升"""
    userId = event.userId
    _updateSkillProgress(userId)


# 技能卡升级
def _triggerSkillLevelUpEvent(event):
    userId = event.userId
    _updateSkillProgress(userId)


# 海星收集
def _triggerStarfishChangeEvent(event):
    _starfishChangeEvent(event)


def _starfishChangeEvent(event):
    userId = event.userId
    count = event.count
    roomId = event.roomId
    if not roomId:
        return
    achConfigs = getAchievementAllTask(userId)
    if not achConfigs:
        return
    for honorId, tasksConf in achConfigs.iteritems():
        for _, conf in tasksConf.iteritems():
            if conf["type"] == AchieveType.CollectStar:  # 海星收集
                taskClass = FishAchievementTask(userId, conf)
                if taskClass.addProgress(count):
                    module_tip.addModuleTipEvent(userId, "achievement", int(honorId))


# 放弃比赛事件
def _triggerGiveUpMatchEvent(event):
    _giveUpMatchEvent(event)


def _giveUpMatchEvent(event):
    pass
    # taskConfigs = config.getAchievementConf()
    # userId = event.userId
    # roomId = event.roomId
    #
    # isHasCmp = False
    # for groupId in taskConfigs:
    #     groupClass = FishAchievementGroup(userId, groupId)
    #     taskConf = taskConfigs[groupId][groupClass.getCurTaskIndex()]
    #     taskClass = FishAchievementTask(userId, taskConf)
    #     hasComplete = False
    #     targetInfo = taskConf["target"]
    #     if taskConf["type"] == AchieveType.ContinueRankMatch:  # 连续参加回馈赛
    #         if targetInfo["roomId"] == roomId:
    #             hasComplete = taskClass.updateProgress(0)
    #     if hasComplete:
    #         module_tip.addModuleTipEvent(userId, "achievementold", taskConf.get("taskId"))


# def _triggerInvitedFinishEvent(event):
#     taskConfigs = config.getAchievementConf()
#     userId = event.userId
#     isHasCmp = False
#     for groupId in taskConfigs:
#         groupClass = FishAchievementGroup(userId, groupId)
#         taskConf = taskConfigs[groupId][groupClass.getCurTaskIndex()]
#         taskClass = FishAchievementTask(userId, taskConf)
#         hasComplete = False
#         if taskConf["type"] == AchieveType.InvitedNum:
#             hasComplete = taskClass.addProgress(1)
#         if hasComplete:
#             module_tip.addModuleTipEvent(userId, "achievementNew", taskConf.get("taskId"))
#     #    isHasCmp = isHasCmp or hasComplete
#     # if isHasCmp:
#     #     module_tip.addModuleTipEvent(userId, "achievementNew", 0)


def _triggerUserLoginEvent(event):
    updateAchievementModuleTips(event.userId, True)


# def _triggerDailyTaskFinishEvent(event):
#     taskConfigs = config.getAchievementConf()
#     userId = event.userId
#     isHasCmp = False
#     for groupId in taskConfigs:
#         groupClass = FishAchievementGroup(userId, groupId)
#         taskConf = taskConfigs[groupId][groupClass.getCurTaskIndex()]
#         taskClass = FishAchievementTask(userId, taskConf)
#         hasComplete = False
#         if taskConf["type"] == AchieveType.DayTaskNum:
#             hasComplete = taskClass.addProgress(1)
#         if hasComplete:
#             module_tip.addModuleTipEvent(userId, "achievementNew", taskConf.get("taskId"))


def _triggerMainQuestSectionFinishEvent(event):
    """
    主线任务章节完成事件
    """
    userId = event.userId
    achConfigs = getAchievementAllTask(userId)
    if not achConfigs:
        return
    currSectionId = event.sectionId
    honorIds = []
    for honorId, tasksConf in achConfigs.iteritems():
        for _, conf in tasksConf.iteritems():
            if conf["type"] != AchieveType.CompleteMainQuestSection:                                    # 完成主线任务
                continue
            taskClass = FishAchievementTask(userId, conf)
            finishAllMainQuest = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.finishAllMainQuest)
            curSectionIdx = currSectionId / 1000 % 640                                                  # 1、2、3、4、5
            # 所有章节都已完成
            if finishAllMainQuest:
                taskClass.taskData["progress"] = conf["target"]["num"]
            else:
                taskClass.taskData["progress"] = min(curSectionIdx, conf["target"]["num"])
            taskClass.updateProgress(taskClass.taskData["progress"])
            if taskClass.isComplete():
                honorIds.append(int(honorId))
    if honorIds:
        module_tip.addModuleTipEvent(userId, "achievement", honorIds)


_inited = False


def initialize():
    global _inited
    if not _inited:
        _inited = True
        ftlog.debug("newfish achievement_system_new initialize begin")
        from poker.entity.events.tyevent import EventUserLogin
        from newfish.game import TGFish
        # TGFish.getEventBus().subscribe(WinCmpttTaskEvent, _triggerWinCmpttTaskEvent)      # 夺宝赛获奖事件
        # TGFish.getEventBus().subscribe(WinBonusTaskEvent, _triggerWinCmpttTaskEvent)      # 奖金赛获奖事件
        TGFish.getEventBus().subscribe(MatchOverEvent, _triggerMatchOverEvent)              # 回馈赛结束事件
        TGFish.getEventBus().subscribe(EnterTableEvent, _triggerEnterTableEvent)            # 进入牌桌事件
        TGFish.getEventBus().subscribe(SkillLevelUpEvent, _triggerSkillLevelUpEvent)        # 技能升级事件
        TGFish.getEventBus().subscribe(StarfishChangeEvent, _triggerStarfishChangeEvent)    # 海星改变事件
        TGFish.getEventBus().subscribe(MatchGiveUpEvent, _triggerGiveUpMatchEvent)          # 放弃比赛
        TGFish.getEventBus().subscribe(EventUserLogin, _triggerUserLoginEvent)              # 用户登录事件
        TGFish.getEventBus().subscribe(RankOverEvent, _triggerRankOverEvent)                # 排行榜结算时间
        TGFish.getEventBus().subscribe(GainChestEvent, _triggerGainChestEvent)              # 获取宝箱事件
        TGFish.getEventBus().subscribe(GunLevelUpEvent, _triggerLevelUpEvent)               # 等级升级
        TGFish.getEventBus().subscribe(PrizeWheelSpinEvent, _triggerPrizeWheelSpinEvent)    # 进行多少转盘
        TGFish.getEventBus().subscribe(MainQuestSectionFinishEvent, _triggerMainQuestSectionFinishEvent)    # 堆金积玉

    ftlog.debug("newfish achievement_system_new initialize end")