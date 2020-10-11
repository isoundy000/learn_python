# -*- coding=utf-8 -*-

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.entity.dao import gamedata
from poker.protocol import router
from newfish.entity import config, weakdata, module_tip, util
from newfish.entity.redis_keys import GameData
from newfish.entity.config import FISH_GAMEID
from newfish.entity.chest import chest_system

import json
import time

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.dao import gamedata
from hall.entity import hallvip, hallstore
from hall.entity.hallconf import HALL_GAMEID
from hall.servers.util.store_handler import StoreHelper
from newfish.entity import config, weakdata, util
from newfish.entity.config import FISH_GAMEID, BT_VOUCHER
from newfish.entity.redis_keys import GameData
from newfish.entity.chest import chest_system


def sendFishCheckinInfo(userId, continueWindow=0):
    """
    发送签到详情
    :param continueWindow: 0:用户点击签到请求 1:客户端登录时自动请求
    """
    if util.isVersionLimit(userId):
        return
    checkinDay = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.checkinDay)
    isCheckin = weakdata.getDayFishData(userId, "isCheckin", 0)
    code = 1
    if (continueWindow and isCheckin):
        code = 2
    elif util.isFinishAllNewbieTask(userId):
        code = 0
        if not isCheckin:
            if checkinDay == len(config.getCheckinConf()):
                checkinDay = 0
                gamedata.setGameAttr(userId, FISH_GAMEID, GameData.checkinDay, checkinDay)
            module_tip.addModuleTipEvent(userId, "checkin", checkinDay)
    mo = MsgPack()
    mo.setCmd("fishCheckin")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("loginDays", gamedata.getGameAttr(userId, FISH_GAMEID, GameData.loginDays))
    mo.setResult("day", checkinDay if isCheckin else checkinDay + 1)
    mo.setResult("checkin", isCheckin)
    rewards = []
    for rewardConf in config.getCheckinConf().values():
        if util.isChestRewardId(rewardConf["shareReward"]["name"]):
            rewards.append(rewardConf["shareReward"])
        else:
            rewards.append(rewardConf["normalReward"])
    mo.setResult("rewards", rewards)
    mo.setResult("continueWindow", continueWindow)
    mo.setResult("code", code)
    router.sendToUser(mo, userId)

def getCoinStore(userId, clientId):
    """
    金币商店
    """
    isVerLimited = util.isVersionLimit(userId)
    coinItems = []
    coinStoreConf = config.getStoreConf(clientId).get("coinStore", {})
    coinStoreTab = {"name": u"购买金币", "subStore": "coin", "iconType": "coin"}
    vipLevel = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
    buyCoinCountDict = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.buyCoinCount, {})
    platformOS = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.platformOS)
    if not util.isVersionLimit(userId) or platformOS == "android":
        for productId, product in coinStoreConf.iteritems():
            if isInvalidePruduct(isVerLimited, product):
                continue
            buyCoinCount = buyCoinCountDict.get(productId, 0)
            if buyCoinCount > 0:
                index = 1
                if vipLevel >= product["additionVip"]:
                    index = 2
            else:
                index = 0
            if index >= len(product["name"]) or index >= len(product["addition"]) or index >= len(product["count"]):
                index = 0
            data = {
                "id": productId,
                "name": product["name"][index],
                "nameurl": "",
                "price": product["price"],
                "priceurl": "",
                "desc": "",
                "discount": [],
                "pic": product["pic"],
                "tag": product["tag"],
                "buy_type": product["buyType"],
                "price_diamond": 0,
                "addition": product["addition"][index],
                "count": product["count"][index],
                "label": product["label"][index],
                "other_buy_type": product.get("otherBuyType", {}),
                "item_id": product.get("itemId", 0),
                "otherProductInfo": {BT_VOUCHER: getVoucherProduct(product.get("otherBuyType", {}))}
            }
            coinItems.append(data)
    coinStoreTab["items"] = coinItems
    return coinStoreTab


def getPearlStore(userId, clientId):
    """
    珍珠商店
    """
    isVerLimited = util.isVersionLimit(userId)
    pearlItems = []
    pearlStoreConf = config.getStoreConf(clientId).get("pearlStore", {})
    pearlStoreTab = {"name": u"购买珍珠", "subStore": "pearl", "iconType": "pearl"}
    vipLevel = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
    buyPearlCountDict = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.buyPearlCount, {})
    platformOS = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.platformOS)
    if not util.isVersionLimit(userId) or platformOS == "android":
        for productId, product in pearlStoreConf.iteritems():
            if isInvalidePruduct(isVerLimited, product):
                continue
            buyPearlCount = buyPearlCountDict.get(productId, 0)
            if buyPearlCount > 0:
                index = 1
                if vipLevel >= product["additionVip"]:
                    index = 2
            else:
                index = 0
            data = {
                "id": productId,
                "name": product["name"][index],
                "nameurl": "",
                "price": product["price"],
                "priceurl": "",
                "desc": "",
                "discount": [],
                "pic": product["pic"],
                "tag": product["tag"],
                "buy_type": product["buyType"],
                "price_diamond": 0,
                "addition": product["addition"][index],
                "item_id": product["itemId"],
                "count": product["count"][index],
                "other_buy_type": product.get("otherBuyType", {}),
                "otherProductInfo": {BT_VOUCHER: getVoucherProduct(product.get("otherBuyType", {}))}
            }
            pearlItems.append(data)
    pearlStoreTab["items"] = pearlItems
    return pearlStoreTab

def isInvalidePruduct(isVerLimited, product):
    if product.get("visible", 1) == 0:  # 隐藏商品不向客户端发送
        return True
    if isVerLimited and product.get("reviewVerLimit", 0) == 1:  # 限制的版本不向客户端发送
        return True
    return False

def getVoucherProduct(otherBuyType):
    """
    获取相应的代购券商品数据
    """
    voucherProductInfo = []
    for k, v in otherBuyType.iteritems():
        if str(k) == BT_VOUCHER:
            coinStoreConf = config.getStoreConf().get("coinStore", {})
            for productId, product in coinStoreConf.iteritems():
                if product.get("type") == BT_VOUCHER and product.get("price", 0) == int(v):
                    name = product.get("name")[0] if len(product.get("name")) > 0 else ""
                    voucherProductInfo = [productId, name, product.get("price")]
                    break
            break
    return voucherProductInfo


def _main():
    from newfish.entity import checkin, store
    checkin.sendFishCheckinInfo = sendFishCheckinInfo
    store.getCoinStore = getCoinStore
    store.getPearlStore = getPearlStore


from freetime.core.timer import FTLoopTimer
FTLoopTimer(0.1, 0, _main).start()