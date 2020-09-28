# -*- coding=utf-8 -*-
"""
Created by lichen on 2020/5/8.
回归豪礼
"""

import json
import time
import math
from datetime import datetime

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.entity.dao import gamedata
from poker.protocol import router
from poker.entity.biz import bireport
from newfish.entity.redis_keys import GameData, WeakData
from newfish.entity.config import FISH_GAMEID
from newfish.entity import util, config, weakdata, module_tip
from hall.entity import hallvip


def getReturnerMission(userId, clientId):
    """
    获取回归豪礼
    """
    timeLeft = 0
    currTime = int(time.time())
    returnerMission = getReturnerMissionData(userId)
    returnerMissionConf = config.getReturnerMissionConf()
    if returnerMission:
        # 获取回归豪礼结束倒计时
        expireDays = returnerMissionConf["expireDays"] * 24 * 3600
        endTime = returnerMission["lastActiveTime"] + expireDays
        timeLeft = max(endTime - currTime, 0)
    mo = MsgPack()
    mo.setCmd("returner_mission")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("timeLeft", timeLeft)
    if timeLeft > 0:
        # 是否首次登录弹出
        dayFirst = weakdata.incrDayFishData(userId, WeakData.returnerMission, 1)
        # 当前是激活后的第几个任务(按天处理)
        lastActiveTime = util.getDayStartTimestamp(returnerMission["lastActiveTime"])
        fewDays = (datetime.fromtimestamp(currTime) - datetime.fromtimestamp(lastActiveTime)).days + 1
        fewDays = max(1, min(fewDays, len(returnerMission["tasks"])))
        currentTaskId = returnerMissionConf["tasks"][fewDays - 1]["taskId"]
        lang = util.getLanguage(userId, clientId)
        # 任务数据
        tasks = buildTaskData(returnerMission, lang)
        mo.setResult("dayFirst", 1 if dayFirst == 1 else 0)
        mo.setResult("currentTaskId", currentTaskId)
        mo.setResult("rule", config.getMultiLangTextConf(returnerMissionConf["rule"], lang=lang))
        mo.setResult("tasks", tasks)
    router.sendToUser(mo, userId)


def getReturnerReward(userId, clientId, taskId):
    """
    领取回归豪礼
    """
    rewards = None
    returnerMission = getReturnerMissionData(userId)
    if returnerMission:
        for taskConf in config.getReturnerMissionConf("tasks"):
            if taskConf["taskId"] == taskId and taskId in returnerMission["tasks"]:
                if returnerMission["tasks"][taskId]["state"] == 2:
                    rewards = buildTaskRewards(taskConf["rewards"], returnerMission["userLevel"], returnerMission["vipExp"])
                    returnerMission["tasks"][taskId]["state"] = 3
                    break
    mo = MsgPack()
    mo.setCmd("returner_reward")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("taskId", taskId)
    mo.setResult("code", 0 if rewards else 1)
    if rewards:
        util.addRewards(userId, rewards, "BI_NFISH_RETURNER_REWARDS", int(taskId))
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.returnerMission, json.dumps(returnerMission))
        module_tip.cancelModuleTipEvent(userId, "returnerMission", taskId)
        mo.setResult("rewards", rewards)
    router.sendToUser(mo, userId)


def buildTaskData(returnerMission, lang):
    """
    构建任务数据
    """
    taskList = []
    for taskConf in config.getReturnerMissionConf("tasks"):
        if taskConf["taskId"] in returnerMission["tasks"]:
            task = {}
            taskId = taskConf["taskId"]
            taskData = returnerMission["tasks"][taskId]
            task["taskId"] = taskId
            task["desc"] = config.getMultiLangTextConf(taskConf["desc"], lang=lang)
            task["progress"] = [min(taskData["progress"], taskConf["value"]), taskConf["value"]]
            task["state"] = taskData["state"]
            task["rewards"] = buildTaskRewards(taskConf["rewards"], returnerMission["userLevel"], returnerMission["vipExp"])
            taskList.append(task)
    return taskList


def buildTaskRewards(rewards, userLevel, vipExp):
    """
    计算任务奖励
    """
    n = int(max(1, min(math.ceil(vipExp / 10000.0), 10)))
    for reward in rewards:
        if reward["name"] == config.CHIP_KINDID:
            reward["count"] *= userLevel * n
        elif reward["name"] == config.STARFISH_KINDID:
            reward["count"] *= n
    return rewards


def getReturnerMissionData(userId):
    """
    获取回归豪礼数据
    """
    returnerMission = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.returnerMission, {})
    if returnerMission:
        currTime = int(time.time())
        expireDays = config.getReturnerMissionConf("expireDays") * 24 * 3600
        endTime = returnerMission["lastActiveTime"] + expireDays
        # 是否全部领取、是否过期
        isAllReceived = True
        for taskData in returnerMission["tasks"].values():
            if taskData["state"] != 3:
                isAllReceived = False
        if isAllReceived or currTime >= endTime:
            return {}
    return returnerMission


def refreshReturnerMissionData(userId, lastLoginTime):
    """
    刷新回归豪礼数据
    """
    currTime = int(time.time())
    lastLoginTime = util.getDayStartTimestamp(lastLoginTime)
    returnerMissionConf = config.getReturnerMissionConf()
    # 判断是否激活回归豪礼
    if currTime - lastLoginTime >= returnerMissionConf["daysLost"] * 24 * 3600:
        returnerMission = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.returnerMission, {})
        lastActiveTime = util.getDayStartTimestamp(returnerMission.get("lastActiveTime", currTime))
        isActive = False
        if returnerMission:
            if currTime - lastActiveTime >= returnerMissionConf["daysBetween"] * 24 * 3600:
                isActive = True
        else:
            isActive = True
        if isActive:
            userLevel = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.level)
            vipLevel = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
            vipExp = hallvip.userVipSystem.getUserVip(userId).vipExp
            returnerMission = {}
            returnerMission["lastActiveTime"] = currTime
            returnerMission["userLevel"] = userLevel
            returnerMission["vipExp"] = vipExp
            returnerMission["tasks"] = initTaskData()
            gamedata.setGameAttr(userId, FISH_GAMEID, GameData.returnerMission, json.dumps(returnerMission))
            bireport.reportGameEvent("BI_NFISH_GE_RETURNER_MISSION", userId, FISH_GAMEID, vipLevel,
                                     vipExp, userLevel, 0, 0, 0, [], util.getClientId(userId))
    returnerMission = getReturnerMissionData(userId)
    if returnerMission:
        # 解锁新任务
        lastActiveTime = util.getDayStartTimestamp(returnerMission["lastActiveTime"])
        fewDays = (datetime.fromtimestamp(currTime) - datetime.fromtimestamp(lastActiveTime)).days + 1
        fewDays = max(1, min(fewDays, len(returnerMission["tasks"])))
        # 第N天之前的任务都会解锁
        isUnlock = False
        taskIds = []
        for _index, taskConf in enumerate(config.getReturnerMissionConf("tasks")):
            if taskConf["taskId"] in returnerMission["tasks"]:
                if _index < fewDays and returnerMission["tasks"][taskConf["taskId"]]["state"] == 0:
                    returnerMission["tasks"][taskConf["taskId"]]["state"] = 1
                    isUnlock = True
                elif returnerMission["tasks"][taskConf["taskId"]]["state"] == 2:
                    taskIds.append(taskConf["taskId"])
        if isUnlock:
            gamedata.setGameAttr(userId, FISH_GAMEID, GameData.returnerMission, json.dumps(returnerMission))
        if taskIds:
            module_tip.addModuleTipEvent(userId, "returnerMission", taskIds)
    else:
        module_tip.resetModuleTipEvent(userId, "returnerMission")


def initTaskData():
    """
    初始化任务数据
    """
    tasks = {}
    for _index, taskConf in enumerate(config.getReturnerMissionConf("tasks")):
        task = {"progress": 0, "state": 0}
        if _index == 0:
            task["state"] = 2
        tasks[taskConf["taskId"]] = task
    return tasks


def addProgress(userId, taskLevel):
    """
    增加任务进度
    """
    taskIds = []
    returnerMission = getReturnerMissionData(userId)
    if returnerMission:
        # 未解锁的任务进度为最后一个已解锁的任务进度
        notUnlockedProgress = 0
        for taskConf in config.getReturnerMissionConf("tasks"):
            if taskConf["taskId"] in returnerMission["tasks"]:
                taskData = returnerMission["tasks"][taskConf["taskId"]]
                if taskData["state"] == 1:
                    taskData["progress"] += taskLevel
                    taskData["progress"] = min(taskData["progress"], taskConf["value"])
                    notUnlockedProgress = taskData["progress"]
                    if taskData["progress"] >= taskConf["value"]:
                        taskData["state"] = 2
                        taskData["progress"] = taskConf["value"]
                elif taskData["state"] == 0:
                    taskData["progress"] = max(taskData["progress"], notUnlockedProgress)
                if taskData["state"] == 2:
                    taskIds.append(taskConf["taskId"])
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.returnerMission, json.dumps(returnerMission))
    taskIds and module_tip.addModuleTipEvent(userId, "returnerMission", taskIds)


def _triggerDailyTaskRewardEvent(event):
    """
    每日任务完成事件
    """
    userId = event.userId
    taskLevel= event.taskLevel
    addProgress(userId, taskLevel)


_inited = False


def initialize():
    ftlog.debug("newfish returner_mission initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from newfish.entity.event import DailyTaskRewardEvent
        from newfish.game import TGFish
        TGFish.getEventBus().subscribe(DailyTaskRewardEvent, _triggerDailyTaskRewardEvent)
    ftlog.debug("newfish returner_mission initialize end")