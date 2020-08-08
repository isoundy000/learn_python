#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/11

import time
import json
from operator import itemgetter

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.dao import gamedata, userchip
from poker.entity.configure import pokerconf
from hall.entity import hallitem, hallvip
from newfish.entity import config, util, weakdata, share_system, vip_system, store
from newfish.entity.redis_keys import GameData, WeakData, ABTestData
from newfish.entity.config import FISH_GAMEID, VOUCHER_KINDID, BT_VOUCHER
from newfish.entity.chest import chest_system
from newfish.entity.gun import gun_system
from newfish.entity.msg import GameMsg
from newfish.entity.honor import honor_system


SECONDOFDAY = 86400
DAYOFMONTH = 30


class GiftType:
    SAIL = 0        # 启航礼包（新手礼包）
    LIMITTIME = 1   # 限时礼包（已废弃）
    NORMAL = 2      # 普通礼包（限购1次，按续解锁，目前包含首充、超值、豪华、终极礼包）
    BANKRUPT = 3    # 破产礼包
    MONTHCARD = 4   # 月卡礼包
    LEVELUP = 5     # 升级礼包


class GiftBase(object):
    """
    礼包基类
    """
    giftType = None

    def __init__(self, userId, clientId):
        self.userId = userId
        self.clientId = clientId
        # 礼包类型
        # 该类型所有礼包ID列表
        self.giftListConf = config.getGiftListConf(clientId, self.giftType)
        # 可领取礼包
        self.availableGift = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.availableGift, [])
        # 玩家等级
        self.level = util.getLevelByGunLevel(self.userId)
        # 玩家VIP等级
        self.vipLevel = hallvip.userVipSystem.getUserVip(userId).vipLevel.level

    def getCurrentGiftConf(self):
        """
        获取当前可购买礼包的配置
        """
        raise NotImplementedError

    def getGiftInfo(self):
        """
        获取该类型的礼包信息
        """
        raise NotImplementedError

    def addGiftData(self, giftId):
        """
        使礼包变为可领取状态并添加礼包数据
        """
        raise NotImplementedError

    def addToAvailableGift(self, giftId):
        """
        添加礼包到可领取礼包数据中
        """
        self.availableGift = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.availableGift, [])
        if giftId not in self.availableGift:
            self.availableGift.append(giftId)
            gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.availableGift, json.dumps(self.availableGift))

    def getGiftDetail(self, giftConf, available, popup=0):
        """
        获取该类型下单个礼包的详细信息
        """
        gift = {}
        gift["giftId"] = giftConf["giftId"]
        gift["giftName"] = giftConf["giftName"]                             # 礼包名
        gift["productId"] = giftConf["productId"]                           # 商品ID
        gift["available"] = available                                       # 0:奖励不可领取 1:奖励可领取
        gift["popup"] = 1 if available == 1 else popup                      # 0:不主动弹出 1:主动弹出
        gift["price"] = giftConf["price"]                                   # 商品原价
        gift["price_direct"] = giftConf.get("price_direct", 0)              # 货币价格
        gift["price_diamond"] = giftConf.get("price_diamond", 0)            # 钻石价格
        gift["discountPrice"] = giftConf["discountPrice"]                   # 折扣价
        gift["buyType"] = giftConf["buyType"]                               # 支付方式
        gift["otherBuyType"] = giftConf.get("otherBuyType", {})             # 可以使用其他货币时字典key为货币类型，val为价格；不可使用时字典为空
        gift["otherProductInfo"] = {}
        # 特殊处理代购券商品数据
        from newfish.entity import store
        gift["otherProductInfo"] = store.getOtherBuyProduct(giftConf.get("otherBuyType", {}), giftConf["buyType"])  # {buy_type:["商品id","商品名",price]}
        gift["items"] = giftConf["items"]
        # 首次购买奖励
        gift["firstBuyRewards"] = giftConf.get("firstBuyRewards", [])       # 首次购买奖励
        # 购买立得
        gift["getAfterBuy"] = giftConf.get("getAfterBuy", [])
        return gift


class SailGift(GiftBase):
    """
    启航礼包
    """
    giftType = GiftType.SAIL

    def getCurrentGiftConf(self):
        """
        获取当前可显示礼包的配置
        """
        for giftId in self.giftListConf:
            return config.getGiftConf(self.clientId, giftId)

    def getGiftInfo(self):
        """
        获取礼包信息
        """
        sailGift = {}
        giftConf = self.getCurrentGiftConf()
        if giftConf:
            giftId = giftConf["giftId"]
            normalGift = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.normalGift, [])
            if giftId not in normalGift:
                # 新用户直接把启航礼包加入到可领取礼包中
                self.addGiftData(giftId)
                # 增加充值奖池（新用户概率ab测试）
                newbieMode = gamedata.getGameAttr(self.userId, FISH_GAMEID, ABTestData.newbieMode)
                if newbieMode in ["b", "c"]:
                    # 破产ab测试
                    bankruptTestMode = gamedata.getGameAttr(self.userId, FISH_GAMEID, ABTestData.bankruptTestMode)  # 破产测试
                    if bankruptTestMode == "b":
                        rechargeBonus = config.getPublic("bankruptTestModeBonusB", 0)
                    else:
                        rechargeBonus = config.getPublic("bankruptTestModeBonusA", 0)
                    # gamedata.incrGameAttr(self.userId, FISH_GAMEID, GameData.rechargeBonus, rechargeBonus)
                    util.incrUserRechargeBonus(self.userId, rechargeBonus)                              # 增加充值奖池
                else:
                    # gamedata.incrGameAttr(self.userId, FISH_GAMEID, GameData.rechargeBonus, 10000)
                    util.incrUserRechargeBonus(self.userId, 10000)
                # 新手ABC测试.
                testMode = util.getNewbieABCTestMode(self.userId)
                registerRechargeBonus = config.getABTestConf("abcTest").get("registerRechargeBonus", {}).get(testMode, 0)
                util.incrUserRechargeBonus(self.userId, registerRechargeBonus)
                if ftlog.is_debug():
                    ftlog.debug("abc test, userId =", self.userId, "mode =", testMode, "registerRechargeBonus =", registerRechargeBonus)

            # 启航礼包目前为手动领取
            availableGift = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.availableGift, [])
            if giftId in availableGift:
                sailGift["giftId"] = giftId
                sailGift["available"] = 1
                sailGift["roomId"] = giftConf["fishPool"]
                sailGift["items"] = giftConf["items"]
        return sailGift

    def addGiftData(self, giftId):
        """
        使礼包变为可领取状态并添加礼包数据
        """
        code = 1
        normalGifts = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.normalGift, [])
        if giftId not in normalGifts:
            normalGifts.append(giftId)
            gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.normalGift, json.dumps(normalGifts))
            self.addToAvailableGift(giftId)
            code = 0
        return code


class NormalGift(GiftBase):
    """
    普通礼包
    """
    giftType = GiftType.NORMAL

    def getCurrentGiftConf(self):
        """
        获取当前可购买礼包的配置
        """
        isIn, roomId, _, _ = util.isInFishTable(self.userId)
        bigRoomId, _ = util.getBigRoomId(roomId)
        vipLevel = hallvip.userVipSystem.getVipInfo(self.userId).get("level", 0)
        # 已购买礼包信息
        normalGiftInfo = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.normalGift, [])
        # 已过期礼包
        expiredGift = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.expiredGift, [])
        # 即将过期礼包
        futureExpiredGift = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.futureExpiredGift, [])

        for giftId in self.giftListConf:
            giftConf = config.getGiftConf(self.clientId, giftId)
            if not giftConf:
                continue
            # 已过期
            if giftId in expiredGift:
                continue
            # 房间限制
            if len(giftConf["roomId"]) > 0 and bigRoomId not in giftConf["roomId"]:
                continue
            # vip限制
            if giftConf["vip"] > vipLevel:
                continue
            # 是否需要先购买某个礼包
            giftLimit = giftConf["giftLimit"]
            if giftLimit != 0 and giftLimit not in normalGiftInfo and giftLimit not in expiredGift:
                continue
            if giftLimit != 0 and giftLimit in normalGiftInfo and giftLimit in self.availableGift:
                continue
            # 已经领取过的
            if giftConf["giftId"] in normalGiftInfo and giftConf["giftId"] not in self.availableGift:
                continue
            # 可以领取的
            elif giftConf["giftId"] in normalGiftInfo and giftConf["giftId"] in self.availableGift:
                return giftConf
            # 未购买的
            if giftConf["giftId"] not in normalGiftInfo:
                expireTime = giftConf.get("expireTime", -1)
                # 游戏过程中，获取礼包数据，属于即将过期中的礼包即使过期也正常显示，下次登录才真正过期
                if expireTime > 0 and giftId not in futureExpiredGift:
                    buyGiftTimestamp = gamedata.getGameAttrInt(self.userId, FISH_GAMEID, GameData.buyGiftTimestamp)
                    # 礼包已过期
                    if int(time.time()) > buyGiftTimestamp + expireTime * 60:
                        expiredGift.append(giftId)
                        gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.expiredGift, json.dumps(expiredGift))
                        continue
                    else:  # 礼包未过期，把当前礼包加入到即将过期礼包中
                        futureExpiredGift.append(giftId)
                        gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.futureExpiredGift, json.dumps(futureExpiredGift))
                return giftConf
        return None

    def getGiftInfo(self):
        """
        获取礼包信息
        """
        giftConf = self.getCurrentGiftConf()
        if not giftConf:
            return {}
        available = 1 if giftConf["giftId"] in self.availableGift else 0            # 奖励可领取
        if available:
            return self.getGiftDetail(giftConf, available)
        else:
            alreadyTakenNormalGift = gamedata.getGameAttrInt(self.userId, FISH_GAMEID, GameData.alreadyTakenNormalGift)  # 此次登录是否领取了普通礼包
            buyGiftTimestamp = gamedata.getGameAttrInt(self.userId, FISH_GAMEID, GameData.buyGiftTimestamp)
            curTimestamp = int(time.time())
            giftConf = config.getGiftConf(self.clientId, giftConf["giftId"])
            if not giftConf:
                return {}
            # 判断是否需要下次登录才显示或者间隔一段时间后才显示
            reloadSucc = (giftConf.get("showAfterReload", 0) == 0 or alreadyTakenNormalGift == 0)
            waitTimesSucc = (giftConf.get("showAfterTimes", -1) != -1 and curTimestamp >= buyGiftTimestamp + 60 * giftConf["showAfterTimes"])
            if reloadSucc or waitTimesSucc:
                return self.getGiftDetail(giftConf, available)
        return {}

    def addGiftData(self, giftId):
        """
        使礼包变为可领取状态并添加礼包数据
        """
        code = 1
        normalGifts = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.normalGift, [])
        if giftId not in normalGifts:
            normalGifts.append(giftId)
            gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.normalGift, json.dumps(normalGifts))
            self.addToAvailableGift(giftId)
            code = 0
        return code


class BankruptGift(GiftBase):
    """
    破产礼包
    """
    giftType = GiftType.BANKRUPT

    def getCurrentGiftConf(self):
        """
        获取当前可显示礼包的配置
        """
        pass


class MonthCardGift(GiftBase):
    """
    月卡礼包
    """
    giftType = GiftType.MONTHCARD


class LevelUpGift(GiftBase):
    """
    升级礼包
    """
    giftType = GiftType.LEVELUP

    def getCurrentGiftConf(self):
        """
        获取当前可显示礼包的配置
        """
        isIn, roomId, _, _ = util.isInFishTable(self.userId)
        bigRoomId, _ = util.getBigRoomId(roomId)
        # 已购买的普通礼包ID
        normalGiftInfo = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.normalGift, [])
        # 已购买的升级礼包ID
        levelUpGiftInfo = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.levelUpGift, [])
        # 升级礼包过期时间
        giftExpireTS = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.giftsExpireTS, {})
        recommonGift = None











def doSendFishGift(userId, clientId):
    """
    发送礼包消息
    """
    doSendFishSeriesGift(userId, clientId)


def doSendFishSeriesGift(userId, clientId):
    """
    发送礼包合集消息（礼包ab测试之b模式）
    """
    if not util.isVersionLimit(userId) and not util.isPurchaseLimit(userId) and util.isFinishAllRedTask(userId):
        showIndex, seriesGift = getSeriesGift(userId, clientId)
    else:
        showIndex, seriesGift = -1, []
    message = MsgPack()
    message.setCmd("fishSeriesGift")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    message.setResult("showIndex", showIndex)
    message.setResult("seriesGift", seriesGift)
    router.sendToUser(message, userId)


def getSeriesGift(userId, clientId):
    """
    获得系列礼包合集
    """
    # 礼包合集类
    seriesGiftClass = {
        GiftType.NORMAL: NormalGift,
        GiftType.LEVELUP: LevelUpGift
    }
    seriesGift = []
    # 已购买已领取且金额最大的礼包Id
    maxBoughtGiftId = -1
    # 已购买的普通礼包ID
    normalGiftInfo = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.normalGift, [])
    # 已购买的升级礼包ID
    levelUpGiftInfo = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.levelUpGift, [])
    # 未领取礼包
    availableGift = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.availableGift, [])
    # 普通礼包
    normalGiftIds = config.getGiftListConf(clientId, GiftType.NORMAL)
    # if isupgradeGunTestMode(userId):
    #     for giftId in normalGiftIds:
    #         if giftId == 70212801:
    #             normalGiftIds.remove(giftId)
    #             normalGiftIds.remove(giftId+1)    # a模式下giftId为70212801何70212802的两个礼包不显示
    # else:
    #     for giftId in normalGiftIds:
    #         if giftId == 702128:
    #             normalGiftIds.remove(giftId)
    #     ftlog.debug("isupgradeGunTestMode =", isupgradeGunTestMode, "userid = ", userId)
    for giftId in normalGiftIds:
        if giftId == 70212801:
            normalGiftIds.remove(giftId)
            normalGiftIds.remove(giftId + 1)  # a模式下giftId为70212801何70212802的两个礼包不显示
    # 升级礼包
    levelUpGiftIds = config.getGiftListConf(clientId, GiftType.LEVELUP)
    # 所有系列礼包，并按价格排序
    allSeriesGiftConf = []
    allSeriesGiftId = []
    for giftId in normalGiftIds + levelUpGiftIds:
        _gift = config.getGiftConf(clientId, giftId)
        if not _gift:
            continue
        allSeriesGiftConf.append(dict(_gift))
    if allSeriesGiftConf:
        allSeriesGiftConf = sorted(allSeriesGiftConf, key=itemgetter("price"))
        allSeriesGiftId = map(lambda conf: conf["giftId"], allSeriesGiftConf)

    # 从所有礼包中筛选出可展示的礼包
    for _, giftConf in enumerate(allSeriesGiftConf):
        giftId = giftConf["giftId"]
        if giftId in availableGift or (giftId not in normalGiftInfo and giftId not in levelUpGiftInfo):
            available = 1 if giftId in availableGift else 0
            giftDetail = seriesGiftClass[giftConf["giftType"]](userId, clientId).getGiftDetail(giftConf, available)
            seriesGift.append(giftDetail)
        # 已购买已领取且金额最大的礼包Id
        if (giftId in normalGiftInfo or giftId in levelUpGiftInfo) and giftId not in availableGift:
            maxBoughtGiftId = giftId

    # 选出推荐购买的礼包
    seriesGiftId = map(lambda conf: conf["giftId"], seriesGift)
    # 推荐的礼包默认为第一个
    recommendGiftId = seriesGiftId[0] if seriesGiftId else None
    if recommendGiftId:
        # 推荐序列中已购买且金额最大的下一个礼包，没有则为最后一个
        if maxBoughtGiftId in allSeriesGiftId:
            recommendGiftId = allSeriesGiftId[
                min(allSeriesGiftId.index(maxBoughtGiftId) + 1, len(allSeriesGiftId) - 1)]
        if recommendGiftId not in seriesGiftId:
            recommendGiftId = seriesGiftId[-1]
        # 优先显示未领取且金额最大的
        for _, giftDetail in enumerate(seriesGift):
            if giftDetail["giftId"] in availableGift:
                recommendGiftId = giftDetail["giftId"]
    # 推荐的礼包下标
    showIndex = seriesGiftId.index(recommendGiftId) if recommendGiftId else -1
    return showIndex, seriesGift





def doBuyFishGift(userId, clientId, giftId, buyType=None, itemId=0):
    """
    购买礼包
    """
    ftlog.debug("doBuyFishGift===>", userId, clientId, giftId, buyType, itemId)


def doGetFishGiftReward(userId, clientId, giftId):
    """
    领取礼包
    """
    pass



_inited = False


def initialize():
    ftlog.debug("newfish gift_system initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from poker.entity.events.tyevent import ChargeNotifyEvent, EventUserLogin
        from hall.game import TGHall
        from newfish.game import TGFish
        from newfish.entity.event import CheckLimitTimeGiftEvent, NFChargeNotifyEvent
        TGHall.getEventBus().subscribe(ChargeNotifyEvent, _triggerChargeNotifyEvent)
        TGFish.getEventBus().subscribe(NFChargeNotifyEvent, _triggerChargeNotifyEvent)
        # TGFish.getEventBus().subscribe(CheckLimitTimeGiftEvent, _triggerCheckLimitTimeGiftEvent)
        TGFish.getEventBus().subscribe(EventUserLogin, _triggerUserLoginEvent)
    ftlog.debug("newfish gift_system initialize end")