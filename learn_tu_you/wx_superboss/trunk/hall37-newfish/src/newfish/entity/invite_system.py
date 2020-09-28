# -*- coding=utf-8 -*-
"""
Created by hhx on 18/03/30.
"""
import time
import json
from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.util import strutil
from poker.entity.dao import gamedata, userdata
from newfish.entity import weakdata
from newfish.entity import config, util, module_tip
from newfish.entity.config import FISH_GAMEID
from newfish.servers.util.rpc import user_rpc
from newfish.entity.chest import chest_system


OneGroupNum = 5
NewPlayerAction = 0
RecallPlayerAction = 1


def loginByInvited(userId, shareUserId, isNewPlayer):
    """
    :param userId: 被邀请人
    :param shareUserId: 分享者(邀请人)
    :param isNewPlayer: 是否为新用户
    """
    isCanInvite = config.getCommonValueByKey("canInvite")
    isInvite = weakdata.getDayFishData(userId, "isInvited", 0)
    if not isCanInvite or isInvite:
        return False
    userdata.checkUserData(shareUserId)
    if isNewPlayer:
        from newfish.game import TGFish
        from newfish.entity.event import AddInvitedNewUserEvent
        # 存储邀请人信息
        from hall.entity import hallvip
        from newfish.entity.redis_keys import GameData
        shareUserVip = int(hallvip.userVipSystem.getUserVip(shareUserId).vipLevel.level)
        inviterInfo = {
            "userId": shareUserId, "inviteTime": int(time.time()), "vip": shareUserVip
        }
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.inviterInfo, json.dumps(inviterInfo))
        saveKey = "inviteNewPlayers"
        actionType = NewPlayerAction
        event = AddInvitedNewUserEvent(shareUserId, FISH_GAMEID, userId)
        TGFish.getEventBus().publishEvent(event)
    else:
        saveKey = "recallPlayers"
        actionType = RecallPlayerAction
    user_rpc.addInviteNum(shareUserId, userId, actionType, saveKey, isNewPlayer)
    return True


def getInviteTasks(userId, actionType):
    weakDatas = weakdata.getDayFishDataAll(userId, FISH_GAMEID)
    taskConfs_ = config.getInviteTasks(actionType)
    taskConfs = taskConfs_.values()
    taskConfs = sorted(taskConfs, key=lambda data: data["Id"])
    if actionType == NewPlayerAction:
        taskState = strutil.loads(weakDatas.get("inviteTasks", "[]"))
        playerNums = len(strutil.loads(weakDatas.get("inviteNewPlayers", "[]")))

    else:
        taskState = strutil.loads(weakDatas.get("recallTasks", "[]"))
        playerNums = len(strutil.loads(weakDatas.get("recallPlayers", "[]")))

    taskStartIndex = len(taskState) / OneGroupNum * OneGroupNum
    taskStartIndex = min((len(taskConfs) / OneGroupNum - 1) * OneGroupNum, taskStartIndex)

    # 奖励
    taskInfos = []
    tipsTaskIds = []
    for m in range(taskStartIndex, taskStartIndex + 5):
        if m >= len(taskConfs):
            break
        taskConf = taskConfs[m]
        taskId = taskConf["Id"]
        taskInfo = {}
        taskInfo["Id"] = taskId
        rewards = []
        for _reward in taskConf["rewards"]:
            rewardMap = {}
            kindId = _reward["name"]
            rewardMap["name"] = kindId
            rewardMap["count"] = _reward["count"]
            rewardMap["info"] = {}
            if util.isChestRewardId(kindId):
                rewardMap["info"] = chest_system.getChestInfo(kindId)
            rewards.append(rewardMap)
        taskInfo["rewards"] = rewards
        taskInfo["target"] = taskConf["target"]
        state = 0
        if taskId in taskState:
            state = 2
        elif playerNums >= taskConf["target"]:
            tipsTaskIds.append(taskId)
            state = 1
        taskInfo["state"] = state
        taskInfos.append(taskInfo)

    module_tip.resetModuleTip(userId, "invitetasks")
    if tipsTaskIds:
        module_tip.addModuleTipEvent(userId, "invitetasks", tipsTaskIds)
    return taskInfos, playerNums


# 领取邀请奖励
def receiveInvitTaskReward(userId, taskId, actionType):
    weakDatas = weakdata.getDayFishDataAll(userId, FISH_GAMEID)
    taskConf = config.getInviteTaskConf(taskId, actionType)
    code = 0
    chestId = 0
    rewards = []
    taskState = []
    saveKey = "inviteTasks"
    if not taskConf:
        return 999, chestId, rewards, taskState
    if actionType == NewPlayerAction:
        taskState = strutil.loads(weakDatas.get("inviteTasks", "[]"))
        playerNums = len(strutil.loads(weakDatas.get("inviteNewPlayers", "[]")))
    else:
        saveKey = "recallTasks"
        taskState = strutil.loads(weakDatas.get("recallTasks", "[]"))
        playerNums = len(strutil.loads(weakDatas.get("recallPlayers", "[]")))

    if taskConf["target"] > playerNums:
        return 1, chestId, rewards, taskState

    if taskId in taskState:
        return 2, chestId, rewards, taskState

    rewards = taskConf["rewards"]
    for _reward in taskConf["rewards"]:
        kindId = _reward["name"]
        if util.isChestRewardId(kindId):
            chestId = kindId
            rewards = chest_system.getChestRewards(userId, kindId)
            code = chest_system.deliveryChestRewards(userId, kindId, rewards, "BI_NFISH_INVITE_TASK_REWARDS")
        else:
            code = util.addRewards(userId, [_reward], "BI_NFISH_INVITE_TASK_REWARDS", int(taskId))
    taskState.append(taskId)
    weakdata.setDayFishData(userId, saveKey, strutil.dumps(taskState))
    # 更新小红点
    module_tip.cancelModuleTipEvent(userId, "invitetasks", taskId)
    return code, chestId, rewards, taskState


# 返回任务列表
def doGetInviteTasks(userId, actionType):
    message = MsgPack()
    message.setCmd("invite_task_infos")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)

    message.setResult("actionType", actionType)
    isCanInvite = config.getCommonValueByKey("canInvite")
    if not isCanInvite:
        message.setResult("code", 100)
    else:
        message.setResult("code", 0)
        tasksInfos, playerNums = getInviteTasks(userId, actionType)
        message.setResult("tasks", tasksInfos)
        message.setResult("playerNums", playerNums)
    router.sendToUser(message, userId)


# 返回任务列表
def doGetTaskRewards(userId, taskId, actionType):
    message = MsgPack()
    message.setCmd("invite_task_receive")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    isCanInvite = config.getCommonValueByKey("canInvite")
    if not isCanInvite:
        message.setResult("code", 100)
        router.sendToUser(message, userId)
    else:
        code, chestId, rewards, taskState = receiveInvitTaskReward(userId, taskId, actionType)
        message.setResult("code", code)
        if code == 0:
            message.setResult("chestId", chestId)
            message.setResult("rewards", rewards)
        message.setResult("taskId", taskId)
        message.setResult("actionType", actionType)
        router.sendToUser(message, userId)

        if len(taskState) > 0 and len(taskState) % OneGroupNum == 0:
            doGetInviteTasks(userId, actionType)


def _triggerUserLoginEvent(event):
    if event and hasattr(event, "inviter") and event.inviter > 0:
        loginByInvited(event.userId, int(event.inviter), event.isCreate)


_inited = False


def initialize():
    ftlog.info("newfish invite_system initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from hall.entity.hallevent import EventAfterUserLogin
        from hall.game import TGHall
        TGHall.getEventBus().subscribe(EventAfterUserLogin, _triggerUserLoginEvent)
    ftlog.info("newfish invite_system initialize end")