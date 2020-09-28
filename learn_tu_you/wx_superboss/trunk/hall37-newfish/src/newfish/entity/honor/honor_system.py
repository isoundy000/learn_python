# -*- coding=utf-8 -*-
"""
新版称号系统
Created by haohongxian on 2019/06/05.
"""

import json
import time

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.util import strutil
from poker.entity.dao import daobase, gamedata
from hall.entity import hallitem
from newfish.entity import config, module_tip, util, mail_system
from newfish.entity.redis_keys import GameData, UserData
from newfish.entity.config import FISH_GAMEID
from newfish.entity.event import GetAchievementTaskRewardEvent, GetHonorEvent, \
    NewbieTaskCompleteEvent, MainQuestSectionFinishEvent


INDEX_STATE = 0                 # 第0位:称号状态      0:未获得 1:已获得未使用 2:已获得使用中
INDEX_LEVEL = 1                 # 第1位:等级
INDEX_CREATE_TIME = 2           # 第2位:称号领取时间


class BufferType:
    Default = 0                 # 默认类型
    FireFrequency = 1           # 开火频率
    PowerAdd = 2                # 武器威力提升
    MatchRewardAdd = 3          # 回馈赛额外增加奖励
    UnlockGunSkin = 4           # 解锁皮肤炮
    StarfishRankRewardAdd = 5   # 海星榜额外增加奖励


def _buildUserHonorKey(userId):
    """
    称号数据存取key
    """
    return UserData.honor % (FISH_GAMEID, userId)


def initHonor(userId):
    """
    初始化称号数据
    """
    for honorId in config.getHonorConf().keys():
        updateHonor(userId, honorId)


def updateHonor(userId, honorId):
    """
    更新新增称号数据
    """
    assert (str(honorId) in config.getHonorConf().keys())
    honorInfo = [0, 0, 0]
    daobase.executeUserCmd(userId, "HSETNX", _buildUserHonorKey(userId), str(honorId), json.dumps(honorInfo))


def setHonor(userId, honorId, honorInfo):
    """
    存储单个称号数据
    """
    assert (str(honorId) in config.getHonorConf().keys())
    assert (isinstance(honorInfo, list) and len(honorInfo) == 3)
    daobase.executeUserCmd(userId, "HSET", _buildUserHonorKey(userId), str(honorId), json.dumps(honorInfo))


def getHonor(userId, honorId):
    """
    获得单个称号数据
    """
    assert(str(honorId) in config.getHonorConf().keys())
    value = daobase.executeUserCmd(userId, "HGET", _buildUserHonorKey(userId), str(honorId))
    if value:
        return strutil.loads(value, False, True)
    return [0, 0, 0]


def _getAllHonors(userId):
    """
    获得所有称号数据
    """
    assert(isinstance(userId, int) and userId > 0)
    value = daobase.executeUserCmd(userId, "HGETALL", _buildUserHonorKey(userId))
    if value:
        honorIds = value[0::2]
        infos = [strutil.loads(info, False, True) for info in value[1::2] if info]
        return dict(zip(honorIds, infos))
    return {}


def getOwnedHonors(userId, allHonors=None):
    """
    获得已拥有称号数据
    """
    honors = {}
    allHonors = allHonors or _getAllHonors(userId)
    if allHonors:
        for honorId, info in allHonors.iteritems():
            if info[INDEX_STATE] != 0:
                honors[int(honorId)] = info
    return honors


def getInstalledHonor(userId, allHonors=None):
    """
    获得已装备称号数据
    """
    return -1, [0, 0, 0]


def getHonorList(userId, hasDesc=False, honorTypeList=None):
    """
    获取称号信息列表
    """
    honorTypeList = honorTypeList or []
    honors = []
    allHonors = _getAllHonors(userId)
    if allHonors:
        lang = util.getLanguage(userId)
        for honorId, info in allHonors.iteritems():
            honor = {}
            honorConf = config.getHonorConf(honorId)
            if honorTypeList and honorConf.get("honorType") not in honorTypeList:
                continue
            honor["honorId"] = int(honorId)
            honorNameId = honorConf["honorName"]
            honor["name"] = config.getMultiLangTextConf(str(honorNameId), lang=lang)
            # 月卡存储的是过期时间
            if honorConf["honorType"] == 3:
                honor["state"] = 1 if int(time.time()) < int(info[INDEX_CREATE_TIME]) else 0
                honor["level"] = honor["state"]
            else:
                honor["state"] = int(info[INDEX_STATE])
                honor["level"] = int(info[INDEX_LEVEL])
            honor["time"] = int(info[INDEX_CREATE_TIME])
            if hasDesc:
                honorDescId = honorConf["desc"]
                honor["desc"] = config.getMultiLangTextConf(str(honorDescId), lang=lang)
            honors.append(honor)

    honors.sort(cmp=cmpHonor)               # 勋章排序
    return honors


def getHonorConfList(userId):
    """
    获取称号信息列表
    """
    honors = []
    allHonors = _getAllHonors(userId)
    if allHonors:
        for honorId, info in allHonors.iteritems():
            honor = {}
            honorConf = config.getHonorConf(honorId)
            honor["honorId"] = int(honorId)
            honor["state"] = int(info[INDEX_STATE])
            honor["level"] = int(info[INDEX_LEVEL])
            honor["time"] = int(info[INDEX_CREATE_TIME])
            honor["desc"] = honorConf["desc"]
            honors.append(honor)
    honors.sort(cmp=cmpHonor)
    return honors


def replaceHonor(userId, honorId, broadcastUserIds=None):
    """
    更换称号
    """
    return 1
    # reason = 1
    # honorInfo = getHonor(userId, honorId)
    # if honorInfo[INDEX_STATE] == 1:
    #     installedHonorId, installedHonorInfo = getInstalledHonor(userId)
    #     if installedHonorId >= 0:
    #         installedHonorInfo[INDEX_STATE] = 1
    #         honorInfo[INDEX_STATE] = 2
    #         setHonor(userId, installedHonorId, installedHonorInfo)
    #         setHonor(userId, honorId, honorInfo)
    #         reason = 0
    # mo = MsgPack()
    # mo.setCmd("honor_replace")
    # mo.setResult("gameId", FISH_GAMEID)
    # mo.setResult("userId", userId)
    # mo.setResult("honorId", honorId)
    # mo.setResult("reason", reason)
    # if broadcastUserIds:
    #     router.sendToUsers(mo, broadcastUserIds)
    # else:
    #     router.sendToUser(mo, userId)
    # return reason


def pushHonor(userId, honorId):
    """
    获得称号时推送
    """
    mo = MsgPack()
    mo.setCmd("honor_push")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)

    # mo.setResult("honors", getHonorList(userId))
    router.sendToUser(mo, userId)
    isIn, roomId, tableId, seatId = util.isInFishTable(userId)
    if isIn:
        mo = MsgPack()
        mo.setCmd("table_call")
        mo.setParam("action", "honor_push")
        mo.setParam("gameId", FISH_GAMEID)
        mo.setParam("clientId", util.getClientId(userId))
        mo.setParam("userId", userId)
        mo.setParam("roomId", roomId)
        mo.setParam("tableId", tableId)
        mo.setParam("seatId", seatId)
        router.sendTableServer(mo, roomId)
    from newfish.game import TGFish
    event = GetHonorEvent(userId, FISH_GAMEID, honorId)
    TGFish.getEventBus().publishEvent(event)


def installHonor(userId, honorId):
    """
    获得称号时装备
    """
    pass
    # isIn, roomId, tableId, seatId = util.isInFishTable(userId)
    # if isIn:
    #     mo = MsgPack()
    #     mo.setCmd("table_call")
    #     mo.setParam("action", "honor_replace")
    #     mo.setParam("gameId", FISH_GAMEID)
    #     mo.setParam("clientId", util.getClientId(userId))
    #     mo.setParam("userId", userId)
    #     mo.setParam("roomId", roomId)
    #     mo.setParam("tableId", tableId)
    #     mo.setParam("seatId", seatId)
    #     mo.setParam("honorId", honorId)
    #     router.sendTableServer(mo, roomId)
    # else:
    #     replaceHonor(userId, honorId)


def cmpHonor(honor1, honor2):
    """
    称号排序
    """
    if honor1["level"] > honor2["level"]:
        return -1
    if honor1["level"] < honor2["level"]:
        return 1
    return honor1["honorId"] - honor2["honorId"]
    # if honor1["state"] == 1 and honor2["state"] == 1:
    #     return -1 if honor1Rare > honor2Rare else 1
    # if honor1["state"] == 0 and honor2["state"] == 0:
    #     return -1 if honor1Rare < honor2Rare else 1


def addNewHonor(userId, honorId, level):
    """
    添加新称号
    """
    setHonor(userId, honorId, [1, level, int(time.time())])
    pushHonor(userId, honorId)
    # installHonor(userId, honorId)
    # module_tip.addModuleTipEvent(userId, "honor", honorId)


def getWeaponPowerAddition(honors, wpId):
    """
    获得特殊称号的武器威力加成
    """
    power = 1
    # for honorId in honors:
    #     honorConf = config.getHonorConf(honorId)
    #     if honorConf["bufferType"] == BufferType.PowerAdd:
    #         bufferInfo = honorConf["bufferInfo"]
    #         if util.getWeaponType(wpId) == bufferInfo["weaponType"]:
    #             power += bufferInfo["powerAddition"]
    return power


def sendMatchRewardMail(userId, roomId, rank):
    """
    发放特殊称号的比赛额外奖励
    """
    ownedHonors = getOwnedHonors(userId)
    # for honorId in ownedHonors:
    #     honorConf = config.getHonorConf(honorId)
    #     if honorConf["bufferType"] == BufferType.MatchRewardAdd:    # 额外奖励
    #         bufferInfo = honorConf["bufferInfo"]
    #         if roomId in bufferInfo["roomId"] and bufferInfo["rank"][0] <= rank <= bufferInfo["rank"][1]:
    #             mail_system.sendSystemMail(userId, mail_system.MailType.HonorReward,  bufferInfo["reward"], bufferInfo["message"])


def sendStarfishRankRewardMail(userId, rank):
    """
    发放特殊称号的海星榜额外奖励
    """
    ownedHonors = getOwnedHonors(userId)
    # for honorId in ownedHonors:
    #     honorConf = config.getHonorConf(honorId)
    #     if honorConf["bufferType"] == BufferType.StarfishRankRewardAdd:
    #         bufferInfo = honorConf["bufferInfo"]
    #         if bufferInfo["rank"][0] <= rank <= bufferInfo["rank"][1] and bufferInfo["reward"]:
    #             mail_system.sendSystemMail(userId, mail_system.MailType.HonorReward, bufferInfo["reward"], bufferInfo["message"])


def _triggerAchievementTaskRewardEvent(event):
    """
    发放荣耀任务奖励的称号
    """
    userId = event.userId
    honorId = event.honorId
    level = event.level
    allHonorConf = config.getHonorConf()
    honorInfo = getHonor(userId, honorId)
    for _, honorConf in allHonorConf.iteritems():
        if (honorConf["honorType"] == 1 and honorConf["honorId"] == honorId and level > honorInfo[INDEX_LEVEL]):
            addNewHonor(userId, honorId, level)
            break


def _triggerNewbieTaskCompleteEvent(event):
    """
    新手任务完成发放(实力认可)称号
    """
    pass
    # userId = event.userId
    # allHonorConf = config.getHonorConf()
    # ownedHonors = getOwnedHonors(userId)
    # for _, honorConf in allHonorConf.iteritems():
    #     if honorConf["honorType"] == 2 and honorConf["honorId"] not in ownedHonors:
    #         addNewHonor(userId, honorConf["honorId"])
    #         break


def _triggerUserLoginEvent(event):
    """登陆事件"""
    userId = event.userId
    initHonor(userId)
    _sendHonorCompensate(userId)
    checkMonthCardHonor(userId)


def _sendHonorCompensate(userId):
    """
    称号补偿
    """
    from newfish.entity import mail_system
    from newfish.entity.mail_system import MailRewardType
    oldKey = "honor2:%d:%d" % (FISH_GAMEID, userId)
    value = daobase.executeUserCmd(userId, "HGETALL", oldKey)
    if not value:
        return
    if gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.compensateOldHonor):
        return

    honorIds = value[0::2]
    infos = [strutil.loads(info, False, True) for info in value[1::2] if info]
    honorData = dict(zip(honorIds, infos))
    compensateRewards = {}
    compensateConf = config.getAchievementConf().get("compensate", {})
    compensateKeys = compensateConf.keys()
    for key_, value_ in honorData.iteritems():
        key_ = str(key_)
        if key_ in compensateKeys and value_[INDEX_STATE] > 0:
            _reward = compensateConf.get(key_, {})
            compensateRewards.setdefault(_reward.get("name"), 0)
            compensateRewards[_reward.get("name")] += _reward.get("count")
    rewards = []
    for k, v in compensateRewards.iteritems():
        rewards.append({"name": int(k), "count": int(v)})
    msg = config.getMultiLangTextConf("ID_HONOR_TASK_CHANGE_REWARD_MSG", lang=util.getLanguage(userId))
    if rewards:
        mail_system.sendSystemMail(userId, MailRewardType.SystemCompensate, rewards, msg)
    # daobase.executeUserCmd(userId, "del", oldKey)
    gamedata.setGameAttr(userId, FISH_GAMEID, GameData.compensateOldHonor, 1)


def _triggerMainQuestSectionFinishEvent(event):
    """
    主线任务章节完成事件
    """
    userId = event.userId
    honorId = event.honorId / 100
    honorLevel = event.honorId % 100
    allHonorConf = config.getHonorConf()
    honorInfo = getHonor(userId, honorId)
    for _, honorConf in allHonorConf.iteritems():
        if (honorConf["honorType"] == 2 and honorConf["honorId"] == honorId and honorLevel > honorInfo[INDEX_LEVEL]):
            addNewHonor(userId, honorId, honorLevel)
            module_tip.addModuleTipEvent(userId, "achievement", int(honorId))
            break


def checkMonthCardHonor(userId):
    """
    检查月卡相关称号
    """
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    itemPermanent = userBag.getItemByKindId(config.PERMANENT_MONTH_CARD_KINDID)
    item = userBag.getItemByKindId(config.MONTH_CARD_KINDID)
    for honorId in config.getHonorConf().keys():
        honorConf = config.getHonorConf(honorId)
        if honorConf.get("honorType") == 3:
            honorInfo = getHonor(userId, honorId)
            if itemPermanent:
                honorInfo[INDEX_STATE] = 1
                honorInfo[INDEX_LEVEL] = honorInfo[INDEX_STATE]
                honorInfo[INDEX_CREATE_TIME] = int(time.time()) + 86400 * 10000
            elif item:
                honorInfo[INDEX_STATE] = 1 if not item.isDied(int(time.time())) else 0
                honorInfo[INDEX_LEVEL] = honorInfo[INDEX_STATE]
                honorInfo[INDEX_CREATE_TIME] = item.expiresTime
            else:
                honorInfo[INDEX_STATE] = 0
                honorInfo[INDEX_LEVEL] = 0
                honorInfo[INDEX_CREATE_TIME] = 0
            setHonor(userId, honorId, honorInfo)
            break


_inited = False


def initialize():
    global _inited
    if not _inited:
        _inited = True
        ftlog.debug("newfish honor_system initialize begin")
        from poker.entity.events.tyevent import EventUserLogin
        from newfish.game import TGFish
        TGFish.getEventBus().subscribe(GetAchievementTaskRewardEvent, _triggerAchievementTaskRewardEvent)
        TGFish.getEventBus().subscribe(NewbieTaskCompleteEvent, _triggerNewbieTaskCompleteEvent)
        TGFish.getEventBus().subscribe(EventUserLogin, _triggerUserLoginEvent)
        # TGFish.getEventBus().subscribe(MainQuestSectionFinishEvent, _triggerMainQuestSectionFinishEvent)
        ftlog.debug("newfish honor_system initialize end")