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
from newfish.entity.config import FISH_GAMEID, BT_VOUCHER
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
    STT_EXCHANGE = 10       # 月度兑换


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
    StoreTabType.STT_EXCHANGE: "exchangeStore"
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
    elif actionType == StoreTabType.STT_EXCHANGE:       # 兑换商城
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
    updateChestStoreModuleTip(userId, util.getUnlockCheckLevel(userId))


def isInvalidePruduct(isVerLimited, product, level, clientVersion, ownGunSkinSkins=None):
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
    elif actionType == StoreTabType.STT_EXCHANGE:
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
        self.level = util.getStoreCheckLevel(userId)            # 用户等级 获取玩家商城需要检测的等级
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
                if isInvalidePruduct(self.isVerLimited, product, self.level, self.clientVersion):
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
                if isInvalidePruduct(self.isVerLimited, product, self.level, self.clientVersion):
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
            if isInvalidePruduct(self.isVerLimited, product, self.level, self.clientVersion, ownGunSkinSkins):
                continue
            productObj = CreateProduct(self, self.actionType, chestId, product, self.userId, self.clientId)
            if productObj:
                data = productObj.parse()
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
        if not self.isVerLimited or self.platformOS == "android":
            for productId, product in storeConf.iteritems():
                if isInvalidePruduct(self.isVerLimited, product, self.level, self.clientVersion):
                    continue
                if self.isAppClient and product.get("limitCond", {}).get("appVisible", 1) == 0:  # app客户端隐藏商品
                    continue
                productObj = CreateProduct(self, self.actionType, productId, product, self.userId, self.clientId)
                if productObj:
                    data = productObj.parse()
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
        exchangeStoreTab = {"name": config.getMultiLangTextConf("ID_BUY_COIN", lang=self.lang), "subStore": "exchange"}
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
        else:
            self.lang = util.getLanguage(userId, clientId)
            self.vipLevel = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
            self.level = util.getStoreCheckLevel(userId)
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
            price = self.product["cur_price"][0] if self.product["cur_price"] else self.product["price"]
        return price

    def getItemCount(self):
        """
        获取商品中道具数量
        """
        return self.product.get("count")[self.idx]

    def getName(self):
        """
        获取商品名字
        """
        if self.product["name"] and self.idx < len(self.product["name"]) and self.product["name"][self.idx]:
            return config.getMultiLangTextConf(self.product["name"][self.idx], lang=self.lang)
        else:
            return ""

    def getLabel1(self):
        if self.product["label1"] and self.idx < len(self.product["label1"]) and self.product["label1"][self.idx]:
            return config.getMultiLangTextConf(self.product["label1"][self.idx], lang=self.lang)
        else:
            return ""

    def getLabel2(self):
        if self.product["label2"] and self.idx < len(self.product["label2"]) and self.product["label2"][self.idx]:
            return config.getMultiLangTextConf(self.product["label2"][self.idx], lang=self.lang)
        else:
            return ""

    def getLabel3(self):
        if self.product["label3"] and self.idx < len(self.product["label3"]) and self.product["label3"][self.idx]:
            return config.getMultiLangTextConf(self.product["label3"][self.idx], lang=self.lang)
        else:
            return ""

    def getLabel1BgType(self):
        if "label1BgType" not in self.product:
            return ""
        if self.product["label1BgType"] and self.idx < len(self.product["label1BgType"]) and self.product["label1BgType"][self.idx]:
            return self.product["label1BgType"][self.idx]
        else:
            return ""

    def getLabel2BgType(self):
        if "label2BgType" not in self.product:
            return ""
        if self.product["label2BgType"] and self.idx < len(self.product["label2BgType"]) and self.product["label2BgType"][self.idx]:
            return self.product["label2BgType"][self.idx]
        else:
            return ""

    def getLabel3BgType(self):
        if "label3BgType" not in self.product:
            return ""
        if self.product["label3BgType"] and self.idx < len(self.product["label3BgType"]) and self.product["label3BgType"][self.idx]:
            return self.product["label3BgType"][self.idx]
        else:
            return ""

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
        self.buyChestCountList = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.buyChestCount, [0, 0, 0, 0])
        itemId = self.product.get("itemId", 0)
        self.buyChestCount = 0
        if str(itemId).isdigit() and util.isChestRewardId(itemId):
            if self.product["order"] == 0:
                self.buyChestCount = weakdata.getDayFishData(self.userId, "buyDailyChestCount", 0)
            elif self.buyChestCountList and len(self.buyChestCountList) > self.product["order"]:
                self.buyChestCount = self.buyChestCountList[self.product["order"]]
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
            ftlog.debug("_checkFreePrice, ", self.userId, freeData, productFreeTS, ts)
            return True if self.curTime >= ts else False
        return False

    def _getIdx(self):
        """
        获取对应索引
        """
        return 0

    def getPrice(self, buyType=None):
        """
        获取商品价格
        """
        if self.isFree:
            return 0
        idx = self.buyChestCount if self.buyChestCount < len(self.product["cur_price"]) else -1
        price = self.product["cur_price"][idx]
        return price

    def getName(self):
        """
        获取商品名字
        """
        name = super(ItemProduct, self).getName()
        # 珍珠商品的名字特殊处理.
        if self.product.get("itemId", 0) == config.PEARL_KINDID:
            return "%sx%d" % (name, self.getItemCount())
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
                    label2 = "%d / %d" % (len(freeData.get("time")) - self.buyChestCount, len(freeData.get("time")))
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
                        label2 = "remain %d hours" % h
                    else:
                        label2 = "remain %d miniutes" % m
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
        return 0



def getPearlStore(userId, clientId):
    """
    珍珠商店
    """
    pass



def getGunSkinStore(userId, clientId):
    """
    火炮皮肤商店
    """
    pass



def getBulletStore(userId, clientId):
    """
    招财珠商店
    """
    pass


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





def _triggerLevelUpEvent(event):
    """
    用户达到宝箱商店解锁等级增加小红点
    """
    if event.level == config.getCommonValueByKey("chestStoreOpenLevel"):
        updateChestStoreModuleTip(event.userId, event.level)


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
    pass


_inited = False
_lastRefreshTimestamp = 0


def initialize(isCenter):
    if ftlog.is_debug():
        ftlog.debug("newfish store initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from poker.entity.events.tyevent import EventUserLogin, EventHeartBeat
        from newfish.game import TGFish
        from newfish.entity.event import LevelUpEvent, UserLevelUpEvent
        TGFish.getEventBus().subscribe(LevelUpEvent, _triggerLevelUpEvent)
        TGFish.getEventBus().subscribe(UserLevelUpEvent, _triggerLevelUpEvent)
        TGFish.getEventBus().subscribe(EventUserLogin, _triggerUserLoginEvent)
        if isCenter:
            from poker.entity.events.tyeventbus import globalEventBus
            globalEventBus.subscribe(EventHeartBeat, onTimer)
    if ftlog.is_debug():
        ftlog.debug("newfish store initialize end")