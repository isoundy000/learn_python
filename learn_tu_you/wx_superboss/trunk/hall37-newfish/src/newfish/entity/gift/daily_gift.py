# -*- coding=utf-8 -*-
"""
每日礼包
"""
# @Author  : Kangxiaopeng
# @Time    : 2019/1/25

import time
import json

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.dao import gamedata, userchip
from poker.entity.configure import pokerconf
from hall.entity import hallvip
from newfish.entity import config, util, weakdata, vip_system, store
from newfish.entity.redis_keys import GameData, WeakData
from newfish.entity.config import FISH_GAMEID, VOUCHER_KINDID, BT_VOUCHER
from newfish.entity.msg import GameMsg
from newfish.entity.chest import chest_system
from newfish.entity import mail_system
from poker.entity.biz import bireport


def doSendGift(userId, clientId):
    """
    获取礼包数据
    """
    message = MsgPack()
    message.setCmd("fishDailyGift")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    vipLevel = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
    dailyGiftConf = config.getDailyGiftConf(clientId)
    lang = util.getLanguage(userId, clientId)
    giftInfo = []
    if not util.isVersionLimit(userId) and not util.isPurchaseLimit(userId) and util.isFinishAllNewbieTask(userId):
        for id, giftConf in dailyGiftConf.iteritems():
            vipRange = giftConf.get("vipRange", [0, 0])
            if vipRange[0] <= vipLevel <= vipRange[1]:
                hasBought = _isBought(userId, id)
                continuousDay = _getContinuousDay(userId, id)
                if continuousDay < len(giftConf.get("giftInfo", [])):
                    hasBought = 0
                dayIdx = _getGiftDayIdx(clientId, id, continuousDay)
                giftInfo.append(getGiftDetail(giftConf, hasBought, dayIdx, lang))
                if ftlog.is_debug():
                    ftlog.debug("doSendGift", userId, id, hasBought, continuousDay, dayIdx)
    message.setResult("btnVisible", bool(len(giftInfo) > 0))
    message.setResult("giftInfo", giftInfo)
    giftTestMode = config.getPublic("giftTestMode", None)
    if giftTestMode is None:
        giftTestMode = "a" if userId % 2 == 0 else "b"
    message.setResult("testMode", giftTestMode)
    router.sendToUser(message, userId)
    if ftlog.is_debug():
        ftlog.debug("doSendGift===>", userId, giftInfo)


def doBuyGift(userId, clientId, giftId, buyType, itemId=0):
    """
    购买礼包
    """
    if ftlog.is_debug():
        ftlog.debug("doBuyGift===>", userId, clientId, giftId, buyType)
    giftConf = config.getDailyGiftConf(clientId).get(str(giftId), {})
    continuousDay = _getContinuousDay(userId, giftId)
    dayIdx = _getGiftDayIdx(clientId, giftId, continuousDay)
    lang = util.getLanguage(userId, clientId)
    commonRewards = []
    chestRewards = []
    chestId = 0
    giftName = config.getMultiLangTextConf(giftConf["giftName"], lang=lang)
    # 使用其他货币(非direct)购买
    if giftConf.get("otherBuyType", {}).get(buyType):
        price = giftConf.get("otherBuyType", {}).get(buyType)
        # 代购券购买礼包
        if buyType == BT_VOUCHER:
            _consume = [{"name": VOUCHER_KINDID, "count": abs(price)}]
            _ret = util.consumeItems(userId, _consume, "BI_NFISH_BUY_ITEM_CONSUME", intEventParam=int(giftId), param01=int(giftId))
            if not _ret:
                code = 1
                _sendBuyGiftRet(userId, clientId, giftId, code, chestId, commonRewards, chestRewards)
                return
            else:
                code = 0
                vip_system.addUserVipExp(FISH_GAMEID, userId, abs(price) * 10, "BUY_PRODUCT",
                                         pokerconf.productIdToNumber(giftConf["productId"]),
                                         giftConf["productId"], rmbs=abs(price))
                # message = u"您使用%s代购券，购买商品【%s】, 获得%s" % (price, giftConf["giftName"], giftConf["giftName"])
                message = config.getMultiLangTextConf("ID_BUY_GIFT_RET_BY_VOUCHER", lang=lang).format(price, giftName, giftName)
                GameMsg.sendPrivate(FISH_GAMEID, userId, 0, message)
        else:
            code = 1
            _sendBuyGiftRet(userId, clientId, giftId, code, chestId, commonRewards, chestRewards)
            return
    elif buyType == config.BT_DIAMOND:
        price = giftConf.get("price", 0)
        price, isSucc = store.getUseRebateItemPrice(userId, itemId, price, buyType, giftId, clientId)
        code = 0
        if price > 0:
            consumeCount = 0
            if isSucc:
                store.autoConvertVoucherToDiamond(userId, price)
                consumeCount, final = userchip.incrDiamond(userId, FISH_GAMEID, -abs(price), 0,
                                                           "BI_NFISH_BUY_ITEM_CONSUME", int(giftId),
                                                           util.getClientId(userId), param01=giftId)
            if not isSucc or abs(consumeCount) != price:
                code = 1
                _sendBuyGiftRet(userId, clientId, giftId, code, chestId, commonRewards, chestRewards)
                return
    else:
        code = 0
        # message = u"您购买商品【%s】, 获得%s" % (giftConf["giftName"], giftConf["giftName"])
        message = config.getMultiLangTextConf("ID_BUY_GIFT_RET_BY_DRIECT", lang=lang).format(giftName, giftName)
        GameMsg.sendPrivate(FISH_GAMEID, userId, 0, message)

    # 记录存档
    boughtGift = weakdata.getDayFishData(userId, WeakData.buyFishDailyGift, [])
    boughtGift.append(giftId)
    weakdata.setDayFishData(userId, WeakData.buyFishDailyGift, json.dumps(boughtGift))

    # 记录每日礼包购买次数.
    buyFishDailyGiftTimes = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.buyFishDailyGiftTimes, {})
    buyFishDailyGiftTimes.setdefault(str(giftId), 0)
    buyFishDailyGiftTimes[str(giftId)] += 1
    gamedata.setGameAttr(userId, FISH_GAMEID, GameData.buyFishDailyGiftTimes, json.dumps(buyFishDailyGiftTimes))

    purchaseData = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.continuousPurchase, {})
    data = purchaseData.get(str(giftId), [0, 0])
    if util.getDayStartTimestamp(data[0]) + 24 * 60 * 60 < util.getDayStartTimestamp(int(time.time())):
        data[1] = 1
    else:
        data[1] += 1
    data[0] = int(time.time())
    purchaseData[str(giftId)] = data
    gamedata.setGameAttr(userId, FISH_GAMEID, GameData.continuousPurchase, json.dumps(purchaseData))
    # 发奖励
    mail_rewards = []
    giftInfo = giftConf.get("giftInfo", [])
    for gift in giftInfo:
        if gift["day_idx"] == dayIdx:
            for item in gift.get("items", []):
                if util.isChestRewardId(item["itemId"]):  # 宝箱
                    chestId = item["itemId"]
                    rewards = chest_system.getChestRewards(userId, chestId)
                    if buyType == BT_VOUCHER or buyType == config.BT_DIAMOND:
                        code = chest_system.deliveryChestRewards(userId, chestId, rewards, "BI_NFISH_BUY_ITEM_GAIN")
                    else:
                        code = 0
                        gamedata.incrGameAttr(userId, FISH_GAMEID, GameData.openChestCount, 1)
                        bireport.reportGameEvent("BI_NFISH_GE_CHEST_OPEN", userId, FISH_GAMEID, 0,
                                                 0, int(chestId), 0, 0, 0, [], util.getClientId(userId))
                    chestRewards.extend(rewards)
                    mail_rewards.extend([{"name": item["itemId"], "count": 1}])
                else:  # 资产/道具
                    rewards = [{"name": item["itemId"], "count": item["count"]}]
                    if buyType == BT_VOUCHER or buyType == config.BT_DIAMOND:
                        code = util.addRewards(userId, rewards, "BI_NFISH_BUY_ITEM_GAIN", int(giftId), param01=int(giftId))
                    else:
                        code = 0
                    commonRewards.extend(rewards)
                    mail_rewards.extend(rewards)
            break
    if buyType == BT_VOUCHER or buyType == config.BT_DIAMOND:
        _sendBuyGiftRet(userId, clientId, giftId, code, chestId, commonRewards, chestRewards)
    else:
        message = config.getMultiLangTextConf("ID_DO_BUY_GIFT_MSG", lang=lang) % giftName
        title = config.getMultiLangTextConf("ID_MAIL_TITLE_DAILY_GIFT", lang=lang)
        mail_system.sendSystemMail(userId, mail_system.MailRewardType.SystemReward, mail_rewards, message, title)
        doSendGift(userId, clientId)
    # 购买礼包事件
    from newfish.game import TGFish
    from newfish.entity.event import GiftBuyEvent
    event = GiftBuyEvent(userId, FISH_GAMEID, giftConf["productId"], buyType, giftId)
    TGFish.getEventBus().publishEvent(event)
    util.addProductBuyEvent(userId, giftConf["productId"], clientId)


def getGiftDetail(giftConf, hasBought, enableDayIdx, lang):
    """获取礼包的详细信息"""
    gift = {}
    gift["giftId"] = giftConf["giftId"]
    # gift["giftName"] = giftConf["giftName"]
    gift["giftName"] = config.getMultiLangTextConf(giftConf["giftName"], lang=lang)
    gift["productId"] = giftConf["productId"]
    gift["available"] = 0
    gift["price"] = giftConf["price"]
    gift["price_direct"] = giftConf.get("price_direct", 0)
    gift["price_diamond"] = giftConf.get("price_diamond", 0)
    gift["buyType"] = giftConf["buyType"]
    gift["otherBuyType"] = giftConf.get("otherBuyType", {})
    gift["otherProductInfo"] = {}
    # 特殊处理代购券商品数据
    from newfish.entity import store
    # gift["otherProductInfo"][BT_VOUCHER] = store.getVoucherProduct(gift["otherBuyType"])
    gift["otherProductInfo"] = store.getOtherBuyProduct(giftConf.get("otherBuyType", {}), giftConf["buyType"])
    gift["items"] = []
    for item in giftConf["giftInfo"]:
        newItems = []
        for v in item["items"]:
            newVal = config.rwcopy(v)
            if util.isChestRewardId(v["itemId"]):
                newVal["info"] = chest_system.getChestInfo(v["itemId"])
            newItems.append(newVal)
        gift["items"].append({item["day_idx"] + 1: newItems})
    gift["hasBought"] = hasBought
    gift["enableDayIdx"] = enableDayIdx
    return gift


def _isBought(userId, giftId):
    """
    礼包是否已购买
    """
    giftId = int(giftId)
    boughtGift = weakdata.getDayFishData(userId, WeakData.buyFishDailyGift, [])
    if giftId in boughtGift:
        return 1
    return 0


def _sendBuyGiftRet(userId, clientId, giftId, code, chestId, commonRewards, chestRewards):
    """
    发送购买礼包结果
    """
    message = MsgPack()
    message.setCmd("buyFishDailyGift")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    message.setResult("giftId", giftId)
    message.setResult("code", code)
    if code == 0:
        message.setResult("chestId", chestId)
        message.setResult("commonRewards", commonRewards)
        message.setResult("chestRewards", chestRewards)
    router.sendToUser(message, userId)
    doSendGift(userId, clientId)


def _getContinuousDay(userId, giftId):
    """持续购买的天数"""
    _checkContinuosPurchase(userId, giftId)
    giftId = str(giftId)
    purchaseData = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.continuousPurchase, {})       # 每日礼包连续购买记录
    continuousDay = purchaseData.get(giftId, [0, 0])[1]
    return continuousDay


def _getGiftDayIdx(clientId, giftId, continuousDay):
    """
    获取礼包可用的连购索引
    """
    giftInfo = config.getDailyGiftConf(clientId).get(str(giftId), {}).get("giftInfo", [])
    dayIdx = 0
    for item in giftInfo:
        if continuousDay >= item["day_idx"]:
            dayIdx = item["day_idx"]
    return dayIdx


def _checkContinuosPurchase(userId, giftId):
    """检查持续购买"""
    giftId = str(giftId)
    purchaseData = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.continuousPurchase, {})
    data = purchaseData.get(giftId, [0, 0])
    if util.getDayStartTimestamp(data[0]) + 24 * 60 * 60 + 60 < util.getDayStartTimestamp(int(time.time())):
        data[0] = int(time.time())
        data[1] = 0
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.continuousPurchase, json.dumps(purchaseData))


def _triggerChargeNotifyEvent(event):
    ftlog.info("daily_gift._triggerChargeNotifyEvent->",
               "userId =", event.userId,
               "gameId =", event.gameId,
               "rmbs =", event.rmbs,
               "productId =", event.productId,
               "clientId =", event.clientId)
    userId = event.userId
    productId = event.productId
    dailyGiftConf = config.getDailyGiftConf(event.clientId)
    for _, gift in dailyGiftConf.iteritems():
        if gift.get("productId") == productId:
            doBuyGift(userId, event.clientId, gift.get("giftId", 0), "direct")
            break


_inited = False


def initialize():
    ftlog.debug("newfish daily_gift initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from poker.entity.events.tyevent import ChargeNotifyEvent
        from hall.game import TGHall
        from newfish.game import TGFish
        from newfish.entity.event import NFChargeNotifyEvent
        TGHall.getEventBus().subscribe(ChargeNotifyEvent, _triggerChargeNotifyEvent)
        TGFish.getEventBus().subscribe(NFChargeNotifyEvent, _triggerChargeNotifyEvent)
    ftlog.debug("newfish daily_gift initialize end")