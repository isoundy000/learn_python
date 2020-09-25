# -*- coding=utf-8 -*-
"""
Created by lichen on 2019/12/23.
"""

import json
from datetime import datetime

from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from poker.entity.dao import onlinedata, sessiondata
from poker.protocol import router
from poker.util import strutil
from hall.entity import hallconf
from hall.entity.hallconf import HALL_GAMEID
from newfish.entity import config

_LEDS = {}


def canSendToUser(userId, clientId, led, userlang):
    """
    是否能发送给玩家
    """
    # led内容赋值 代码搜索[0, gameId, msgDict, scope, clientIds, isStopServer]
    isStopServer = led[5] if len(led) > 5 else False
    msgLang = dict(led[2]).get("lang", "zh")
    if userlang != msgLang:
        if ftlog.is_debug():
            ftlog.debug("led.canSendToUser LangFilter",
                        "userId=", userId,
                        "clientId=", clientId,
                        "led=", led,
                        "userlang=", userlang,
                        "msgLang=", msgLang)
        return False

    if not isStopServer and clientId in config.getPublic("closeLedClientIds", []):
        if ftlog.is_debug():
            ftlog.debug("led.canSendToUser ClientIdClosed",
                        "userId=", userId,
                        "clientId=", clientId,
                        "led=", led)
        return False

    clientIdFilter = led[4]
    if clientIdFilter and clientId in clientIdFilter:
        if ftlog.is_debug():
            ftlog.debug("led.canSendToUser ClientIdFilter",
                        "userId=", userId,
                        "clientId=", clientId,
                        "led=", led)
        return False

    return True


def doSendLedToUser(userId):
    """
    发送LED消息给玩家（由客户端心跳消息触发，大概15s一次）
    """
    from newfish.entity import util
    gameIdList = onlinedata.getGameEnterIds(userId)
    lastGameId = onlinedata.getLastGameId(userId)
    # if not HALL_GAMEID in gameIdList:
    #     gameIdList.append(HALL_GAMEID)
    # if not lastGameId in gameIdList:
    #     gameIdList.append(lastGameId)

    clientId = sessiondata.getClientId(userId)
    gameIdInClientId = strutil.getGameIdFromHallClientId(clientId)
    if not gameIdInClientId in gameIdList:
        gameIdList.append(gameIdInClientId)
    lang = util.getLanguage(userId, clientId)
    if ftlog.is_debug():
        ftlog.debug("led.doSendLedToUser userId=", userId,
                    "gameIdList=", gameIdList,
                    "clientId=", clientId,
                    "gameIdInClientId=", gameIdInClientId,
                    "lastGameId=", lastGameId)
    for gameId in gameIdList:
        try:
            leds = getLedMsgList(gameId)
            if ftlog.is_debug():
                ftlog.debug("led.doSendLedToUser gameId=", gameId,
                            "userId=", userId,
                            "clientId=", clientId,
                            "leds=", leds)
            if leds:
                for led in leds:
                    if canSendToUser(userId, clientId, led, lang):
                        msgDict = led[2]
                        mo = MsgPack()
                        mo.setCmd("led")
                        for k, v in msgDict.iteritems():
                            mo.setResult(k, v)
                        mo.setResult("scope", led[3])
                        router.sendToUser(mo, userId)
        except:
            ftlog.error("error leds:", leds)


def decodeMsgV3(gameId, msgstr):
    try:
        if len(msgstr) > 0 and msgstr[0] in ("{", "["):
            d = json.loads(msgstr)
            if not isinstance(d, dict):
                return None
            d["gameId"] = gameId
            return d
    except:
        if ftlog.is_debug():
            ftlog.error()
        return None


def decodeMsg(gameId, msgstr):
    msgDict = decodeMsgV3(gameId, msgstr)
    if msgDict:
        return msgDict

    return {
        "text": [{"color": "FFFFFF", "text": msgstr, "gameId": gameId}]
    }


def sendLed(gameId, msgstr, ismgr=0, scope="hall", clientIds=None, isStopServer=False):
    """
    发送LED
    @param gameId: 游戏gameId，gameId部分起到了过滤/范围的作用
    @param msgstr: LED消息内容
    @param ismgr: 是否是GDSS发的，默认非GDSS发送的
    @param scope: string类型，LED显示级别/范围，详见http://192.168.10.93:8090/pages/viewpage.action?pageId=1281059
        scope摘要
        - "6": 只在地主插件里面播放
        - "hall": 在大厅界面播放
        - "hall6": 在大厅和地主插件里面播放
        - "global": 在大厅任何界面都播放
    @param clientIds: 不发送的clientId集合，默认全发送
    @param isStopServer: 是否是停服led
    """
    assert isinstance(msgstr, basestring)
    clientIds = clientIds or []

    closeLedGameIds = hallconf.getPublicConf("closeLedGameIds", [])

    if not isStopServer and closeLedGameIds and gameId in closeLedGameIds:
        if ftlog.is_debug():
            ftlog.debug("led.sendLed closed",
                        "gameId=", gameId,
                        "msgstr=", msgstr,
                        "scope=", scope,
                        "ismgr=", ismgr,
                        "isStopServer=", isStopServer)
        return None

    if ftlog.is_debug():
        ftlog.debug("led.sendLed gameId=", gameId,
                    "msgstr=", msgstr,
                    "scope=", scope,
                    "ismgr=", ismgr,
                    "isStopServer=", isStopServer)

    try:
        msgDict = decodeMsg(gameId, msgstr)
        # 每条LED所包含的数据内容
        msg = [0, gameId, msgDict, scope, clientIds, isStopServer]
        leds = _LEDS
        kmsg = "m:" + str(gameId)
        ktime = "t:" + str(gameId)

        if ismgr:
            leds[kmsg] = [msg]
            leds[ktime] = datetime.now()
        else:
            if not kmsg in leds:
                leds[kmsg] = []
                leds[ktime] = None

            timeout = leds[ktime]
            if timeout != None:
                timeouts = hallconf.getHallPublic().get("led.manager.timeout", 30)
                secondes = (datetime.now() - timeout).seconds
                if secondes < timeouts:
                    if ftlog.is_debug():
                        ftlog.warn("led.sendLed Failed gameId=", gameId,
                                   "msgstr=", msgstr,
                                   "ismgr=", ismgr,
                                   "scope=", scope,
                                   "timeouts=", timeouts,
                                   "secondes=", secondes)
                    return
            msgq = leds[kmsg]
            msgq.append(msg)
            ledlength = 3
            leds[ktime] = datetime.now()
            leds[kmsg] = msgq[-ledlength:]

        if ftlog.is_debug():
            ftlog.debug("led.sendLed gameId=", gameId,
                        "msgstr=", msgstr,
                        "ismgr=", ismgr,
                        "msg=", msg,
                        "leds=", _LEDS)
        return msg
    except:
        ftlog.error("led.sendLed gameId=", gameId,
                    "msgstr=", msgstr,
                    "scope=", scope,
                    "ismgr=", ismgr,
                    "leds=", _LEDS)
        return None


def getLedMsgList(gameId):
    """根据游戏gameId获取Led信息"""
    leds = _LEDS
    kmsg = "m:" + str(gameId)
    ktime = "t:" + str(gameId)
    msgList = leds.get(kmsg, [])
    if msgList:
        timeouts = hallconf.getHallPublic().get("led.manager.timeout", 30)  # 从测试数据看客户端heartBeat间隔时间有10秒误差，也就是在30到40秒之间
        sendTime = leds.get(ktime)
        isTimeout = sendTime and (datetime.now() - sendTime).seconds >= timeouts
        if ftlog.is_debug():
            ftlog.debug("led.getLedMsgList gameId=", gameId,
                        "leds=", leds,
                        "sendTime=", sendTime,
                        "nowTime=", datetime.now(),
                        "isTimeout=", isTimeout)
        if isTimeout:
            return []
    return msgList


def sendUserNewLed(userId, clientId):
    """发送新手Led"""
    import random
    from hall.entity import hallranking
    import time
    from newfish.entity.config import FISH_GAMEID
    from poker.entity.dao import gamedata
    from newfish.entity.redis_keys import GameData
    from newfish.entity import util
    if gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.hasSendUserNewLed) == 0:
        lang = util.getLanguage(userId, clientId)
        names = config.getRobotConf("names")
        name = random.choice(names)
        msg_1 = config.getMultiLangTextConf("ID_LED_NEWBIE_TASK_1", lang=lang) % name
        msg_3 = config.getMultiLangTextConf("ID_LED_NEWBIE_TASK_4", lang=lang) % name
        msg_4 = config.getMultiLangTextConf("ID_LED_NEWBIE_TASK_6", lang=lang) % name
        msg_5 = config.getMultiLangTextConf("ID_LED_NEWBIE_TASK_7", lang=lang) % name
        rankingList = hallranking.rankingSystem.getTopN(config.RANK_MATCH_WZZB, 1, int(time.time()))
        if rankingList and len(rankingList.rankingUserList) > 0:
            user = rankingList.rankingUserList[0]
            name = util.getNickname(user.userId)
        msg_2 = config.getMultiLangTextConf("ID_LED_NEWBIE_TASK_2", lang=lang) % name
        mo = MsgPack()
        mo.setCmd("sendUserNewLed")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("msg_1", msg_1)
        mo.setResult("msg_2", msg_2)
        mo.setResult("msg_3", msg_3)
        mo.setResult("msg_4", msg_4)
        mo.setResult("msg_5", msg_5)
        router.sendToUser(mo, userId)
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.hasSendUserNewLed, json.dumps(1))