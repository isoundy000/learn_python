# -*- coding=utf-8 -*-
"""
Created by hhx on 17/6/14.
"""

import json
from distutils.version import StrictVersion


from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from poker.protocol import router

from poker.entity.dao import daobase, gamedata
from hall.entity import hallvip
from newfish.entity import util, config, module_tip
from newfish.entity.redis_keys import GameData, UserData
from newfish.entity.fishactivity.fish_activity import ActivityErrorCode
from newfish.entity.config import FISH_GAMEID


def updateUnReadNotice(userId, clientId, allConfigs=None, readNotice=None):
    """
    是否有未读的活动
    """
    hasUnRead = False
    tipsIds = []
    allConfigs = allConfigs or _getAllNoticeConfigs(userId, clientId)
    readNotice = readNotice or _getNoticeReadInfo(userId)
    for notConf in allConfigs:
        if notConf["Id"] not in readNotice:
            hasUnRead = True
            tipsIds.append(notConf["Id"])
    module_tip.resetModuleTip(userId, "noticenew")
    if hasUnRead:
        tipsIds.append(0)
    module_tip.addModuleTipEvent(userId, "noticenew", tipsIds)


def _getActivityKey(userId):
    return UserData.activity % (FISH_GAMEID, userId)


def _getNoticeReadInfo(userId):
    """获取读取的公告"""
    readNotice = daobase.executeUserCmd(userId, "HGET", _getActivityKey(userId), "notice")
    readNotice = json.loads(readNotice) if readNotice else []
    return readNotice


def _setNoticeReadInfo(userId, readInfo):
    daobase.executeUserCmd(userId, "HSET", _getActivityKey(userId), "notice", json.dumps(readInfo))


def loginModuleUpdate(userId, clientId):
    """登陆模块更新"""
    allConfigs = config.getNoticeConf()
    readNotice = _getNoticeReadInfo(userId)
    noticeKeys = []
    for noticeId in allConfigs:
        noticeKeys.append(noticeId)
    delIds = set(readNotice) - set(noticeKeys)
    readNotice = list(set(readNotice).difference(delIds))
    _setNoticeReadInfo(userId, readNotice)
    updateUnReadNotice(userId, clientId, readNotice=readNotice)


def getAllNotice(userId, clientId):
    """
    获取所有开启活动的信息
    """
    noticeConfigs = _getAllNoticeConfigs(userId, clientId)
    readNotice = _getNoticeReadInfo(userId)
    ftlog.debug()
    noticeInfos = []
    lang = util.getLanguage(userId, clientId)
    ftlog.debug("getAllNotice->noticeInfos =", noticeConfigs)
    for noticeConf in noticeConfigs:
        noticeInfo = _getNoticeInfo(noticeConf, lang, readNotice)
        noticeInfos.append(noticeInfo)

    ftlog.debug("getAllNotice->noticeInfos =", noticeInfos)
    updateUnReadNotice(userId, clientId, noticeInfos)
    return noticeInfos


# def getOneActivityInfos(userId, acId, extendKey=0):
#     """
#     获取活动数据
#     """
#     acConfig = config.getActivityConfigById(acId)
#     if _isOneActivityEnable(userId, acConfig):
#         acClass = _getActivityClass(userId, acConfig)
#         if not acClass:
#             return None
#         acInfo = acClass.getActivityInfo(extendKey)
#         return acInfo
#     return None


def readNoticeById(userId, clientId, noticeConf):
    """
    读活动
    """
    noticeId = noticeConf["Id"]
    readNotice = _getNoticeReadInfo(userId)
    if noticeId in readNotice:
        return None
    readNotice.append(noticeId)
    _setNoticeReadInfo(userId, readNotice)
    updateUnReadNotice(userId, clientId, readNotice=readNotice)
    lang = util.getLanguage(userId, clientId)
    return _getNoticeInfo(noticeConf, lang, readNotice)


def doReadFishNotice(userId, clientId, noticeId):
    """
    读通知
    """
    message = MsgPack()
    message.setCmd("fishNoticeRead")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    message.setResult("noticeId", noticeId)
    noticeConf = config.getNoticeConf(noticeId)
    vipLevel = int(hallvip.userVipSystem.getUserVip(userId).vipLevel.level)
    level = util.getActivityCheckLevel(userId)
    clientIdNum = util.getClientIdNum(userId, clientId)
    acTemplate = config.getActivityTemplateByClientIdNum(clientIdNum, util.getLanguage(userId, clientId))
    if noticeConf and noticeConf.get("enable", 0) and _isNoticeEnable(userId, acTemplate, noticeConf, vipLevel, level):
        noticeData = readNoticeById(userId, clientId, noticeConf)
        if noticeData:
            message.setResult("notice", noticeData)
            message.setResult("code", 0)
        else:
            message.setResult("code", ActivityErrorCode.OtherError)
    else:
        message.setResult("code", ActivityErrorCode.OtherError)
    router.sendToUser(message, userId)


def doGetFishAllNoticeInfos(userId, clientId):
    """
    获取所有公告信息
    """
    message = MsgPack()
    message.setCmd("fishNoticeBtns")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    message.setResult("noticeBtns", getAllNotice(userId, clientId))
    router.sendToUser(message, userId)


def _getAllNoticeConfigs(userId, clientId):
    """
    获取所有开启的通知
    """
    clientIdNum = util.getClientIdNum(userId, clientId)
    noticeArray = []
    noticeConfigs = config.getNoticeConf()                      # 活动通知
    # 通知是否有效的参数
    vipLevel = int(hallvip.userVipSystem.getUserVip(userId).vipLevel.level)
    level = util.getActivityCheckLevel(userId)
    acTemplate = config.getActivityTemplateByClientIdNum(clientIdNum, util.getLanguage(userId, clientId))
    for noticeId in noticeConfigs:
        enable = noticeConfigs[noticeId]["enable"]
        if enable and _isNoticeEnable(userId, acTemplate, noticeConfigs[noticeId], vipLevel, level):
            noticeArray.append(noticeConfigs[noticeId])

    noticeArray = sorted(noticeArray, key=lambda noticeInfo: noticeInfo["order"])
    return noticeArray


def _isNoticeEnable(userId, acTemplate, noticeConf, userVIP, userLevel):
    """
    活动是否可以开启
    """
    ftlog.debug("_isNoticeEnable===>", userId, userVIP, userLevel, noticeConf["Id"])
    if not isActivityTemplateEnable(acTemplate, noticeConf["enable"]):
        return False
    # 提审版本不可见.
    if util.isVersionLimit(userId) and noticeConf.get("reviewVerLimit", 0) == 1:
        return False
    if noticeConf["limitVip"] > userVIP:
        return False
    if noticeConf["limitLevel"] > userLevel:
        return False
    clientVersion = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.clientVersion)
    lowClientVersion = noticeConf.get("lowClientVersion", "0.0.0")
    ftlog.debug("_isNoticeEnable===>", userId, "clientVerion", clientVersion, lowClientVersion)
    if not clientVersion or StrictVersion(str(clientVersion)) < StrictVersion(str(lowClientVersion)):
        return False
    return util.isTimeEffective(noticeConf["effectiveTime"])


def isActivityTemplateEnable(activityTemplate, enable):
    if not enable or len(enable) == 0:
        return False
    elif "ALL" in enable or activityTemplate in enable:
        return True
    return False


def _getNoticeInfo(noticeConf, lang, readNotice=None):
    """
    获取公告信息
    """
    noticeInfo = {}
    noticeInfo["Id"] = noticeConf["Id"]
    noticeInfo["name"] = config.getMultiLangTextConf(noticeConf["name"], lang=lang)
    noticeInfo["img"] = getNoticeImgUrl(noticeConf, lang)
    noticeInfo["read"] = 0 if noticeConf["Id"] not in readNotice else 1
    return noticeInfo


def getNoticeImgUrl(noticeConf, lang):
    imgUrl = ""
    if lang == "en":
        imgUrl = noticeConf.get("imgEN")
    return imgUrl or noticeConf["img"]


def _triggerUserLoginEvent(event):
    loginModuleUpdate(event.userId, event.clientId)


_inited = False


def initialize():
    ftlog.debug("newfish fish_notice_system initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from poker.entity.events.tyevent import EventUserLogin
        from newfish.game import TGFish
        TGFish.getEventBus().subscribe(EventUserLogin, _triggerUserLoginEvent)
    ftlog.debug("newfish fish_notice_system initialize end")