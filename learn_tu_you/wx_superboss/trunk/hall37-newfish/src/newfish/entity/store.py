# -*- coding=utf-8 -*-
"""
Created by lichen on 16/11/14.

原则上每个商城对应一个BaseStoreShop，每个BaseStoreShop对应一个BaseProduct，
但是HotStoreShop中的商品根据pt类型对应不用的BaseProduct!
"""

import json
import time
import random
import copy
from distutils.version import StrictVersion

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
import poker.util.timestamp as pktimestamp
from poker.entity.dao import gamedata, userchip, daobase
from hall.entity import hallvip, hallstore, hallitem
from hall.entity.hallconf import HALL_GAMEID
from hall.servers.util.store_handler import StoreHelper
from newfish.entity import config, weakdata, util, vip_system
from newfish.entity.config import FISH_GAMEID, BT_VOUCHER, vipConf
from newfish.entity.redis_keys import GameData, MixData, WeakData, UserData
from newfish.entity.chest import chest_system


# 奖券兑换商品库存量状态.
exchangeTipData = [
    {"state": 0, "txt": "ID_EXCHANGE_ENOUGH_STOCK", "color": "57fbb3"},     # 库存充足
    {"state": 1, "txt": "ID_EXCHANGE_LIMITED_STOCK", "color": "fa5f24"},    # 库存紧张
    {"state": 2, "txt": "ID_EXCHANGE_UNDER_STOCK", "color": "d3cee8"}       # 今日无货
]


# 商城标签类型.
class StoreTabType:
    """商城类型"""
    STT_HOT = 0             # 热卖
    STT_COIN = 1            # 金币
    STT_DIAMOND = 2         # 钻石
    STT_PEARL = 3           # 珍珠
    STT_COUPON = 4          # 奖券
    STT_ITEM = 5            # 道具
    STT_GUNSKIN = 6         # 皮肤炮
    STT_BULLET = 7          # 招财珠
    STT_CHEST = 8           # 宝箱
    STT_TIMELIMITED = 9     # 限时
    STT_CONVERT = 10       # 月度兑换


# 商城标签商品配置.
storeTabConfName = {
    StoreTabType.STT_HOT: "hotStore",
    StoreTabType.STT_CHEST: "chestStore",
    StoreTabType.STT_ITEM: "itemStore",
    StoreTabType.STT_COIN: "coinStore",
    StoreTabType.STT_DIAMOND: "diamondStore",
    StoreTabType.STT_COUPON: "couponStore",
    StoreTabType.STT_GUNSKIN: "gunSkinStore",
    StoreTabType.STT_BULLET: "bulletStore",
    StoreTabType.STT_TIMELIMITED: "timeLimitedStore",
    StoreTabType.STT_CONVERT: "exchangeStore"
}


def getStoreTabsFish(userId, clientId, actionType, isRefresh=False):
    """
    捕鱼商店
    """
    tabs = []
    if actionType == StoreTabType.STT_HOT:          # 热卖商城
        hotStoreTab = HotStoreShop(userId, clientId, actionType).getStore()
        if hotStoreTab:
            tabs.append(hotStoreTab)
    elif actionType == StoreTabType.STT_CHEST:      # 宝箱商城
        chestStoreTab = ChestStoreShop(userId, clientId, actionType).getStore()
        if chestStoreTab:
            tabs.append(chestStoreTab)
    elif actionType == StoreTabType.STT_ITEM:       # 道具商城
        itemStoreTab = ItemStoreShop(userId, clientId, actionType).getStore()
        if itemStoreTab:
            tabs.append(itemStoreTab)
    elif actionType == StoreTabType.STT_COIN:       # 金币
        coinStoreTab = CoinStoreShop(userId, clientId, actionType).getStore()
        if coinStoreTab:
            tabs.append(coinStoreTab)
    elif actionType == StoreTabType.STT_DIAMOND:    # 钻石
        diamondStoreTab = DiamondStoreShop(userId, clientId, actionType).getStore()
        if diamondStoreTab:
            tabs.append(diamondStoreTab)
    elif actionType == StoreTabType.STT_PEARL:      # 珍珠
        pearlStoreTab = getPearlStore(userId, clientId)
        if pearlStoreTab:
            tabs.append(pearlStoreTab)
    elif actionType == StoreTabType.STT_COUPON:     # 奖券
        couponStoreTab = CouponStoreShop(userId, clientId, actionType).getStore()
        if couponStoreTab:
            tabs.append(couponStoreTab)
    elif actionType == StoreTabType.STT_GUNSKIN:    # 火炮皮肤
        gunSkinStoreTab = getGunSkinStore(userId, clientId)
        if gunSkinStoreTab:
            tabs.append(gunSkinStoreTab)
    elif actionType == StoreTabType.STT_BULLET:     # 招财珠
        bulletStoreTab = getBulletStore(userId, clientId)
        if bulletStoreTab:
            tabs.append(bulletStoreTab)
    elif actionType == StoreTabType.STT_TIMELIMITED:    # 限时商城
        timeLimitedStoreTab = getTimeLimitedStore(userId, clientId, isRefresh)
        if timeLimitedStoreTab:
            tabs.append(timeLimitedStoreTab)
    elif actionType == StoreTabType.STT_CONVERT:       # 兑换商城
        exchangeStoreTab = ExchangeStoreShop(userId, clientId, actionType).getStore()
        if exchangeStoreTab:
            tabs.append(exchangeStoreTab)
    mo = MsgPack()
    mo.setCmd("store_config_fish")
    mo.setResult("action", "update")
    mo.setResult("actionType", actionType)
    mo.setResult("tabs", tabs)
    router.sendToUser(mo, userId)
    # 宝箱免费次数存在多次,所以需要在获取商城时检测宝箱商城时候存在红点.
    updateChestStoreModuleTip(userId, util.getUserLevel(userId), util.getGunLevelVal(userId, config.MULTIPLE_MODE))


def isInvalidePruduct(isVerLimited, product, level, gunLevel, clientVersion, ownGunSkinSkins=None):
    """
    不需要发送给客户端的商品
    :param isVerLimited: 是否限制True|False
    :param product: 商店
    :param level: 玩家等级
    :param clientVersion: 客户端版本
    :param ownGunSkinSkins: 自己皮肤炮皮肤
    """
    # 隐藏商品不向客户端发送
    if product.get("limitCond", {}).get("visible", 1) == 0:
        return True
    # 限制的版本不向客户端发送
    if isVerLimited and product.get("limitCond", {}).get("reviewVerLimit", 0) == 1:
        return True
    # 玩家等级太低
    if level < product.get("limitCond", {}).get("levelLimit", 0):
        return True
    # 玩家炮台等级太低
    if gunLevel < product.get("limitCond", {}).get("gunLevelLimit", 0):
        return True
    # 客户端版本太低
    lowVersion = product.get("limitCond", {}).get("lowVersion")
    if lowVersion and clientVersion and StrictVersion(str(lowVersion)) > StrictVersion(str(clientVersion)):
        return True
    # 皮肤类商品如果玩家已拥有皮肤商品对应的皮肤，则该商品不显示.
    if product.get("extendData", {}).get("itemType") == 5 and ownGunSkinSkins and product.get("itemId") in ownGunSkinSkins:
        return True
    curTs = int(time.time())
    # 商品是否在有效期内，有效期内可见.
    if product.get("extendData", {}).get("activityPrice", {}).get("effectiveTime"):
        startTime = product["extendData"]["activityPrice"]["effectiveTime"].get("start")
        endTime = product["extendData"]["activityPrice"]["effectiveTime"].get("end")
        if util.getTimestampFromStr(startTime) > curTs or curTs > util.getTimestampFromStr(endTime):
            return True
    # 商品在显示时间内可见，用于处理折扣商品.
    if product.get("limitCond", {}).get("visibleTime", {}):
        startTime = product["limitCond"]["visibleTime"].get("start")
        endTime = product["limitCond"]["visibleTime"].get("end")
        if util.getTimestampFromStr(startTime) > curTs or curTs > util.getTimestampFromStr(endTime):
            return True
    if product.get("activityPrice"):
        curTs = int(time.time())
        startTime = util.getTimestampFromStr(product["activityPrice"]["effectiveTime"]["start"])
        endTime = util.getTimestampFromStr(product["activityPrice"]["effectiveTime"]["end"])
        if curTs < startTime or curTs > endTime:
            return True
    return False


def getVoucherProduct(v):
    """
    获取相应的代购券商品数据
    """
    voucherProductInfo = []
    diamondStoreConf = config.getStoreConf().get("diamondStore", {})
    for productId, product in diamondStoreConf.iteritems():
        if product.get("extendData", {}).get("type") == BT_VOUCHER and product.get("price", 0) == int(v):
            name = product.get("name")[0] if len(product.get("name")) > 0 else ""
            voucherProductInfo = [productId, name, product.get("price")]
            break
    return voucherProductInfo


def getDiamondBuyProduct():
    """
    获取相应的钻石商品数据
    """
    diamondProductInfo = []
    diamondStoreConf = config.getStoreConf().get("diamondStore", {})
    for productId, product in diamondStoreConf.iteritems():
        if product.get("extendData", {}).get("type") == config.BT_DIAMOND:
            name = product.get("name")[0] if len(product.get("name")) > 0 else ""
            count = product.get("count")[0] if len(product.get("count")) > 0 else 0
            diamondProductInfo.append([productId, name, product.get("price"), count])
    return diamondProductInfo


def getOtherBuyProduct(otherBuyType, buyType):
    """
    获取相应的代购券和钻石商品数据
    """
    otherBuyDict = {}
    for k, v in otherBuyType.iteritems():
        if str(k) == BT_VOUCHER:
            otherBuyDict[BT_VOUCHER] = getVoucherProduct(v)
    #     elif str(k) == config.BT_DIAMOND:
    #         otherBuyDict[config.BT_DIAMOND] = getDiamondBuyProduct()
    # if buyType == config.BT_DIAMOND and not otherBuyDict.has_key(config.BT_DIAMOND):
    #     otherBuyDict[config.BT_DIAMOND] = getDiamondBuyProduct()
    return otherBuyDict


def CreateProduct(storeShop, actionType, productId, product, userId, clientId=None):
    """
    创建商品
    """
    # 按照商品类型或是商城类型确定具体商品类.
    productId = str(productId)
    productObj = None
    if not hasattr(product, "pt"):
        return
    # 更新热销商城商品的extendData和limitCond.
    if actionType == StoreTabType.STT_HOT and (product.get("extendData") or product.get("limitCond")):
        if product.pt in ["diamond", "coin", "coupon", "item", "chest"]:
            confName = "%sStore" % product.pt
            productConf = config.rwcopy(config.getStoreConf(clientId).get(confName, {}).get("items", {}).get(productId))
            if product.get("extendData"):
                productConf["extendData"] = product["extendData"]
            if product.get("limitCond"):
                productConf["limitCond"] = product["limitCond"]
        else:
            productConf = product
            ftlog.error("hot store product type error! userId =", userId, "productId =", productId)
    else:
        productConf = product
    if product.pt == "diamond" or (not product.pt and actionType == StoreTabType.STT_DIAMOND):
        productObj = DiamondProduct(storeShop, productId, productConf, userId, clientId)
    elif product.pt == "coin" or (not product.pt and actionType == StoreTabType.STT_COIN):
        productObj = CoinProduct(storeShop, productId, productConf, userId, clientId)
    elif product.pt == "coupon" or (not product.pt and actionType == StoreTabType.STT_COUPON):
        productObj = CouponProduct(storeShop, productId, productConf, userId, clientId)
    elif product.pt in ["item", "chest"] or (not product.pt and actionType in [StoreTabType.STT_ITEM, StoreTabType.STT_CHEST]):
        # 招财商品
        if isBulletStore(productId):
            productObj = BulletProduct(storeShop, productId, productConf, userId, clientId)
        else:
            productObj = ItemProduct(storeShop, productId, productConf, userId, clientId)
    elif actionType == StoreTabType.STT_CONVERT:
        productObj = ExchangeProduct(storeShop, productId, productConf, userId, clientId)
    return productObj


class BaseStoreShop(object):
    """
    商城基类
    """
    def __init__(self, userId, clientId, actionType):
        self.userId = userId
        self.clientId = clientId
        self.isAppClient = util.isAppClient(userId)             # 判断是否为单包客户端
        self.isVerLimited = util.isVersionLimit(userId) or util.isPurchaseLimit(userId)     # 判断客户端版本是否属于提审版本(2.0.56) True|False
        self.lang = util.getLanguage(userId, clientId)
        self.vipLevel = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
        self.platformOS = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.platformOS)    # platformOS 微信小游戏的客户端系统 android|ios
        self.clientVersion = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.clientVersion)  # clientVersion 客户端当前版本号(2.0.56)
        self.level = util.getUserLevel(userId)  # 玩家等级 获取玩家商城需要检测的等级
        self.gunLevel = util.getGunLevelVal(userId, config.MULTIPLE_MODE)  # 玩家最大炮倍数 获取玩家商城需要检测的等级
        self.actionType = actionType                            # 0、1、2、---10
        self.curTime = int(time.time())
        self._setConf()

    def _setConf(self):
        """
        设置商城配置文件
        """
        confName = storeTabConfName.get(self.actionType)                                    # 获取各种商品类名
        self.storeConf = config.getStoreConf(self.clientId).get(confName, {})               # 商品项


class CoinStoreShop(BaseStoreShop):
    """
    金币商城
    """
    def __init__(self, userId, clientId, actionType):
        super(CoinStoreShop, self).__init__(userId, clientId, actionType)

    def getStore(self):
        """
        金币商店
        """
        coinItems = []
        coinStoreConf = self.storeConf.get("items", {})
        coinStoreTab = {"name": config.getMultiLangTextConf("ID_BUY_COIN", lang=self.lang), "subStore": "coin"}
        if not self.isVerLimited or self.platformOS == "android":
            for productId, product in coinStoreConf.iteritems():
                if isInvalidePruduct(self.isVerLimited, product, self.level, self.gunLevel, self.clientVersion):
                    continue
                if self.isAppClient and product.get("limitCond", {}).get("appVisible", 1) == 0:  # app客户端隐藏商品
                    continue
                productObj = CreateProduct(self, self.actionType, productId, product, self.userId, self.clientId)
                if productObj:
                    data = productObj.parse()
                    coinItems.append(data)
        coinStoreTab["items"] = coinItems
        return coinStoreTab


class DiamondStoreShop(BaseStoreShop):
    """
    钻石商城
    """
    def __init__(self, userId, clientId, actionType):
        super(DiamondStoreShop, self).__init__(userId, clientId, actionType)

    def getStore(self):
        """
        钻石商店
        """
        diamondStoreConf = self.storeConf.get("items", {})
        if ftlog.is_debug():
            ftlog.debug("getDiamondStore", diamondStoreConf)
        diamondItems = []
        diamondStoreTab = {"name": config.getMultiLangTextConf("ID_BUY_DIAMOND", lang=self.lang), "subStore": "diamond"}
        if not self.isVerLimited or self.platformOS == "android":
            for productId, product in diamondStoreConf.iteritems():
                if isInvalidePruduct(self.isVerLimited, product, self.level, self.gunLevel, self.clientVersion):
                    continue
                if self.isAppClient and product.get("limitCond", {}).get("appVisible", 1) == 0:  # app客户端隐藏商品
                    continue
                productObj = CreateProduct(self, self.actionType, productId, product, self.userId, self.clientId)
                if productObj:
                    data = productObj.parse()
                    diamondItems.append(data)
        diamondStoreTab["items"] = diamondItems
        return diamondStoreTab


class ItemStoreShop(BaseStoreShop):
    """
    道具商城
    """
    def __init__(self, userId, clientId, actionType):
        super(ItemStoreShop, self).__init__(userId, clientId, actionType)
        self.chestStoreTab = {"name": config.getMultiLangTextConf("ID_BUY_ITEM", lang=self.lang), "subStore": "item"}

    def getStore(self):
        """
        道具商店
        """
        chestItems = []
        chestItemsConf = self.storeConf.get("items", {})
        chestAds = self.storeConf.get("shop", {}).get("ads", [])
        ownGunSkinSkins = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.ownGunSkinSkins, [])
        for chestId, product in chestItemsConf.iteritems():
            if isInvalidePruduct(self.isVerLimited, product, self.level, self.gunLevel, self.clientVersion, ownGunSkinSkins):
                continue
            if not util.isOldPlayerV2(self.userId) and product.get("itemId", 0) == config.SKILLCD_KINDID:   # 老玩家可见冷却道具
                continue
            productObj = CreateProduct(self, self.actionType, chestId, product, self.userId, self.clientId)
            if productObj:
                data = productObj.parse()
                if product.get("itemId", 0) == config.GOLDEN_KEY_KINDID:
                    _key = UserData.buyProductCount % (FISH_GAMEID, self.userId)
                    _subKey = util.getDayStartTimestamp(int(time.time())) + 86400
                    dayBuyCount = json.loads(daobase.executeUserCmd(self.userId, "HGET", _key, str(_subKey)) or "{}")
                    dayPurchaseNum = dayBuyCount.get(chestId, 0)
                    vipDailyCountLimit = product.get("limitCond", {}).get("vipDailyCountLimit", [])
                    userVip = hallvip.userVipSystem.getUserVip(self.userId).vipLevel.level
                    vipLimit = product.get("limitCond", {}).get("vipLimit", 0)
                    buyCountLimit = vipDailyCountLimit[userVip]
                    data.update({"dayPurchaseNum": dayPurchaseNum})
                    data.update({"buyCountLimit": buyCountLimit})
                    data.update({"minVipLimit": [vipLimit, vipDailyCountLimit[vipLimit]]})
                if product.get("itemId", 0) == 36201:
                    freeChestCount = weakdata.getDayFishData(self.userId, "buyDailyChestCount", 0)
                    freeData = product.get("extendData", {}).get("free")
                    dayLeftFreeCount = len(freeData.get("time")) - freeChestCount
                    data.update({"dayLeftFreeCount": dayLeftFreeCount})
                chestItems.append(data)
        self.chestStoreTab["items"] = chestItems
        if self.actionType == StoreTabType.STT_CHEST:
            self.chestStoreTab["ads"] = chestAds
        return self.chestStoreTab


class ChestStoreShop(ItemStoreShop):
    """
    宝箱商城
    """
    def __init__(self, userId, clientId, actionType):
        super(ChestStoreShop, self).__init__(userId, clientId, actionType)
        self.chestStoreTab = {"name": config.getMultiLangTextConf("ID_BUY_CHEST", lang=self.lang), "subStore": "chest"}


class HotStoreShop(BaseStoreShop):
    """
    热卖商城, 此中商品必须要配置pt参数指定商品的类型!
    """
    def __init__(self, userId, clientId, actionType):
        super(HotStoreShop, self).__init__(userId, clientId, actionType)

    def getStore(self):
        """
        热卖商店
        """
        storeConf = self.storeConf.get("items", {})
        tip = ""
        tipConf = self.storeConf.get("shop", {}).get("tip", [])
        for _tip in tipConf:
            _effTime = _tip.get("effectiveTime")
            if _effTime and util.getTimestampFromStr(_effTime["start"]) <= self.curTime <= util.getTimestampFromStr(_effTime["end"]):
                tip = config.getMultiLangTextConf(_tip.get("txt", ""), lang=self.lang)
        hotItems = []
        hotStoreTab = {"name": config.getMultiLangTextConf("ID_BUY_DIAMOND", lang=self.lang), "subStore": "hot"}
        ownGunSkinSkins = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.ownGunSkinSkins, [])
        if not self.isVerLimited or self.platformOS == "android":
            for productId, product in storeConf.iteritems():
                if isInvalidePruduct(self.isVerLimited, product, self.level, self.gunLevel, self.clientVersion, ownGunSkinSkins):
                    continue
                if self.isAppClient and product.get("limitCond", {}).get("appVisible", 1) == 0:  # app客户端隐藏商品
                    continue
                productObj = CreateProduct(self, self.actionType, productId, product, self.userId, self.clientId)
                if productObj:
                    data = productObj.parse()
                    serverBuyCount = product.get("limitCond", {}).get("hotServerDailyCountLimit", -1)
                    if serverBuyCount != -1:
                        key = MixData.buyHotProductServerCount % FISH_GAMEID
                        serverPurchaseNum = daobase.executeMixCmd("HGET", key, productId) or 0
                        leftNum = serverBuyCount - serverPurchaseNum
                        data.update({"leftNum": leftNum})
                    hotItems.append(data)
        hotStoreTab["items"] = hotItems
        hotStoreTab["tip"] = tip
        return hotStoreTab


class CouponStoreShop(BaseStoreShop):
    """
    兑换券商城
    """
    def __init__(self, userId, clientId, actionType):
        super(CouponStoreShop, self).__init__(userId, clientId, actionType)

    def getStore(self):
        """
        兑换券商店
        """
        couponItems = []
        couponStoreConf = self.storeConf.get("items", {})
        couponNum = userchip.getCoupon(self.userId)
        for productId, product in couponStoreConf.iteritems():
            if self.isVerLimited and product.get("limitCond", {}).get("reviewVerLimit", 0) == 1:  # 限制的版本不向客户端发送
                continue
            # 新手限定商品（10元话费卡）
            if product.get("visible") == 0:
                exchangeCount = gamedata.getGameAttrInt(self.userId, FISH_GAMEID, GameData.exchangeCount)
                if exchangeCount:
                    continue
            if couponNum < product.get("limitCond", {}).get("displayLimitNum", 0):
                continue
            if config.isClientIgnoredConf("storeIds", productId, self.clientId):
                continue
            if self.level < product.get("limitCond", {}).get("levelLimit", 0):
                continue
            lowVersion = product.get("limitCond", {}).get("lowVersion")
            if lowVersion and self.clientVersion and StrictVersion(str(lowVersion)) > StrictVersion(str(self.clientVersion)):
                continue
            # 处理库存状态.
            stockState = 0
            serverBuyNumLimit = product.get("limitCond", {}).get("serverDailyCountLimit", -1)
            if serverBuyNumLimit == 0:
                stockState = 2
            elif serverBuyNumLimit > 0:
                key = MixData.buyProductServerCount % FISH_GAMEID
                serverPurchaseNum = daobase.executeMixCmd("HGET", key, productId) or 0
                if serverBuyNumLimit <= serverPurchaseNum:
                    stockState = 2
                else:
                    stockPct = int(100. * (serverBuyNumLimit - serverPurchaseNum) / serverBuyNumLimit)
                    if stockPct < 50:
                        stockState = 1
            productObj = CreateProduct(self, self.actionType, productId, product, self.userId, self.clientId)
            if productObj:
                data = productObj.parse()
                data.update(
                    {
                        "tipTxt": config.getMultiLangTextConf(exchangeTipData[stockState].get("txt", "ID_EXCHANGE_UNDER_STOCK"), lang=self.lang),
                        "tipColor": exchangeTipData[stockState].get("color", "d3cee8"),
                        "tipState": exchangeTipData[stockState].get("state", 0),
                        "vip": product.get("limitCond", {}).get("vipLimit", 0)
                    }
                )
                couponItems.append(data)
        couponStoreTab = {"name": config.getMultiLangTextConf("ID_EXCHANGE_COUPON", lang=self.lang), "subStore": "coupon"}
        couponStoreTab["items"] = couponItems
        refreshTime = config.getPublic("couponStoreRefreshTime")
        couponStoreTab["tip"] = config.getMultiLangTextConf("ID_EXCHANGE_TIP_TXT", lang=self.lang).format(refreshTime)
        couponStoreRefreshTime = config.getPublic("couponStoreRefreshTime", "00:00")
        refreshTS = util.getDayStartTimestamp(self.curTime) + util.timeStrToInt(couponStoreRefreshTime)
        couponStoreTab["refreshLeftTime"] = (refreshTS - self.curTime) if refreshTS >= self.curTime  else (refreshTS - self.curTime + 86400)
        return couponStoreTab


class ExchangeStoreShop(BaseStoreShop):
    """
    兑换商城
    """
    def __init__(self, userId, clientId, actionType):
        super(ExchangeStoreShop, self).__init__(userId, clientId, actionType)

    def _getSubKey(self):
        """
        获取兑换商城按时间存档的key,使用此次购买阶段的开始时间戳
        """
        startTS = util.getTimestampFromStr(self.storeConf.get("startTS"))
        loopDays = self.storeConf.get("loopDays", 1)
        if loopDays <= 0:
            ftlog.error("ExchangeStoreShop config error! loopDays =", loopDays)
            loopDays = 1
        subKey = startTS
        while subKey + loopDays * 86400 <= self.curTime:
            subKey += loopDays * 86400
        return subKey

    def removeExpiredData(self, subKey):
        """
        去除过期的存档数据
        """
        _key = UserData.buyExchangeProduct % (FISH_GAMEID, self.userId)
        datas = daobase.executeUserCmd(self.userId, "HGETALL", _key)
        delKeys = []
        for key in datas[0::2]:
            if int(key) < subKey:
                delKeys.append(key)
        for key in delKeys:
            daobase.executeUserCmd(self.userId, "HDEL", _key, key)

    def _setConf(self):
        """
        设置商城配置文件
        """
        self.storeConf = config.getExchangeStoreConf()

    def getStore(self):
        """
        兑换商店
        """
        items = []
        # 商品配置中的商品等级必须由低到高配置!
        storeConf = self.storeConf.get("items", {})
        exchangeStoreTab = {"name": config.getMultiLangTextConf("ID_BUY_COIN", lang=self.lang), "subStore": "convert"}
        _subKey = self._getSubKey()
        self.removeExpiredData(_subKey)
        _key = UserData.buyExchangeProduct % (FISH_GAMEID, self.userId)
        buyExchangeProduct = json.loads(daobase.executeUserCmd(self.userId, "HGET", _key, str(_subKey)) or "{}")
        highestUnlockedId = buyExchangeProduct.setdefault("highestUnlockedId", 0)
        buyCount = buyExchangeProduct.get("buyCount", {})
        for productId, product in storeConf.iteritems():
            productId = str(productId)
            productObj = CreateProduct(self, self.actionType, productId, product, self.userId, self.clientId)
            if productObj:
                data = productObj.parse()
                buyCountLimit = product.get("limitCond").get("userCountLimit")
                categoryId = product.get("categoryId")
                alreadyBuyCount = buyCount.get(productId, 0)
                data.update({"buyCountLimit": buyCountLimit})
                data.update({"alreadyBuyCount": alreadyBuyCount})
                data.update({"categoryId": categoryId})
                items.append(data)
        exchangeStoreTab["items"] = items
        exchangeStoreTab["nextRefreshLeftTime"] = max(0, (_subKey + self.storeConf.get("loopDays", 1) * 86400 - self.curTime))
        exchangeStoreTab["highestUnlockedId"] = highestUnlockedId
        return exchangeStoreTab


class BaseProduct(object):
    """
    商品基类
    """
    def __init__(self, storeShop, productId, product, userId, clientId=None):
        self.curTime = int(time.time())
        self.userId = userId
        self.productId = productId
        self.product = product
        self.idx = 0
        if storeShop:
            self.vipLevel = storeShop.vipLevel
            self.lang = storeShop.lang
            self.level = storeShop.level
            self.gunLevel = storeShop.gunLevel
        else:
            self.lang = util.getLanguage(userId, clientId)
            self.vipLevel = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
            self.level = util.getStoreCheckLevel(userId)
            self.gunLevel = util.getGunLevelVal(userId, config.MULTIPLE_MODE)
        self.idx = self._getIdx()

    def _getIdx(self):
        """
        获取对应索引
        """
        raise NotImplementedError

    def getPrice(self, buyType=None):
        """
        获取商品价格
        """
        if self.product.get("otherBuyType", {}).get(buyType):
            price = self.product.get("otherBuyType").get(buyType)
        else:
            price = self.product["cur_price"][self.idx] if self.product["cur_price"] and self.idx < len(self.product.get("cur_price")) else self.product["cur_price"][-1]
        return price

    def getItemCount(self):
        """
        获取商品中道具数量
        """
        if self.idx >= len(self.product.get("count")):
            return self.product.get("count")[-1]
        return self.product.get("count")[self.idx]

    def getName(self):
        """
        获取商品名字
        """
        if self.product["name"] and self.idx < len(self.product["name"]) and self.product["name"][self.idx]:
            return config.getMultiLangTextConf(self.product["name"][self.idx], lang=self.lang)
        else:
            return config.getMultiLangTextConf(self.product["name"][-1])

    def getLabel1(self):
        if self.product["label1"]:
            if self.product["label1"][0] == "ID_CONFIG_COIN_STORE_ACTIVITY_1":
                key = MixData.buyHotProductServerCount % FISH_GAMEID
                serverPurchaseNum = daobase.executeMixCmd("HGET", key, self.productId) or 0
                serverBuyCount = self.product.get("limitCond", {}).get("hotServerDailyCountLimit", -1)
                return config.getMultiLangTextConf(self.product["label1"][self.idx], lang=self.lang).format(
                    serverBuyCount - serverPurchaseNum, serverBuyCount)
            if self.idx < len(self.product["label1"]) and self.product["label1"][self.idx]:
                return config.getMultiLangTextConf(self.product["label1"][self.idx], lang=self.lang)
            else:
                return config.getMultiLangTextConf(self.product["label1"][-1], lang=self.lang) if self.product["label1"][-1] else ""
        else:
            return ""

    def getLabel2(self):
        if self.product["label2"]:
            if self.idx < len(self.product["label2"]) and self.product["label2"][self.idx]:
                return config.getMultiLangTextConf(self.product["label2"][self.idx], lang=self.lang)
            else:
                return config.getMultiLangTextConf(self.product["label2"][-1], lang=self.lang) if self.product["label2"][-1] else ""
        else:
            return ""

    def getLabel3(self):
        if self.product["label3"]:
            if self.idx < len(self.product["label3"]) and self.product["label3"][self.idx]:
                return config.getMultiLangTextConf(self.product["label3"][self.idx], lang=self.lang)
            else:
                return config.getMultiLangTextConf(self.product["label3"][-1], lang=self.lang) if self.product["label3"][-1] else ""
        else:
            return ""

    def getLabel1BgType(self):
        if "label1BgType" not in self.product:
            return ""
        if self.product["label1BgType"] and self.idx < len(self.product["label1BgType"]) and self.product["label1BgType"][self.idx]:
            return self.product["label1BgType"][self.idx]
        else:
            return self.product["label1BgType"][-1]

    def getLabel2BgType(self):
        if "label2BgType" not in self.product:
            return ""
        if self.product["label2BgType"] and self.idx < len(self.product["label2BgType"]) and self.product["label2BgType"][self.idx]:
            return self.product["label2BgType"][self.idx]
        else:
            return self.product["label2BgType"][-1]

    def getLabel3BgType(self):
        if "label3BgType" not in self.product:
            return ""
        if self.product["label3BgType"] and self.idx < len(self.product["label3BgType"]) and self.product["label3BgType"][self.idx]:
            return self.product["label3BgType"][self.idx]
        else:
            return self.product["label3BgType"][-1]

    def parse(self):
        """
        商品配置解析
        """
        item_id = self.product.get("itemId", 0)
        data = {
            "id": self.productId,
            "name": self.getName(),
            "price": self.product["price"],
            "cur_price": self.getPrice(),
            "price_direct": self.product.get("price_direct", 0),
            "price_diamond": self.product.get("price_diamond", 0),
            "pic": self.product["pic"],
            "item_id": item_id,
            "count": self.getItemCount(),
            "tag": 0,
            "desc": self.getLabel2(),
            "addition": self.getLabel1(),
            "label": "",
            "label1": self.getLabel1(),
            "label2": self.getLabel2(),
            "label3": self.getLabel3(),
            "label1BgType": self.getLabel1BgType(),
            "label2BgType": self.getLabel2BgType(),
            "label3BgType": self.getLabel3BgType(),
            "buy_type": self.product["buyType"],
            "other_buy_type": self.product.get("otherBuyType", {}),
            "otherProductInfo": getOtherBuyProduct(self.product.get("otherBuyType", {}), self.product["buyType"]),
            "skinType": self.product.get("extendData", {}).get("itemType", 0),
            "info": chest_system.getChestInfo(item_id) if str(item_id).isdigit() and util.isChestRewardId(item_id) else {},
            "convenientBuy": self.product.get("extendData", {}).get("convenientBuy", 0),
            "productType": self.product.get("pt", "")
        }
        return data


class CoinProduct(BaseProduct):
    """
    金币商品
    """
    def __init__(self, storeShop, productId, product, userId, clientId=None):
        super(CoinProduct, self).__init__(storeShop, productId, product, userId, clientId)

    def _getIdx(self):
        buyCoinCountDict = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.buyCoinCount, {})    # 金币商城购买各商品次数
        buyCoinCount = buyCoinCountDict.get(self.productId, 0)
        if buyCoinCount > 0:
            index = 1                       # if self.vipLevel >= self.product.get("additionVip", 0) else 1
        else:
            index = 0
        if index >= len(self.product["name"]) or index >= len(self.product["count"]):
            index = 0
        return index


class DiamondProduct(BaseProduct):
    """
    钻石商品
    """
    def __init__(self, storeShop, productId, product, userId, clientId=None):
        super(DiamondProduct, self).__init__(storeShop, productId, product, userId, clientId)

    def _getIdx(self):
        """
        获取对应索引
        """
        return 0


class BulletProduct(BaseProduct):
    """
    招财珠商品
    """
    def __init__(self, storeShop, productId, product, userId, clientId=None):
        super(BulletProduct, self).__init__(storeShop, productId, product, userId, clientId)
        self.todayBuyInfo = weakdata.getDayFishData(self.userId, WeakData.shopBuyInfo, {})
        self.code, self.leftNum = canBuyResult(self.userId, "bulletStore", self.productId, self.product, self.vipLevel, self.todayBuyInfo)

    def getLabel1(self):
        labelIndex = -1
        label1 = ""
        if self.product["label1"] and self.product["label1"][labelIndex] and self.product["label1"][labelIndex]:
            label1 = config.getMultiLangTextConf(self.product["label1"][labelIndex], lang=self.lang)
        if self.product.get("limitCond", {}).get("userDailyCountLimit", 0) > 0:
            label1 = config.getMultiLangTextConf("ID_LEFT_NUM", lang=self.lang) % self.leftNum
        return label1

    def parse(self):
        """
        商品配置解析
        """
        if self.code != 0:
            return None
        return super(BulletProduct, self).parse()


class ItemProduct(BaseProduct):
    """
    道具商品
    """
    def __init__(self, storeShop, productId, product, userId, clientId=None):
        super(ItemProduct, self).__init__(storeShop, productId, product, userId, clientId)
        # self.buyChestCountList = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.buyChestCount, [0, 0, 0, 0, 0, 0, 0])
        self.buyChestCountList = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.buyChestCount1, {})
        itemId = self.product.get("itemId", 0)
        self.buyChestCount = 0
        if str(itemId).isdigit() and util.isChestRewardId(itemId):
            if self.product["order"] == 0:
                self.buyChestCount = weakdata.getDayFishData(self.userId, "buyDailyChestCount", 0)
            elif self.buyChestCountList and str(productId) in self.buyChestCountList:
                self.buyChestCount = self.buyChestCountList[str(productId)]
            else:
                self.buyChestCount = 0
        self.isFree = self._checkFreePrice()

    def _checkFreePrice(self):
        """
        检测商品是否免费
        """
        freeData = self.product.get("extendData", {}).get("free")
        if freeData:
            if freeData.get("type") == "interval":
                productFreeTS = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.productFreeTS, {})
            elif freeData.get("type") == "day":
                productFreeTS = weakdata.getDayFishData(self.userId, WeakData.productFreeTS, {})
            else:
                productFreeTS = {}
            ts = productFreeTS.get(str(self.productId), 0)
            if ftlog.is_debug():
                ftlog.debug("_checkFreePrice, ", self.userId, freeData, productFreeTS, ts)
            return True if self.curTime >= ts else False
        return False

    def _getIdx(self):
        """
        获取对应索引
        """
        if self.product.get("itemId", 0) == config.GRAND_PRIX_FEES_KINDID:
            _key = UserData.buyProductCount % (FISH_GAMEID, self.userId)
            _subKey = util.getDayStartTimestamp(int(time.time())) + 86400
            dayBuyCount = json.loads(daobase.executeUserCmd(self.userId, "HGET", _key, str(_subKey)) or "{}")
            dayPurchaseNum = dayBuyCount.get(self.productId, 0)
            if ftlog.is_debug():
                ftlog.debug("_dayPurchaseNum, ", self.userId, dayPurchaseNum, _subKey)
            return dayPurchaseNum
        return 0

    def getPrice(self, buyType=None):
        """
        获取商品价格
        """
        if self.isFree:
            return 0
        if self.product.get("itemId", 0) == config.GRAND_PRIX_FEES_KINDID:
            price = self.product["cur_price"][self.idx] if self.product["cur_price"] and self.idx < len(self.product.get("cur_price")) else self.product["price"]
            return price
        idx = self.buyChestCount if self.buyChestCount < len(self.product["cur_price"]) else -1
        price = self.product["cur_price"][idx]
        return price

    def getName(self):
        """
        获取商品名字
        """
        name = super(ItemProduct, self).getName()
        # 珍珠商品的名字特殊处理.
        # if self.product.get("itemId", 0) == config.PEARL_KINDID:
        #     return "%sx%d" % (name, self.getItemCount())
        return name

    def getLabel1(self):
        idx = self.buyChestCount if self.buyChestCount < len(self.product["label1"]) else -1
        label1 = ""
        if self.product["label1"] and self.product["label1"][idx]:
            label1 = config.getMultiLangTextConf(self.product["label1"][idx], lang=self.lang)
        return label1

    def getLabel2(self):
        label2 = ""
        freeData = self.product.get("extendData", {}).get("free")
        if freeData:
            if self.isFree:
                if freeData.get("type") == "day":
                    # label2 = "%d / %d" % (len(freeData.get("time")) - self.buyChestCount, len(freeData.get("time")))
                    label2 = config.getMultiLangTextConf(self.product["label2"][2], lang=self.lang).format(len(freeData.get("time")) - self.buyChestCount, len(freeData.get("time")))
                elif freeData.get("type") == "interval":
                    label2 = ""
            else:
                import math
                productFreeTS = {}
                if freeData.get("type") == "day":
                    productFreeTS = weakdata.getDayFishData(self.userId, WeakData.productFreeTS, {})
                elif freeData.get("type") == "interval":
                    productFreeTS = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.productFreeTS, {})
                ts = productFreeTS.get(str(self.productId), 0)
                if ts > self.curTime:
                    minute = int(math.ceil((ts - self.curTime) / 60))
                    m = minute % 60
                    h = minute / 60
                    if h > 0:
                        h += (1 if m > 0 else 0)
                        # label2 = "remain %d hours" % h
                        label2 = config.getMultiLangTextConf(self.product["label2"][0], lang=self.lang) % h
                    else:
                        # label2 = "remain %d miniutes" % m
                        if len(self.product["label2"]) > 1:
                            label2 = config.getMultiLangTextConf(self.product["label2"][1], lang=self.lang) % m
        elif self.product.get("itemId", 0) == config.GRAND_PRIX_FEES_KINDID:
            label2 = config.getMultiLangTextConf(self.product["label2"][self.idx], lang=self.lang)
        else:
            idx = self.buyChestCount if self.buyChestCount < len(self.product["label2"]) else -1
            if self.product["label2"] and self.product["label2"][idx]:
                label2 = config.getMultiLangTextConf(self.product["label2"][idx], lang=self.lang)
        return label2

    def parse(self):
        data = super(ItemProduct, self).parse()
        data["price_diamond"] = self.getPrice()
        return data


class CouponProduct(BaseProduct):
    """
    兑换券商品
    """
    def __init__(self, storeShop, productId, product, userId, clientId=None):
        super(CouponProduct, self).__init__(storeShop, productId, product, userId, clientId)

    def _getIdx(self):
        idx = -1
        if self.product.get("extendData", {}).get("activityPrice"):
            startTime = util.getTimestampFromStr(self.product["extendData"]["activityPrice"]["effectiveTime"]["start"])
            endTime = util.getTimestampFromStr(self.product["extendData"]["activityPrice"]["effectiveTime"]["end"])
            if startTime < self.curTime < endTime:
                idx = 0
        return idx

    def getPrice(self, buyType=None):
        price = super(CouponProduct, self).getPrice(buyType)
        if self.product.get("extendData", {}).get("activityPrice"):
            startTime = util.getTimestampFromStr(self.product["extendData"]["activityPrice"]["effectiveTime"]["start"])
            endTime = util.getTimestampFromStr(self.product["extendData"]["activityPrice"]["effectiveTime"]["end"])
            if startTime < self.curTime < endTime:
                price = self.product["extendData"]["activityPrice"]["cur_price"]
        return price


class ExchangeProduct(BaseProduct):
    """
    兑换商品
    """
    def __init__(self, storeShop, productId, product, userId, clientId=None):
        super(ExchangeProduct, self).__init__(storeShop, productId, product, userId, clientId)

    def _getIdx(self):
        """
        获取对应索引
        """
        from newfish.entity.item import ExchangeStoreBuyAction
        _subKey = ExchangeStoreBuyAction._getSubKey()
        _key = UserData.buyExchangeProduct % (FISH_GAMEID, self.userId)
        buyExchangeProduct = json.loads(daobase.executeUserCmd(self.userId, "HGET", _key, str(_subKey)) or "{}")
        buyCount = buyExchangeProduct.get("buyCount", {})
        alreadyBuyCount = buyCount.get(str(self.productId), 0)
        return alreadyBuyCount



def getPearlStore(userId, clientId):
    """
    珍珠商店
    """
    clientVersion = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.clientVersion)
    isVerLimited = util.isVersionLimit(userId) or util.isPurchaseLimit(userId)
    lang = util.getLanguage(userId, clientId)
    pearlItems = []
    pearlStoreConf = config.getStoreConf(clientId).get("pearlStore", {})
    pearlStoreTab = {"name": config.getMultiLangTextConf("ID_BUY_PEARL", lang=lang), "subStore": "pearl", "iconType": "pearl"}
    vipLevel = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
    buyPearlCountDict = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.buyPearlCount, {})
    level = util.getStoreCheckLevel(userId)
    gunLevel = util.getGunLevelVal(userId, config.MULTIPLE_MODE)
    platformOS = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.platformOS)
    if not isVerLimited or platformOS == "android":
        for productId, product in pearlStoreConf.iteritems():
            if isInvalidePruduct(isVerLimited, product, level, gunLevel, clientVersion):
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
                "name": config.getMultiLangTextConf(product["name"][index], lang=lang),
                "price": product["price"],
                "desc": "",
                "pic": product["pic"],
                "tag": product["tag"],
                "buy_type": product["buyType"],
                "price_direct": product.get("price_direct", 0),
                "price_diamond": product.get("price_diamond", 0),
                "addition": config.getMultiLangTextConf(product["addition"][index], lang=lang),
                "item_id": product["itemId"],
                "count": product["count"][index],
                "other_buy_type": product.get("otherBuyType", {}),
                "otherProductInfo": getOtherBuyProduct(product.get("otherBuyType", {}), product["buyType"])
            }
            pearlItems.append(data)
    pearlStoreTab["items"] = pearlItems
    return pearlStoreTab


def getGunSkinStore(userId, clientId):
    """
    火炮皮肤商店
    """
    clientVersion = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.clientVersion)
    level = util.getStoreCheckLevel(userId)
    gunLevel = util.getGunLevelVal(userId, config.MULTIPLE_MODE)
    isVerLimited = util.isVersionLimit(userId) or util.isPurchaseLimit(userId)
    lang = util.getLanguage(userId, clientId)
    gunSKinItems = []
    gunSkinStoreConf = config.getStoreConf(clientId).get("gunSkinStore", {})
    gunSkinStoreTab = {"name": config.getMultiLangTextConf("ID_BUY_GUN_SKIN", lang=lang), "subStore": "gunSkin", "iconType": "gunSkin"}
    for productId, product in gunSkinStoreConf.iteritems():
        if isInvalidePruduct(isVerLimited, product, level, gunLevel, clientVersion):
            continue
        discountPriceIndex = -1
        additionIndex = -1
        discountPrice = product["discountPrice"][discountPriceIndex]
        addition = ""
        if product["addition"][additionIndex]:
            addition = config.getMultiLangTextConf(product["addition"][additionIndex], lang=lang)
        desc = ""
        if product["desc"]:
            desc = config.getMultiLangTextConf(product["desc"], lang=lang)
        data = {
            "id": productId,
            "name": config.getMultiLangTextConf(product["name"], lang=lang),
            "price": product["price"],
            "discountPrice": discountPrice,
            "desc": desc,
            "pic": product["pic"],
            "tag": product["tag"],
            "item_id": product["itemId"],
            "count": product["count"],
            "buy_type": product["buyType"],
            "addition": addition
        }
        gunSKinItems.append(data)
    gunSkinStoreTab["items"] = gunSKinItems
    return gunSkinStoreTab


def getBulletStore(userId, clientId):
    """
    招财珠商店
    """
    clientVersion = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.clientVersion)
    level = util.getStoreCheckLevel(userId)
    gunLevel = util.getGunLevelVal(userId, config.MULTIPLE_MODE)
    isVerLimited = util.isVersionLimit(userId) or util.isPurchaseLimit(userId)
    lang = util.getLanguage(userId, clientId)
    bulletStoreConf = config.getStoreConf(clientId).get("bulletStore", {})
    version = util.getClientIdVer(userId)
    versionName = "hall37" if version < 5 else "hall51"
    bulletStoreConf = bulletStoreConf.get(versionName, {})
    bulletItems = []
    bulletStoreTab = {"name": config.getMultiLangTextConf("ID_BUY_ROBBERY_BULLET", lang=lang), "subStore": "bullet", "iconType": "bullet"}
    userVip = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
    todayBuyInfo = weakdata.getDayFishData(userId, WeakData.shopBuyInfo, {})
    for productId, product in bulletStoreConf.iteritems():
        if isInvalidePruduct(isVerLimited, product, level, gunLevel, clientVersion):
            continue
        code, leftNum = canBuyResult(userId, "bulletStore", productId, product, userVip, todayBuyInfo)
        if code != 0:
            continue
        additionIndex = -1
        price = product["price"]
        addition = ""
        if product["addition"][additionIndex]:
            addition = config.getMultiLangTextConf(product["addition"][additionIndex], lang=lang)
            if product.get("limitCond", {}).get("userDailyCountLimit", 0) > 0:
                addition = config.getMultiLangTextConf("ID_LEFT_NUM", lang=lang) % leftNum
        data = {
            "id": productId,
            "name": config.getMultiLangTextConf(product["name"], lang=lang),
            "price": price,
            "desc": "",
            "pic": product["pic"],
            "tag": product["tag"],
            "buy_type": product["buyType"],
            "price_direct": product.get("price_direct", 0),
            "price_diamond": product.get("price_diamond", 0),
            "addition": addition,
            "other_buy_type": product.get("otherBuyType", {}),
            "item_id": product["itemId"],
            "count": product["count"],
            "otherProductInfo": getOtherBuyProduct(product.get("otherBuyType", {}), product["buyType"])
        }
        bulletItems.append(data)
    bulletStoreTab["items"] = bulletItems
    return bulletStoreTab


def getTimeLimitedStoreRefreshInfo(userId):
    """
    获取限时商城刷新相关数据
    """
    # timeLimitedStoreConf = config.getTimeLimitedStoreConf()
    key = GameData.timeLimitedStore % (FISH_GAMEID, userId)
    tls_nextRefreshTS = daobase.executeUserCmd(userId, "HGET", key, GameData.tls_nextRefreshTS) or 0
    # nextRefreshLeftTime = max(tls_nextRefreshTS - int(time.time()), 0)

    tls_refreshedTimes = json.loads(daobase.executeUserCmd(userId, "HGET", key, GameData.tls_refreshedTimes) or "{}")
    refreshedTimes = tls_refreshedTimes.get(str(util.getDayStartTimestamp(int(time.time()))), 0)

    # priceList = timeLimitedStoreConf.get("refresh", {}).get("price", [])
    vipLevel = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
    maxRefreshTimes = config.getVipConf(vipLevel).get("timeLimitedStoreRefreshTimes", 0)
    # refreshPrice = priceList[-1]
    # if refreshedTimes < len(priceList):
    #     refreshPrice = priceList[refreshedTimes]
    if ftlog.is_debug():
        ftlog.debug("getTimeLimitedStoreRefreshInfo, userId =", userId, vipLevel, maxRefreshTimes, refreshedTimes)
    return refreshedTimes, maxRefreshTimes


def getTimeLimitedStoreTab(userId, clientId, isRefresh):
    """
    获取玩家限时商城数据
    """
    code = 0
    timeLimitedStoreConf = config.getTimeLimitedStoreConf()
    buyTimeLimitedCountDict = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.buyTimeLimitedCount, {})

    needRefresh = False
    key = GameData.timeLimitedStore % (FISH_GAMEID, userId)
    dayStartTS = util.getDayStartTimestamp(int(time.time()))
    storeInfo = json.loads(daobase.executeUserCmd(userId, "HGET", key, GameData.tls_info) or "{}")
    tls_refreshedTimes = json.loads(daobase.executeUserCmd(userId, "HGET", key, GameData.tls_refreshedTimes) or "{}")
    vipLevel = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
    maxRefreshTimes = config.getVipConf(vipLevel).get("timeLimitedStoreRefreshTimes", 0)
    # 手动刷新.
    if isRefresh:
        refreshedTimes = tls_refreshedTimes.get(str(dayStartTS), 0)
        # priceList = timeLimitedStoreConf.get("refresh", {}).get("price", [])
        if maxRefreshTimes > refreshedTimes >= 0:
            # refreshPrice = priceList[refreshedTimes]
            # if util.balanceItem(userId, config.RUBY_KINDID) >= refreshPrice > 0:
            #     _consume = [{"name": config.RUBY_KINDID, "count": abs(refreshPrice)}]
            #     _ret = util.consumeItems(userId, _consume, "BI_NFISH_BUY_ITEM_CONSUME", refreshedTimes)
            #     if _ret:
            #         needRefresh = True
            #         code = 0
            #     else:
            #         code = 1
            # else:
            #     code = 2
            needRefresh = True
            code = 0
        else:
            code = 1
    # else:# 检查自动刷新点
    #     tls_nextRefreshTS = daobase.executeUserCmd(userId, "HGET", key, GameData.tls_nextRefreshTS) or 0
    #     needRefresh = tls_nextRefreshTS <= int(time.time())
    if not storeInfo:
        needRefresh = True
        code = 0
    if needRefresh and code == 0:
        storeInfo = {}
        typeStores = timeLimitedStoreConf.get("types", {})
        gunLevel = util.getGunLevelVal(userId, config.MULTIPLE_MODE)

        idx = 0
        _stores = []
        _storeIds = []

        # 选择slot中商品
        def _isValidStore(_product):
            if _product["gunLevelRange"][0] <= gunLevel <= _product["gunLevelRange"][1]:
                if _product["maxBuyCount"] == -1 or buyTimeLimitedCountDict.get(_product["id"], 0) < _product["maxBuyCount"]:
                    return _product["id"] not in _storeIds
            return False

        for val in config.getTimeLimitedStoreConf().get("slot", []):
            idx += 1
            storeList = []
            for type in val.get("typeList", []):
                if typeStores.get(str(type), []):
                    storeList.extend(typeStores.get(str(type), []))
            storeList = [_v for _v in storeList if _isValidStore(_v)]
            if ftlog.is_debug():
                ftlog.debug("getTimeLimitedStoreTab, userId =", userId, "slot =", idx, "storeList =", storeList)
            totalRate = sum(map(lambda x: x.get("rate", 0), storeList), 0)
            rand = random.randint(0, totalRate)
            for item in storeList:
                if rand > item.get("rate", 0):
                    rand -= item.get("rate", 0)
                else:
                    _stores.append({"id": item["id"], "unlockGunLevel": val.get("unlockGunLevel", 0)})
                    _storeIds.append(item.get("id"))
                    break
        storeInfo.setdefault("stores", _stores)
        # # 计算下个自动刷新时间点
        # ts = int(time.time())
        # nextRefreshTS = 0
        # while nextRefreshTS == 0:
        #     _dayStartTS = util.getDayStartTimestamp(ts)
        #     for val in config.getTimeLimitedStoreConf().get("refresh", {}).get("auto"):
        #         if len(str(val).split(":")) >= 2:
        #             _hour = int(str(val).split(":")[0])
        #             _min = int(str(val).split(":")[1])
        #             _refreshTS = _dayStartTS + _hour * 3600 + _min * 60
        #             if int(time.time()) < _refreshTS:
        #                 nextRefreshTS = _refreshTS
        #                 if ftlog.is_debug():
        #                     ftlog.debug("getTimeLimitedStoreTab, userId =", userId, util.timestampToStr(nextRefreshTS))
        #                 break
        #     ts += 86400
        # daobase.executeUserCmd(userId, "HSET", key, GameData.tls_nextRefreshTS, nextRefreshTS)
        daobase.executeUserCmd(userId, "HSET", key, GameData.tls_buyCount, json.dumps({}))
        daobase.executeUserCmd(userId, "HSET", key, GameData.tls_info, json.dumps(storeInfo))
        if isRefresh:
            for _k in tls_refreshedTimes.keys():
                if int(_k) < dayStartTS:
                    del tls_refreshedTimes[_k]
            tls_refreshedTimes.setdefault(str(dayStartTS), 0)
            tls_refreshedTimes[str(dayStartTS)] += 1
            daobase.executeUserCmd(userId, "HSET", key, GameData.tls_refreshedTimes, json.dumps(tls_refreshedTimes))
    if code == 0:
        if ftlog.is_debug():
            ftlog.debug("getTimeLimitedStoreTab, userId =", userId, code, storeInfo, isRefresh)
    else:
        ftlog.warn("getTimeLimitedStoreTab, userId =", userId, code, storeInfo, isRefresh)
    return code, storeInfo


def getTimeLimitedStore(userId, clientId, isRefresh):
    """
    限时商城商店
    """
    vipLevel = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
    vipLimit = config.getTimeLimitedStoreConf().get("vipLimit", 0)
    if vipLevel < vipLimit:
        return []
    timeLimitedItems = []
    code, storeInfo = getTimeLimitedStoreTab(userId, clientId, isRefresh)
    lang = util.getLanguage(userId, clientId)
    key = GameData.timeLimitedStore % (FISH_GAMEID, userId)
    buyCount = json.loads(daobase.executeUserCmd(userId, "HGET", key, GameData.tls_buyCount) or "{}")
    timeLimitedStoreTab = {"name": config.getMultiLangTextConf("ID_TIMED_STORE", lang=lang), "subStore": "ruby", "iconType": "ruby"}
    refreshedTimes, maxRefreshTimes = getTimeLimitedStoreRefreshInfo(userId)
    # timeLimitedStoreTab.setdefault("nextRefreshLeftTime", nextRefreshLeftTime)
    # timeLimitedStoreTab.setdefault("refreshPrice", refreshPrice)
    timeLimitedStoreTab.setdefault("refreshedTimes", refreshedTimes)
    timeLimitedStoreTab.setdefault("maxRefreshTimes", maxRefreshTimes)
    timeLimitedStoreTab.setdefault("refresh", 1 if isRefresh else 0)
    timeLimitedStoreTab.setdefault("code", code)
    storeConf = config.getTimeLimitedStoreConf().get("stores", {})
    for store in storeInfo.get("stores", []):
        productId = store.get("id")
        product = storeConf.get(productId)
        if product is None:
            continue
        itemId = product["itemId"]
        label2 = ""
        if product.get("label2", ""):
            label2 = config.getMultiLangTextConf(product.get("label2", ""), lang=lang)
        data = {
            "id": productId,
            "name": config.getMultiLangTextConf(product["name"], lang=lang),
            "price": product["price"],
            "cur_price": product["price"],
            "pic": product.get("pic", ""),
            "buy_type": product["buyType"],
            "addition": "",
            "desc": label2,
            "tag": product.get("tag", 0),
            "grade": 1,
            "item_id": itemId,
            "count": product["count"],
            "other_buy_type": product.get("otherBuyType", {}),
            "otherProductInfo": getOtherBuyProduct(product.get("otherBuyType", {}), product["buyType"]),
            "unlockGunLevel": store.get("unlockGunLevel"),
            "label1": config.getMultiLangTextConf(product.get("label1"), lang=lang) if product.get("label1") else "",
            "label2": label2,
            "label3": config.getMultiLangTextConf(product.get("label3"), lang=lang) if product.get("label3") else "",
            "label1BgType": product.get("labelBgType") if product.get("labelBgType") else "",
            "label2BgType": product.get("label2BgType") if product.get("label2BgType") else "",
            "label3BgType": product.get("label3BgType") if product.get("label3BgType") else "",
            "info": chest_system.getChestInfo(itemId) if str(itemId).isdigit() and util.isChestRewardId(itemId) else {}
        }
        timeLimitedItems.append(data)
    timeLimitedStoreTab["items"] = timeLimitedItems
    return timeLimitedStoreTab


def canBuyResult(userId, tabName, productId, productConf, userVip, todayBuyInfo=None):
    """
    是否满足购买条件判断
    """
    todayBuyInfo = todayBuyInfo or weakdata.getDayFishData(userId, WeakData.shopBuyInfo, {})
    vipLimit = productConf.get("vip", 0)
    todayBuyNumLimit = productConf.get("limitCond", {}).get("userDailyCountLimit", 0)
    timeLimit = productConf.get("timeLimit", [])
    key = "%s_%s" % (tabName, str(productId))
    todayPurchasedNum = todayBuyInfo.get(key, 0)
    if userVip < vipLimit:
        return 1, 0
    if 0 < todayBuyNumLimit <= todayPurchasedNum:
        return 2, 0
    if timeLimit:
        startTime = util.getTimestampFromStr(timeLimit[0])
        endTime = util.getTimestampFromStr(timeLimit[-1])
        if int(time.time()) < startTime or int(time.time()) > endTime:
            return 3, 0
    return 0, max(todayBuyNumLimit - todayPurchasedNum, 0)


def resetBuyData(userId):
    """
    重置所有宝箱购买次数数据
    """
    return
    gamedata.setGameAttr(userId, FISH_GAMEID, GameData.buyChestCount, json.dumps([0, 0, 0, 0, 0, 0, 0]))


def updateChestStoreModuleTip(userId, level=0, gunLevel=0):
    """
    更新宝箱商城红点提示
    """
    # from newfish.entity import weakdata, module_tip
    # buyChestCount = weakdata.getDayFishData(userId, WeakData.buyDailyChestCount)
    # userLevel = level or util.getUserLevel(userId)
    # if not buyChestCount and userLevel >= config.getCommonValueByKey("chestStoreOpenLevel"):
    #     module_tip.addModuleTipEvent(userId, "store", "chestStore")
    # else:
    #     module_tip.cancelModuleTipEvent(userId, "store", "chestStore")
    from newfish.entity import weakdata, module_tip
    userLevel = level or util.getUserLevel(userId)
    gunLevel = gunLevel or util.getGunLevelVal(userId, config.MULTIPLE_MODE)
    clientId = util.getClientId(userId)
    items = config.getStoreConf(clientId).get("chestStore").get("items")
    module_tip.resetModuleTipEvent(userId, "store")
    # 检查宝箱商城和是否解锁.
    if userLevel >= config.getCommonValueByKey("chestStoreOpenLevel") and gunLevel >= config.getCommonValueByKey("chestStoreOpenGunLevel"):
        curTime = int(time.time())
        # 检查每日宝箱是否有可以免费领取的.
        productFreeTS = weakdata.getDayFishData(userId, WeakData.productFreeTS, {})
        for productId, freeTS in productFreeTS.iteritems():
            if items.get(str(productId)) and freeTS > curTime:
                break
        else:
            module_tip.addModuleTipEvent(userId, "store", "chestStore1")
        # 检查固定间隔宝箱是否有可领取的.
        productFreeTS = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.productFreeTS, {})
        for productId, freeTS in productFreeTS.iteritems():
            if items.get(str(productId)) and freeTS > curTime:
                break
        else:
            module_tip.addModuleTipEvent(userId, "store", "chestStore2")


def convertItemByDiamond(userId, convertCount, itemId, sendMsg=True, rebateItemId=0, clientId=""):
    """
    使用钻石转换为物品
    """
    itemId = int(itemId)
    convertCount = abs(convertCount)
    convertCount, costDiamondCount = getConvertToDiamondCount(userId, itemId, convertCount)
    if convertCount and rebateItemId and clientId:
        costDiamondCount, _ = getUseRebateItemPrice(userId, rebateItemId, costDiamondCount, config.BT_DIAMOND, itemId, clientId)
    if convertCount == 0:
        reason = 0
    elif userchip.getDiamond(userId) >= costDiamondCount >= 0 and convertCount > 0:
        consume = {"name": config.DIAMOND_KINDID, "count": -costDiamondCount}
        reward = {"name": itemId, "count": convertCount}
        reason = util.addRewards(userId, [consume, reward], "ASSEMBLE_ITEM", config.DIAMOND_KINDID)
    else:
        reason = 1
    if not sendMsg:
        return
    mo = MsgPack()
    mo.setCmd("store_config_fish")
    mo.setResult("action", "convertItem")
    mo.setResult("code", reason)
    router.sendToUser(mo, userId)


def getConvertToDiamondCount(userId, itemId, itemCount):
    """
    获取物品等值的钻石数量
    """
    itemId = int(itemId)
    userVip = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
    key = "convert%dToDRate" % itemId
    rate = config.getVipConf(userVip).get(key)
    if isinstance(rate, list) and len(rate) == 2 and rate[0] and rate[1]:
        if (rate[1] * itemCount) % rate[0] != 0:
            import math
            itemCount = int(math.ceil(rate[1] * itemCount * 1. / rate[0])) * rate[0] / rate[1]
        return itemCount, (rate[1] * itemCount) / rate[0]
    else:
        return itemCount, 0


def autoConvertVoucherToDiamond(userId, needDiamondCount):
    """
    代购券->钻石, 1:10
    """
    diamondCount = userchip.getDiamond(userId)
    if diamondCount >= needDiamondCount or needDiamondCount <= 0:
        return
    rate = 10
    costVoucherCount = (needDiamondCount - diamondCount) / rate
    if (needDiamondCount - diamondCount) % rate != 0:
        costVoucherCount += 1
    if util.balanceItem(userId, config.VOUCHER_KINDID) >= costVoucherCount > 0:
        consume = {"name": config.VOUCHER_KINDID, "count": -abs(costVoucherCount)}
        reward = {"name": config.DIAMOND_KINDID, "count": abs(costVoucherCount * rate)}
        vip_system.addUserVipExp(FISH_GAMEID, userId, abs(costVoucherCount) * 10, "BUY_PRODUCT", config.DIAMOND_KINDID, config.DIAMOND_KINDID, rmbs=abs(costVoucherCount))
        util.addRewards(userId, [consume, reward], "ASSEMBLE_ITEM", config.DIAMOND_KINDID)
        if ftlog.is_debug():
            ftlog.debug("autoConvertVoucherToDiamond, userId =", userId, needDiamondCount, diamondCount, costVoucherCount, util.balanceItem(userId, config.VOUCHER_KINDID))


def setAutoBuyAfterSDKPayData(userId, productIdA, productIdB, actionType, count):
    """
    设置sdk支付后自动购买商品的数据
    """
    from poker.entity.dao import daobase
    key = GameData.autoBuyAfterSDKPay % (FISH_GAMEID, userId)
    if len(str(productIdA)) == 0 or len(str(productIdB)) == 0 or count == 0:
        daobase.executeUserCmd(userId, "DEL", key)
    else:
        daobase.executeUserCmd(userId, "SET", key, json.dumps([productIdA, productIdB, actionType, count]))


def isBulletStore(storeId):
    """招财商品"""
    return storeId.find(str(config.BRONZE_BULLET_KINDID)) > -1 or storeId.find(str(config.SILVER_BULLET_KINDID)) > -1 \
                or storeId.find(str(config.GOLD_BULLET_KINDID)) > -1 or storeId.find("TY0044B") > -1


def getUseRebateItemPrice(userId, itemId, fullPrice, buyType, productId, clientId):
    """
    获取使用满减券后的价格
    """
    price = fullPrice
    ret = False
    if itemId == 0:
        return price, True
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    item = userBag.findItem(itemId)
    # 过期时间保留1分钟的余量.
    if item and not item.isDied(int(time.time()) - 60):
        actions = config.getItemConf(clientId, item.kindId).get("actions", [])
        for action in actions:
            if action["action"] != "rebate":
                continue
            for params in action["params"]:
                if ftlog.is_debug():
                    ftlog.debug("getUseRebateItemPrice, userId =", userId, "fullPrice =", fullPrice, "buyType =", buyType, "params =", params)
                if params["minPrice"] <= fullPrice and params["buyType"] == buyType:
                    _eventParam = int(productId) if str(productId).isdigit() else 0
                    userBag.removeItem(FISH_GAMEID, item, pktimestamp.getCurrentTimestamp(), "BI_NFISH_BUY_ITEM_CONSUME", _eventParam)
                    price = max(price - params["rebate"], 0)
                    ret = True
                    break
    if ftlog.is_debug():
        ftlog.debug("getUseRebateItemPrice, userId =", userId, "itemId =", itemId, "item =", item, "fullPrice =", fullPrice, "buyType =", buyType, "price =", price, "productId =", productId)
    return price, ret


def buyProductByDiamond(userId, productId, price, clientId, eventId, rebateItemId):
    """
    使用钻石购买商品
    """
    code = 1
    from poker.entity.configure import pokerconf
    productIdNumber = pokerconf.productIdToNumber(productId)
    price, isSucc = getUseRebateItemPrice(userId, rebateItemId, price, config.BT_DIAMOND, productIdNumber, clientId)
    # 不能出现使用满减券后不需要花钱的情况！！！
    if price > 0 and isSucc:
        autoConvertVoucherToDiamond(userId, price)
        consumeCount, final = userchip.incrDiamond(userId, FISH_GAMEID, -abs(price), 0, eventId, productIdNumber, clientId, param01=productId)
        if abs(consumeCount) != price:
            code = 2
        else:
            code = 0
    return code


def doUserBuyProductRet(userId, productId, count, code, buyType, clientId):
    """
    商城以外购买商品返回的消息
    """
    mo = MsgPack()
    mo.setCmd("product_buy")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("clientId", clientId)
    mo.setResult("productId", productId)
    mo.setResult("count", count)
    mo.setResult("buyType", buyType)
    mo.setResult("code", code)
    router.sendToUser(mo, userId)
    if ftlog.is_debug():
        ftlog.debug("doUserBuyProductRet, userId =", userId, "mo =", mo)


def _triggerLevelUpEvent(event):
    """
    用户达到宝箱商店解锁等级增加小红点
    """
    if event.level == config.getCommonValueByKey("chestStoreOpenLevel"):
        updateChestStoreModuleTip(event.userId, event.level, event.gunlevel)

def _triggerGunLevelUpEvent(event):
    """
    用户炮台达到宝箱商店解锁等级增加小红点
    """
    if event.gunLevel == config.getCommonValueByKey("chestStoreOpenGunLevel"):
        updateChestStoreModuleTip(event.userId, event.level, event.gunlevel)


def _triggerUserLoginEvent(event):
    """
    用户每日首次登录添加宝箱商店免费宝箱小红点
    """
    # if event.dayFirst:
    #     updateChestStoreModuleTip(event.userId)
    pass


def onTimer(event):
    """
    计时器
    """
    global _lastRefreshTimestamp
    timestamp = pktimestamp.getCurrentTimestamp()
    if timestamp - _lastRefreshTimestamp >= 60:
        couponStoreRefreshTime = config.getPublic("couponStoreRefreshTime", "00:00")
        refreshTS = util.timeStrToInt(couponStoreRefreshTime) + util.getDayStartTimestamp(timestamp)
        if _lastRefreshTimestamp < refreshTS <= timestamp:
            if ftlog.is_debug():
                ftlog.debug("store, refresh coupon store")
            key = MixData.buyProductServerCount % FISH_GAMEID
            daobase.executeMixCmd("DEL", key)
        storeConf = config.getStoreConf().get("hotStore", {}).get("items", {})
        for productId, product in storeConf.iteritems():
            if "dayHotRefreshTime" in product.get("limitCond", {}):
                dayHotRefreshTime = product.get("limitCond", {}).get("dayHotRefreshTime", "00:00")
                refreshHotTS = util.timeStrToInt(dayHotRefreshTime) + util.getDayStartTimestamp(timestamp)
                if _lastRefreshTimestamp < refreshHotTS <= timestamp:
                    key = MixData.buyHotProductServerCount % FISH_GAMEID
                    daobase.executeMixCmd("HSET", key, productId, 0)
        _lastRefreshTimestamp = timestamp


_inited = False
_lastRefreshTimestamp = 0

def initialize(isCenter):
    global _inited
    if not _inited:
        _inited = True
        from poker.entity.events.tyevent import EventUserLogin, EventHeartBeat
        from newfish.game import TGFish
        from newfish.entity.event import GunLevelUpEvent, UserLevelUpEvent
        TGFish.getEventBus().subscribe(GunLevelUpEvent, _triggerGunLevelUpEvent)
        TGFish.getEventBus().subscribe(UserLevelUpEvent, _triggerLevelUpEvent)
        TGFish.getEventBus().subscribe(EventUserLogin, _triggerUserLoginEvent)
        if isCenter:
            from poker.entity.events.tyeventbus import globalEventBus
            globalEventBus.subscribe(EventHeartBeat, onTimer)
