#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/8/26
"""
升级礼包
"""

import json
import time

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack

from poker.entity.biz import bireport
from poker.protocol import router
from poker.entity.dao import gamedata, userchip
from newfish.entity import config, util, store, weakdata
from newfish.entity.redis_keys import GameData, WeakData
from newfish.entity.config import FISH_GAMEID


def doSendLevelGift(userId, clientId):
    """
    获取升级礼包数据
    """
    message = MsgPack()
    message.setCmd("levelGiftData")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    giftInfo = []
    if not util.isVersionLimit(userId) and not util.isPurchaseLimit(userId) and util.isFinishAllNewbieTask(userId):
        levelGiftConf = config.getLevelGiftConf()
        gunLv = util.getGunLevelVal(userId, config.MULTIPLE_MODE)
        for giftId, giftConf in levelGiftConf.iteritems():
            if _isBought(userId, giftId):
                continue
            if not (giftConf["minLevel"] <= gunLv <= giftConf["maxLevel"]):
                continue
            now = int(time.time())
            timeout = giftConf["showTime"] * 60
            data = weakdata.getDayFishData(userId, WeakData.LevelUpCountDownData, [])
            if not data:
                weakdata.setDayFishData(userId, WeakData.LevelUpCountDownData, json.dumps([giftId, now]))
            else:
                if data[0] == giftId:
                    if timeout - (now - data[1]) > 0:
                        timeout = timeout - (now - data[1])
                    else:
                        timeout = 0
                else:
                    weakdata.setDayFishData(userId, WeakData.LevelUpCountDownData, json.dumps([giftId, now]))
            giftInfo.append(getGiftDetail(giftConf, util.getLanguage(userId, clientId), timeout))
    message.setResult("giftInfo", giftInfo)
    router.sendToUser(message, userId)
    return giftInfo


def doBuyLevelGift(userId, clientId, buyType, productId, itemId=0):
    """
    购买升级礼包
    """
    levelGift = config.getLevelGiftConf()
    giftId = 0
    for val in levelGift.values():
        if val.get("productId") == productId:
            giftId = val["giftId"]
            break
    if giftId == 0:
        return
    levelGiftConf = levelGift.get(str(giftId), {})
    commonRewards = []
    if _isBought(userId, giftId):
        code = 1
    elif buyType == config.BT_DIAMOND:
        price = levelGiftConf.get("discountPrice", 0)
        price, isSucc = store.getUseRebateItemPrice(userId, itemId, price, buyType, productId, clientId)
        code = 0
        if price > 0:
            consumeCount = 0
            if isSucc:                                                      # 用优惠券
                store.autoConvertVoucherToDiamond(userId, price)
                consumeCount, final = userchip.incrDiamond(userId, FISH_GAMEID, -abs(price), 0,
                    "BI_NFISH_BUY_LEVEL_GIFT_CONSUME", int(config.DIAMOND_KINDID), util.getClientId(userId), param01=productId)
            if not isSucc or abs(consumeCount) != price:
                code = 2
                _sendBuyLevelGiftRet(userId, clientId, productId, code, commonRewards)
                return
        else:
            code = 4
    else:
        code = 3
    if code == 0:
        # 记录存档
        boughtGift = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.buyLevelGift, [])
        boughtGift.append(int(giftId))
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.buyLevelGift, json.dumps(boughtGift))
        # 升级炮倍率
        gunLv = util.getGunLevelVal(userId, config.MULTIPLE_MODE)
        if gunLv < levelGiftConf["levelUp"]:
            gunLevel = gunLv
            for level in config.getGunLevelKeysConf(config.MULTIPLE_MODE):
                value = config.getGunLevelConf(level, config.MULTIPLE_MODE)
                if value["levelValue"] == levelGiftConf["levelUp"]:
                    gunLevel = level
                    break
            gamedata.setGameAttr(userId, FISH_GAMEID, GameData.gunLevel_m, gunLevel)
            from newfish.game import TGFish
            from newfish.entity.event import GunLevelUpEvent
            event = GunLevelUpEvent(userId, FISH_GAMEID, gamedata.getGameAttr(userId, FISH_GAMEID, GameData.level), gunLevel, config.MULTIPLE_MODE)
            TGFish.getEventBus().publishEvent(event)
            bireport.reportGameEvent("BI_NFISH_GE_LEVEL_UP", userId, FISH_GAMEID, 0, 0, 0, config.MULTIPLE_MODE, 0, 0, [gunLevel], util.getClientId(userId))
        # 发奖励
        rewards = levelGiftConf.get("rewards", [])
        # 资产/道具
        code = util.addRewards(userId, rewards, "BI_NFISH_BUY_ITEM_GAIN", int(giftId), param01=int(giftId))
        commonRewards.extend(rewards)
    _sendBuyLevelGiftRet(userId, clientId, productId, code, commonRewards)
    util.addProductBuyEvent(userId, productId, clientId)


def getGiftDetail(giftConf, lang, timeout):
    """获取升级礼包详情"""
    gift = {}
    gift["giftId"] = giftConf["giftId"]
    gift["giftName"] = config.getMultiLangTextConf(giftConf["giftName"], lang=lang)
    gift["productId"] = giftConf["productId"]
    gift["fromLevel"] = 0 if giftConf["levelUp"] == 0 else giftConf["minLevel"]
    gift["levelUp"] = giftConf["levelUp"]
    gift["showTime"] = timeout
    gift["buyType"] = giftConf["buyType"]
    gift["priceDiamond"] = giftConf.get("priceDiamond", 0)
    gift["discountPrice"] = giftConf.get("discountPrice", 0)
    gift["rewards"] = giftConf.get("rewards")
    return gift


def _isBought(userId, giftId):
    """
    礼包是否已购买
    """
    giftId = int(giftId)
    boughtGift = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.buyLevelGift, [])
    if giftId in boughtGift:
        return 1
    return 0


def _sendBuyLevelGiftRet(userId, clientId, giftId, code, commonRewards):
    """
    发送购买礼包结果
    """
    message = MsgPack()
    message.setCmd("buyLevelGift")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    message.setResult("productId", giftId)
    message.setResult("code", code)
    if code == 0:
        message.setResult("commonRewards", commonRewards)
    router.sendToUser(message, userId)
    doSendLevelGift(userId, clientId)


def _triggerLevelUpEvent(event):
    """
    炮台升级/升倍率事件弹出升级礼包
    """
    userId = event.userId
    clientId = util.getClientId(userId)
    mode = event.gameMode
    if mode != 1:
        return
    gunLv = util.getGunLevelVal(userId, mode)
    levelGiftConf = config.getLevelGiftConf()
    for giftId, giftConf in levelGiftConf.iteritems():
        if not giftConf["minLevel"] <= gunLv <= giftConf["maxLevel"]:
            continue
        if not _isBought(userId, giftId):
            doSendLevelGift(userId, clientId)
            break


_inited = False


def initialize():
    ftlog.debug("newfish level_gift initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from newfish.game import TGFish
        from newfish.entity.event import GunLevelUpEvent
        TGFish.getEventBus().subscribe(GunLevelUpEvent, _triggerLevelUpEvent)
    ftlog.debug("newfish level_gift initialize end")