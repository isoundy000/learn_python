#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/22
"""
新手7日礼包
"""

import math
import time
import json
from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.entity.biz import bireport
from poker.protocol import router
from poker.entity.dao import userchip, userdata, gamedata, daobase
from newfish.entity.msg import GameMsg
from newfish.entity.redis_keys import MixData, GameData
from newfish.entity.config import FISH_GAMEID
from newfish.entity import config, util, module_tip


def checkNewbie7DaysGiftState(userId, redState):
    """
    检测新手7日礼包状态,0:未开启,1:已开启,2:已结束
    """
    newbie7DayGiftData = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.newbie7DayGiftData)
    if isinstance(newbie7DayGiftData, list) and len(newbie7DayGiftData) == 2:
        startTS, takenDays = newbie7DayGiftData
        curDayStartTS = util.getDayStartTimestamp(int(time.time()))
        curDayIdx = (curDayStartTS - startTS) / 86400
        daysConf = config.getNewbie7DaysGiftConf()
        # 最后一天已领取或是已过期
        if daysConf[-1].get("idx") in takenDays or curDayIdx > daysConf[-1].get("idx"):
            giftState = 2
        else:
            giftState = 1
    else:
        from newfish.entity.task.task_system_user import RedState
        giftState = 2 if redState >= RedState.Complete else 0
    return giftState


def queryNewbie7DayGift(userId, clientId):
    """
    返回新手礼包数据
    """
    module_tip.resetModuleTipEvent(userId, "newbie7DaysGift")
    message = MsgPack()
    message.setCmd("newbie_7_gift_query")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    message.setResult("clientId", clientId)
    redState = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.redState)
    message.setResult("redState", redState)
    giftState = checkNewbie7DaysGiftState(userId, redState)
    rewardsList = []
    curDayIdx = 0
    newbie7DayGiftData = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.newbie7DayGiftData)
    if giftState == 1 and isinstance(newbie7DayGiftData, list) and len(newbie7DayGiftData) == 2:
        startTS, takenDays = newbie7DayGiftData
        curTime = int(time.time())
        curDayStartTS = util.getDayStartTimestamp(curTime)
        curDayIdx = (curDayStartTS - startTS) / 86400
        daysConf = config.getNewbie7DaysGiftConf()
        # 最后一天已领取或是已过期
        if daysConf[-1].get("idx") in takenDays or curDayIdx > daysConf[-1].get("idx"):
            giftState = 2
            curDayIdx = 0
        else:
            for _val in daysConf:
                _idx = _val.get("idx")
                _state = 1 if _idx in takenDays else 0
                _rewards = _processRewards(_val.get("rewards"))
                rewardsList.append({"rewards": _rewards, "idx": _idx, "state": _state})
                if _state == 0 and _idx == curDayIdx:
                    module_tip.addModuleTipEvent(userId, "newbie7DaysGift", curDayIdx)
            message.setResult("nextRefreshTime", 86400 - (curTime - curDayStartTS))
    message.setResult("giftState", giftState)
    message.setResult("rewardsList", rewardsList)
    message.setResult("curDayIdx", curDayIdx)
    ignoreClient = config.isClientIgnoredConf("clientIds", clientId, clientId)
    message.setResult("isPureClient", 1 if ignoreClient else 0)
    router.sendToUser(message, userId)
    if ftlog.is_debug():
        ftlog.debug("newbie7DaysGift, userId =", userId, newbie7DayGiftData, "message =", message)


def takeNewbie7DaysGift(userId, clientId, idx):
    """
    领取7日礼包奖励
    """
    isIn, roomId, tableId, seatId = util.isInFishTable(userId)
    if isIn:
        mo = MsgPack()
        mo.setCmd("table_call")
        mo.setParam("action", "newbie_7_gift_take")
        mo.setParam("gameId", FISH_GAMEID)
        mo.setParam("clientId", clientId)
        mo.setParam("userId", userId)
        mo.setParam("idx", idx)
        mo.setParam("roomId", roomId)
        mo.setParam("tableId", tableId)
        mo.setParam("seatId", seatId)
        router.sendTableServer(mo, roomId)
        return
    level = util.getActivityCheckLevel(userId)
    fireCount = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.fireCount)
    takeGiftRewards(userId, clientId, idx, fireCount, level)


def takeGiftRewards(userId, clientId, idx, fireCount, level):
    code = 1
    rewards = []
    lang = util.getLanguage(userId)
    errTxt = config.getMultiLangTextConf("ID_NEWBIE_7_DAYS_GIFT_COND", lang)
    newbie7DayGiftData = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.newbie7DayGiftData)
    if isinstance(newbie7DayGiftData, list) and len(newbie7DayGiftData) == 2:
        startTS, takenDays = newbie7DayGiftData
        curDayStartTS = util.getDayStartTimestamp(int(time.time()))
        curDayIdx = (curDayStartTS - startTS) / 86400
        daysConf = config.getNewbie7DaysGiftConf()
        # 未过期前只能领取当前奖励
        if curDayIdx == idx and curDayIdx not in takenDays and curDayIdx <= daysConf[-1].get("idx"):
            rewards = daysConf[idx].get("rewards", [])
            if daysConf[idx].get("cond"):
                for key, val in daysConf[idx].get("cond", {}).iteritems():
                    # 玩家等级
                    if key == "level" and level < val:
                        errTxt = config.getMultiLangTextConf(daysConf[idx].get("des"), lang)
                        break
                    # 开火次数
                    elif key == "fire":
                        if not isinstance(val, list) or len(val) != 2:
                            break
                        if val[0] and fireCount.get(val[0]) < val[1]:
                            errTxt = config.getMultiLangTextConf(daysConf[idx].get("des"), lang)
                            break
                        if not val[0] and sum(fireCount.values()) < val[1]:
                            errTxt = config.getMultiLangTextConf(daysConf[idx].get("des"), lang)
                            break
                else:
                    code = 0
            else:
                code = 0
        if code == 0:
            errTxt = ""
            newbie7DayGiftData[-1].append(curDayIdx)
            gamedata.setGameAttr(userId, FISH_GAMEID, GameData.newbie7DayGiftData, json.dumps(newbie7DayGiftData))
            util.addRewards(userId, rewards, "BI_NFISH_NEWBIE_7DAYS_GIFT", param01=idx + 1)
            util.increaseExtraRechargeBonus(userId, daysConf[idx].get("rechargeBonus", 0))
    message = MsgPack()
    message.setCmd("newbie_7_gift_take")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    message.setResult("clientId", clientId)
    message.setResult("idx", idx)
    message.setResult("code", code)
    message.setResult("errTxt", errTxt)
    _rewards = _processRewards(rewards)
    message.setResult("rewards", _rewards)
    router.sendToUser(message, userId)
    if ftlog.is_debug():
        ftlog.debug("newbie7DaysGift, userId =", userId, newbie7DayGiftData, "message =", message)


def _processRewards(rewards):
    return rewards
    # _rewards = []
    # for val in rewards:
    #     _count = val["count"]
    #     if val["name"] == config.COUPON_KINDID:
    #         _count *= config.COUPON_DISPLAY_RATE
    #         _count = "%.2f" % _count
    #     _rewards.append({"name": val["name"], "count": _count})
    # return _rewards