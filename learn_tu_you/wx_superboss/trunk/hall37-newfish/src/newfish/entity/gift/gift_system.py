#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/11

import time
import json
from operator import itemgetter

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack

from newfish.entity.gift.level_gift import doSendLevelGift
from poker.protocol import router
from poker.entity.dao import gamedata, userchip
from poker.entity.configure import pokerconf
from hall.entity import hallitem, hallvip
from newfish.entity import config, util, weakdata, share_system, vip_system, store
from newfish.entity.redis_keys import GameData, WeakData, ABTestData
from newfish.entity.config import FISH_GAMEID, VOUCHER_KINDID, BT_VOUCHER, MULTIPLE_MODE
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
        self.level = util.getUserLevel(self.userId)
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
        gift["popup"] = 1 if available == 1 else popup                      # 0:不主动弹出 1:主动弹出 available为2时，表示已领取，不弹出
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
                    else:   # 礼包未过期，把当前礼包加入到即将过期礼包中
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
        isIn, roomId, _, _ = util.isInFishTable(self.userId)
        bigRoomId, _ = util.getBigRoomId(roomId)
        fishPool = util.getFishPoolByBigRoomId(bigRoomId)
        if not isIn:
            return None
        # 各渔场破产次数
        bankruptCount = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.coinShortageCount, {})
        bankruptTimes = bankruptCount.get(str(fishPool), 0)
        # 获取当前消费的礼包最高价格.
        consumePriceMax = 0
        # 获取已购买的普通礼包中最高价格
        # normalGiftInfo = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.normalGift, [])
        # buyGiftTimes = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.buyGiftTimes, {})
        # normalGiftInfo.extend(buyGiftTimes.keys())
        # for giftId in normalGiftInfo:
        #     gift = config.getGiftConf(self.clientId, str(giftId))
        #     price = gift.get("discountPrice", 0) if gift else 0
        #     if price > consumePriceMax:
        #         consumePriceMax = price
        # 已经购买等级礼包中最高的价格
        buyLevelGift = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.buyLevelGift, [])
        for giftId in buyLevelGift:
            levelGiftConf = config.getLevelGiftConf().get(str(giftId), {})
            price = levelGiftConf.get("discountPrice", 0) if levelGiftConf else 0
            if price > consumePriceMax:
                consumePriceMax = price
        # 获取已购买的每日礼包中最高价格
        buyFishDailyGiftTimes = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.buyFishDailyGiftTimes, {})
        for giftId in buyFishDailyGiftTimes.keys():
            gift = config.getDailyGiftConf(self.clientId).get(str(giftId), {})
            price = gift.get("price", 0) if gift else 0
            if price > consumePriceMax:
                consumePriceMax = price
        # 每日已购买的破产礼包
        dailyGifts = weakdata.getDayFishData(self.userId, WeakData.dailyGift, [])
        # 当前房间可以使用的破产礼包列表.
        _giftList = []
        for giftId in self.giftListConf:
            giftConf = config.getGiftConf(self.clientId, giftId)
            if not giftConf:
                continue
            # 房间限制
            if len(giftConf["roomId"]) > 0 and bigRoomId not in giftConf["roomId"]:
                continue
            available = 1 if giftConf["giftId"] in self.availableGift else 0  # 1可领取 0 不可领
            # 已购买不显示.
            if available == 0 and giftId in dailyGifts:
                continue
            _giftList.append(giftId)

        recommonGift = None
        minPriceDiff = 9999
        # 玩家未消费，且在[44404, 44405]房间中第一次破产, 其余房间为前两次时，使用中档礼包
        useMidValueGift = (consumePriceMax == 0 and bankruptTimes <= (1 if bigRoomId in [44404, 44405] else 5))
        for giftId in _giftList:
            giftConf = config.getGiftConf(self.clientId, giftId)
            if not giftConf:
                continue
            available = 1 if giftConf["giftId"] in self.availableGift else 0  # 1可领取 0 不可领
            # 房间限制
            if len(giftConf["roomId"]) > 0 and bigRoomId not in giftConf["roomId"]:
                continue
            # 可领取
            if available == 1:
                return giftConf
            # vip限制
            if giftConf["vip"] > self.vipLevel:
                continue
            # 使用中档礼包
            if useMidValueGift:
                if giftId == _giftList[len(_giftList) / 2]:
                    recommonGift = giftConf
                    break
            else:  # 消费价格匹配的礼包
                priceDiff = abs(giftConf["discountPrice"] - consumePriceMax)
                if priceDiff < minPriceDiff:
                    minPriceDiff = priceDiff
                    recommonGift = giftConf
        if ftlog.is_debug():
            ftlog.debug("getCurrentGiftConf->", self.userId, bigRoomId, consumePriceMax,
                        bankruptTimes, recommonGift, bankruptCount, useMidValueGift)
        # # 该存档仅用于礼包abc测试使用.
        # gamedata.delGameAttr(self.userId, FISH_GAMEID, GameData.bankruptGiftInfo)
        return recommonGift

    def getCurrentGiftConf_Abc(self, mode):
        """
        获取当前可显示礼包的配置
        """
        isIn, roomId, _, _ = util.isInFishTable(self.userId)
        bigRoomId, _ = util.getBigRoomId(roomId)
        fishPool = util.getFishPoolByBigRoomId(bigRoomId)
        if not isIn:
            return None, ""
        # 获取礼包档位.
        grade = self._getGrade(fishPool)
        buyTimes = self._getBuyTimes(fishPool)
        giftAbcTestConf = config.getGiftAbcTestConf(self.clientId)
        giftListConf = giftAbcTestConf.get("data", {}).get(str(fishPool), {}).get(grade, {}).get("giftList", {}).get(mode, [])
        recommonGift = None
        # 当前房间可以使用的破产礼包列表.
        for giftId in giftListConf:
            giftConf = giftAbcTestConf.get("gift", {}).get(str(giftId))
            if not giftConf:
                continue
            available = 1 if giftConf["giftId"] in self.availableGift else 0  # 1可领取 0 不可领
            # 优先展示可领取的礼包.
            if available == 1:
                recommonGift = giftConf
                break
        # 没有可领取礼包则按照已购买次数显示礼包.
        if not recommonGift and 0 <= buyTimes < len(giftListConf):
            giftId = giftListConf[buyTimes]
            giftConf = giftAbcTestConf.get("gift", {}).get(str(giftId))
            if giftConf:
                recommonGift = giftConf
        if ftlog.is_debug():
            ftlog.debug("getCurrentGiftConf_Abc, userId =", self.userId, "fishPool =", fishPool, "grade =", grade, "mode =", mode, "gift =", recommonGift)
        lang = util.getLanguage(self.userId, self.clientId)
        remainTimes = max(0, len(giftListConf) - buyTimes)
        if recommonGift:
            gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.bankruptGiftInfo, json.dumps([fishPool, grade]))
            tip = config.getMultiLangTextConf("ID_BANKRUPT_GIFT_TIP", lang=lang).format(remainTimes)
        else:
            # gamedata.delGameAttr(self.userId, FISH_GAMEID, GameData.bankruptGiftInfo)
            tip = ""
        return recommonGift, tip

    def getGiftInfo(self):
        """
        获取礼包信息
        """
        dailyGift = []
        # a模式维持原状.
        mode = util.getGiftAbcTestMode(self.userId)
        if mode == "a":
            giftConf = self.getCurrentGiftConf()
            lang = util.getLanguage(self.userId, self.clientId)
            tip = config.getMultiLangTextConf("ID_BANKRUPT_GIFT_TIP", lang=lang).format(1) if giftConf else ""
        else:                                                                       # bc模式.
            giftConf, tip = self.getCurrentGiftConf_Abc(mode)
        if giftConf:
            available = 1 if giftConf["giftId"] in self.availableGift else 0
            dailyGift.append(self.getGiftDetail(giftConf, available))
        return dailyGift, tip

    def addGiftData(self, giftId):
        """
        使礼包变为可领取状态并添加礼包数据
        """
        code = 1
        # a模式维持原状.
        mode = util.getGiftAbcTestMode(self.userId)
        if mode == "a":
            dailyGifts = weakdata.getDayFishData(self.userId, WeakData.dailyGift, [])
            isValid = giftId not in dailyGifts
            # 每个破产礼包每日只能购买一次.
            if isValid:
                dailyGifts.append(giftId)
                weakdata.setDayFishData(self.userId, WeakData.dailyGift, json.dumps(dailyGifts))
        else:
            bankruptGiftInfo = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.bankruptGiftInfo)
            if bankruptGiftInfo:
                fishPool, grade = bankruptGiftInfo
                # 检查礼包是否存在以及购买次数.
                giftAbcTestConf = config.getGiftAbcTestConf(self.clientId).get("data", {})
                giftListConf = giftAbcTestConf.get(str(fishPool), {}).get(grade, {}).get("giftList", {}).get(mode, [])
                buyTimes = self._getBuyTimes(fishPool)
                isValid = 0 <= buyTimes < len(giftListConf) and str(giftId) == str(giftListConf[buyTimes])
            else:
                isValid = False
        if isValid:
            self.addToAvailableGift(giftId)
            code = 0
            # 记录破产礼包累计购买次数
            giftConf = getGiftConf(self.clientId, giftId)
            key = giftConf.get("recordKey") if giftConf else 0
            if key:
                buyTimes = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.brokeGift, {})
                buyTimes.setdefault(str(key), 0)
                buyTimes[str(key)] += 1
                gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.brokeGift, json.dumps(buyTimes))
        return code

    def _getGrade(self, fishPool):
        """
        获取abc测试中的礼包档位
        """
        buyBankruptGift = weakdata.getDayFishData(self.userId, WeakData.buyBankruptGiftTimesPerPool, {})
        grade = buyBankruptGift.get(str(fishPool), {}).get("grade")
        # 根据当前的消费能力计算礼包档位.
        if not grade:
            # 获取当前消费的礼包最高价格.
            consumePriceMax = 0
            # 获取已购买的普通礼包中最高价格
            normalGiftInfo = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.normalGift, [])
            buyGiftTimes = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.buyGiftTimes, {})
            normalGiftInfo.extend(buyGiftTimes.keys())
            for giftId in normalGiftInfo:
                gift = getGiftConf(self.clientId, str(giftId))
                price = gift.get("discountPrice", 0) if gift else 0
                if price > consumePriceMax:
                    consumePriceMax = price
            # 获取已购买的每日礼包中最高价格
            buyFishDailyGiftTimes = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.buyFishDailyGiftTimes, {})
            for giftId in buyFishDailyGiftTimes.keys():
                gift = config.getDailyGiftConf(self.clientId).get(str(giftId), {})
                price = gift.get("price", 0) if gift else 0
                if price > consumePriceMax:
                    consumePriceMax = price
            # 选择合适的礼包档位.
            giftAbcTestConf = config.getGiftAbcTestConf(self.clientId).get("data", {}).get(str(fishPool), {})
            _minDiff = -1
            for k, v in giftAbcTestConf.iteritems():
                if abs(v["price"] - consumePriceMax) < _minDiff or _minDiff == -1:
                    _minDiff = abs(v["price"] - consumePriceMax)
                    grade = k
        return grade

    def _getBuyTimes(self, fishPool):
        """
        获取abc测试中礼包购买次数
        """
        buyBankruptGift = weakdata.getDayFishData(self.userId, WeakData.buyBankruptGiftTimesPerPool, {})
        buyTimes = buyBankruptGift.get(str(fishPool), {}).get("count", 0)
        return buyTimes


class MonthCardGift(GiftBase):
    """
    月卡礼包
    """
    giftType = GiftType.MONTHCARD

    def getCurrentGiftConf(self):
        """
        获取当前可显示礼包的配置
        """
        userBag = hallitem.itemSystem.loadUserAssets(self.userId).getUserBag()
        itemPermanent = userBag.getItemByKindId(config.PERMANENT_MONTH_CARD_KINDID)
        item = userBag.getItemByKindId(config.MONTH_CARD_KINDID)
        giftList = []
        for giftId in self.giftListConf:
            giftConf = config.getGiftConf(self.clientId, giftId)
            # 已购买永久月卡并且普通月卡未买或是普通月卡已过期,普通月卡不再显示.
            if giftConf and giftConf["monthCard"]["name"] == config.MONTH_CARD_KINDID \
                    and itemPermanent and (item is None or item.isDied(int(time.time()))):
                continue
            giftList.append(giftConf)
        return giftList

    def getGiftInfo(self):
        """
        获取礼包信息
        """
        giftInfo = []
        giftConfList = self.getCurrentGiftConf()
        for giftConf in giftConfList:
            if giftConf and giftConf["minLevelLimit"] <= self.level <= giftConf["maxLevelLimit"]:
                itemId = giftConf["monthCard"]["name"]
                userBag = hallitem.itemSystem.loadUserAssets(self.userId).getUserBag()
                item = userBag.getItemByKindId(itemId)
                if item and not item.isDied(int(time.time())):
                    # 今日是否已领取月卡奖励
                    if itemId == config.MONTH_CARD_KINDID:
                        available = 2 if weakdata.getDayFishData(self.userId, WeakData.getMonthCardGift, 0) > 0 else 1
                    else:
                        available = 2 if weakdata.getDayFishData(self.userId, WeakData.getPermanentMonthCardGift, 0) > 0 else 1
                else:
                    available = 0  # 0：未购买月卡 1：未领取 2：已领取
                monthCardGift = self.getGiftDetail(giftConf, available)
                giftInfo.append([monthCardGift, itemId, available])
        return giftInfo

    def addGiftData(self, giftId):
        """
        使礼包变为可领取状态并添加礼包数据
        """
        extraRwards = []
        giftConf = config.getGiftConf(self.clientId, giftId)
        itemId = giftConf["monthCard"]["name"]
        count = giftConf["monthCard"]["count"]
        userBag = hallitem.itemSystem.loadUserAssets(self.userId).getUserBag()
        itemPermanent = userBag.getItemByKindId(config.PERMANENT_MONTH_CARD_KINDID)
        # 已购买永久月卡后不可以再次购买任何月卡.
        if itemPermanent:
            return 1, extraRwards
        item = userBag.getItemByKindId(itemId)
        # 当前没有月卡时购买月卡天数减1(普通月卡需特殊处理).
        if itemId == config.MONTH_CARD_KINDID and (item is None or item.isDied(int(time.time()))) and count > 1:
            count -= 1
        rewards = [{"name": itemId, "count": count}]
        # 首次购买奖励
        if gamedata.getGameAttrInt(self.userId, FISH_GAMEID, GameData.hasBoughtMonthCard) == 0:
            for reward in giftConf.get("firstBuyRewards", []):
                if reward["type"] == 3:  # 资产/道具
                    extraRwards.append({"name": reward["itemId"], "count": reward["count"]})
        # 购买立得
        for reward in giftConf.get("getAfterBuy", []):
            if reward["type"] == 3:  # 资产/道具
                extraRwards.append({"name": reward["itemId"], "count": reward["count"]})
        rewards.extend(extraRwards)
        util.addRewards(self.userId, rewards, "BI_NFISH_BUY_ITEM_GAIN", int(giftId), param01=int(giftId))
        gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.hasBoughtMonthCard, json.dumps(1))
        honor_system.checkMonthCardHonor(self.userId)
        return 0, extraRwards


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
        for giftId in self.giftListConf:
            giftConf = config.getGiftConf(self.clientId, giftId)
            if not giftConf:
                continue
            # 房间限制
            if len(giftConf["roomId"]) > 0 and bigRoomId not in giftConf["roomId"]:
                continue
            # vip限制
            if giftConf["vip"] > self.vipLevel:
                continue
            # 已经领取过的
            if giftConf["giftId"] in levelUpGiftInfo and (giftConf["giftId"] not in self.availableGift):
                continue
            # 已经领取过的，兼容老账号
            if giftConf["giftId"] in normalGiftInfo and (giftConf["giftId"] not in self.availableGift):
                continue
            available = 1 if giftConf["giftId"] in self.availableGift else 0  # 1可领取 0 不可领取
            # 可以领取的
            if available == 1:
                return giftConf
            # 未购买的
            if giftConf["giftId"] not in levelUpGiftInfo:
                if giftConf["minLevelLimit"] <= self.level <= giftConf["maxLevelLimit"]:
                    # 已过期
                    expireTime = giftConf.get("expireTime", -1)
                    if expireTime > 0 and giftExpireTS.get(str(giftId), int(time.time())) < int(time.time()):
                        continue
                    recommonGift = giftConf
                    if expireTime > 0 and str(giftId) not in giftExpireTS:
                        giftExpireTS[str(giftId)] = int(time.time()) + expireTime * 60
                        gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.giftsExpireTS, json.dumps(giftExpireTS))
                    break
        return recommonGift

    def getGiftInfo(self):
        """
        获取礼包信息
        """
        levelUpGift = []
        giftConf = self.getCurrentGiftConf()
        if giftConf:
            popup = 0
            popupGiftInfo = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.popupGift, [])
            # 达到指定等级需要主动弹出的升级礼包
            if giftConf["giftId"] in popupGiftInfo:
                popupGiftInfo.remove(giftConf["giftId"])
                gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.popupGift, json.dumps(popupGiftInfo))
                popup = 1
            available = 1 if giftConf["giftId"] in self.availableGift else 0
            levelUpGift.append(self.getGiftDetail(giftConf, available, popup))
        return levelUpGift

    def addGiftData(self, giftId):
        """
        使礼包变为可领取状态并添加礼包数据
        """
        code = 1
        levelUpGifts = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.levelUpGift, [])
        if giftId not in levelUpGifts:
            levelUpGifts.append(giftId)
            gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.levelUpGift, json.dumps(levelUpGifts))
            self.addToAvailableGift(giftId)
            code = 0
        return code


def doSendFishGift(userId, clientId):
    """
    发送礼包消息
    """
    doSendFishSeriesGift(userId, clientId)                                  # 系列礼包
    message = MsgPack()
    message.setCmd("fishGift")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    sailGift = SailGift(userId, clientId).getGiftInfo()                     # 启航礼包
    if sailGift:
        message.setResult("sailGift", sailGift)
    if not util.isVersionLimit(userId):                                     # 提审版本限制
        bankruptGift, bestIndex, tip = BankruptGift(userId, clientId).getGiftInfo()    # 破产礼包
        if bankruptGift:
            message.setResult("dailyGiftMode", util.getGiftAbcTestMode(userId))
            message.setResult("dailyGift", bankruptGift)                    # 破产礼包
            message.setResult("bestIndex", bestIndex)
            message.setResult("dailyGiftTxt", tip)                          # 提示信息
    alms = share_system.AlmsCoin(userId)                                    # 救济金分享
    gotTimes = alms.shareData[share_system.INDEX_FINISH_COUNT]
    # 今日领取救济金次数
    message.setResult("gotAlmsCoinTimes", gotTimes)
    enterFishPoolTimes = weakdata.getDayFishData(userId, WeakData.enterFishPoolTimes, 0)
    # 今日进入渔场次数
    message.setResult("enterFishPoolTimes", enterFishPoolTimes)
    giftTestMode = config.getPublic("giftTestMode", None)                   # b测试模式
    if giftTestMode is None:
        giftTestMode = "a"                                      # if userId % 2 == 0 else "b"
    # 显示钻石或元测试
    message.setResult("testMode", giftTestMode)
    router.sendToUser(message, userId)


def doSendFishSeriesGift(userId, clientId):
    """
    发送礼包合集消息（礼包ab测试之b模式）
    """
    # if not util.isVersionLimit(userId) and not util.isPurchaseLimit(userId) and util.isFinishAllNewbieTask(userId):
    #     showIndex, seriesGift = getSeriesGift(userId, clientId)
    # else:
    showIndex, seriesGift = -1, []
    message = MsgPack()
    message.setCmd("fishSeriesGift")                                    # 单独返回捕鱼系列礼包信息（当为b模式时才返回）
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
    for giftId in normalGiftIds:
        if giftId == 70212801:
            normalGiftIds.remove(giftId)
            normalGiftIds.remove(giftId + 1)                            # a模式下giftId为70212801何70212802的两个礼包不显示
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
            recommendGiftId = allSeriesGiftId[min(allSeriesGiftId.index(maxBoughtGiftId) + 1, len(allSeriesGiftId) - 1)]
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
    giftConf = getGiftConf(clientId, giftId)
    if not giftConf:
        ftlog.error("doBuyFishGift, userId =", userId, "giftId =", giftId, "buyType =", buyType, "itemId =", itemId)
        return
    lang = util.getLanguage(userId, clientId)
    buyType = buyType or giftConf.get("buyType")
    # 直充购买或者三方渠道支付
    if buyType == "direct" or config.isThirdBuyType(buyType):
        message = config.getMultiLangTextConf("ID_BUY_GIFT_RET_BY_DRIECT", lang=lang).format(giftConf["giftName"], giftConf["giftName"])
        GameMsg.sendPrivate(FISH_GAMEID, userId, 0, message)
    else:
        # 使用代购券购买
        if giftConf.get("otherBuyType", {}).get(buyType):
            price = giftConf.get("otherBuyType", {}).get(buyType)
            if buyType == BT_VOUCHER:
                _consume = [{"name": VOUCHER_KINDID, "count": abs(price)}]
                _, consumeCount, final = util.consumeItems(userId, _consume, "BI_NFISH_BUY_ITEM_CONSUME", 0,
                                                          param01=int(giftId))
                if abs(consumeCount) != price:
                    _sendBuyFishGiftRet(userId, clientId, giftId, 1)
                    return
                else:
                    vip_system.addUserVipExp(FISH_GAMEID, userId, abs(price) * 10, "BUY_PRODUCT",
                                             pokerconf.productIdToNumber(giftConf["productId"]),
                                             giftConf["productId"], rmbs=abs(price))
                    message = config.getMultiLangTextConf("ID_BUY_GIFT_RET_BY_VOUCHER", lang=lang).format(price, giftConf["giftName"], giftConf["giftName"])
                    GameMsg.sendPrivate(FISH_GAMEID, userId, 0, message)
            else:
                _sendBuyFishGiftRet(userId, clientId, giftId, 1)
                return
        # 使用钻石购买
        elif buyType == config.BT_DIAMOND:
            price = giftConf.get("discountPrice", 0)
            price, isSucc = store.getUseRebateItemPrice(userId, itemId, price, buyType, giftId, clientId)   # 满减券之后的钻石 满减券
            if price > 0:
                consumeCount = 0
                if isSucc:
                    store.autoConvertVoucherToDiamond(userId, price)                                        # 代购券
                    consumeCount, final = userchip.incrDiamond(userId, FISH_GAMEID, -abs(price), 0,
                                                               "BI_NFISH_BUY_ITEM_CONSUME", int(giftId),
                                                               util.getClientId(userId), param01=giftId)
                if not isSucc or abs(consumeCount) != price:
                    _sendBuyFishGiftRet(userId, clientId, giftId, 1)
                    return
    # 记录礼包购买次数.
    buyGiftTimes = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.buyGiftTimes, {})
    buyGiftTimes.setdefault(str(giftId), 0)
    buyGiftTimes[str(giftId)] += 1
    gamedata.setGameAttr(userId, FISH_GAMEID, GameData.buyGiftTimes, json.dumps(buyGiftTimes))
    # 使礼包变为可领取状态
    code, extraRwards = 1, None
    if giftConf["giftType"] == GiftType.NORMAL:                             # 普通礼包
        code = NormalGift(userId, clientId).addGiftData(int(giftId))
    elif giftConf["giftType"] == GiftType.BANKRUPT:                         # 破产礼包
        code = BankruptGift(userId, clientId).addGiftData(int(giftId))
        if code == 0:
            # 购买成功后更新破产礼包购买次数并存储礼包等级.
            bankruptGiftInfo = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.bankruptGiftInfo, [])
            if bankruptGiftInfo:
                if len(bankruptGiftInfo) == 2:
                    fishPool, grade = bankruptGiftInfo
                else:
                    fishPool, grade, _ = bankruptGiftInfo
                buyBankruptGift = weakdata.getDayFishData(userId, WeakData.buyBankruptGiftTimesPerPool, {})
                buyBankruptGift.setdefault(str(fishPool), {}).setdefault("count", 0)
                buyBankruptGift[str(fishPool)]["count"] += 1
                buyBankruptGift[str(fishPool)]["grade"] = grade
                weakdata.setDayFishData(userId, WeakData.buyBankruptGiftTimesPerPool, json.dumps(buyBankruptGift))
            if ftlog.is_debug():
                ftlog.debug("doBuyFishGift, userId =", userId, "giftId =", giftId, "bankruptGiftInfo =", bankruptGiftInfo)
        gamedata.delGameAttr(userId, FISH_GAMEID, GameData.bankruptGiftInfo)
    elif giftConf["giftType"] == GiftType.MONTHCARD:                        # 月卡|永久月卡礼包
        code, extraRwards = MonthCardGift(userId, clientId).addGiftData(int(giftId))
    elif giftConf["giftType"] == GiftType.LEVELUP:                          # 升级礼包
        code = LevelUpGift(userId, clientId).addGiftData(int(giftId))
    _sendBuyFishGiftRet(userId, clientId, giftId, code, extraRwards)
    # 购买礼包事件
    if code != 0:
        return
    from newfish.game import TGFish
    from newfish.entity.event import GiftBuyEvent
    event = GiftBuyEvent(userId, FISH_GAMEID, giftConf["productId"], buyType, giftId)
    TGFish.getEventBus().publishEvent(event)
    util.addProductBuyEvent(userId, giftConf["productId"], clientId)


def _sendBuyFishGiftRet(userId, clientId, giftId, code, rewards=None):
    """
    返回购买礼包结果
    """
    giftConf = getGiftConf(clientId, giftId)
    message = MsgPack()
    message.setCmd("buyFishGift")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    message.setResult("giftId", giftId)
    message.setResult("code", code)
    rewards = [] if rewards is None else rewards
    message.setResult("commonRewards", rewards)
    router.sendToUser(message, userId)
    if giftConf and giftConf["giftType"] == GiftType.MONTHCARD:
        doSendNewMonthCardGiftInfo(userId, clientId)
    else:
        doSendFishGift(userId, clientId)
    ftlog.info("buyGiftRet, userId =", userId, "clientId =", clientId, "giftId =", giftId, "code =", code)


def doGetFishGiftReward(userId, clientId, giftId):
    """
    领取礼包
    """
    availableGift = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.availableGift, [])
    code = 1
    chestId = 0
    commonRewards = []
    chestRewards = []
    giftConf = getGiftConf(clientId, giftId)
    if not giftConf:
        ftlog.error("doGetFishGiftReward, userId =", userId, "giftId =", giftId)
        return
    canGetRewards = False
    if giftConf["giftType"] == GiftType.MONTHCARD:
        userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
        itemId = giftConf["monthCard"]["name"]
        item = userBag.getItemByKindId(itemId)
        if item and not item.isDied(int(time.time())):
            if itemId == config.MONTH_CARD_KINDID:
                canGetRewards = weakdata.getDayFishData(userId, WeakData.getMonthCardGift, 0) == 0
            else:
                canGetRewards = weakdata.getDayFishData(userId, WeakData.getPermanentMonthCardGift, 0) == 0
    else:
        canGetRewards = giftId in availableGift
    if canGetRewards:
        eventId = "BI_NFISH_BUY_ITEM_GAIN"
        if giftConf.get("giftId") == 7001:
            eventId = "BI_NFISH_NEW_USER_REWARDS"
        for item in giftConf.get("items", []):
            if item["type"] == 1:     # 宝箱
                chestId = item["itemId"]
                rewards = chest_system.getChestRewards(userId, chestId)
                code = chest_system.deliveryChestRewards(userId, chestId, rewards, eventId)
                chestRewards.extend(rewards)
            elif item["type"] == 2:   # 等级
                _makeUserLevelUp(userId, item["count"])
                code = 0
            elif item["type"] == 3:   # 资产/道具
                rewards = [{"name": item["itemId"], "count": item["count"]}]
                code = util.addRewards(userId, rewards, eventId, int(giftId), param01=int(giftId))
                commonRewards.extend(rewards)
            elif item["type"] == 5:   # 皮肤炮皮肤
                skinId = item["itemId"]
                ret = gun_system.addEquipGunSkinSkin(userId, skinId, clientId)
                if ret:
                    code = 0
                    rewards = [{"name": item["itemId"], "count": item["count"], "type": item["type"]}]
                    commonRewards.extend(rewards)
            elif item["type"] == 6:     # 直升炮台
                upToLevel = item["count"]
                success = gun_system.upgradeGun(userId, False, MULTIPLE_MODE, byGift=True, upToLevel=upToLevel)
                if success:
                    code = 0

    message = MsgPack()
    if giftConf["giftType"] == GiftType.MONTHCARD:
        message.setCmd("monthGiftGet")
    else:
        message.setCmd("fishGiftReward")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    message.setResult("giftId", giftId)
    message.setResult("chestId", chestId)
    if code == 0 and (commonRewards or chestRewards):
        if giftConf["giftType"] == GiftType.MONTHCARD:
            itemId = giftConf["monthCard"]["name"]
            if itemId == config.MONTH_CARD_KINDID:
                weakdata.incrDayFishData(userId, WeakData.getMonthCardGift, 1)
            else:
                weakdata.incrDayFishData(userId, WeakData.getPermanentMonthCardGift, 1)
        else:
            availableGift.remove(giftId)
            gamedata.setGameAttr(userId, FISH_GAMEID, GameData.availableGift, json.dumps(availableGift))
        message.setResult("commonRewards", commonRewards)
        message.setResult("chestRewards", chestRewards)
    message.setResult("code", code)
    router.sendToUser(message, userId)

    # 如果领取的是普通类型礼包需要记录一下
    if code == 0 and giftConf["giftType"] == GiftType.NORMAL:
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.alreadyTakenNormalGift, 1)
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.buyGiftTimestamp, json.dumps(int(time.time())))

    productId = giftConf.get("productId", "")
    isIn, roomId, tableId, seatId = util.isInFishTable(userId)
    if isIn:
        mo = MsgPack()
        mo.setCmd("table_call")
        mo.setParam("action", "take_gift_reward")
        mo.setParam("gameId", FISH_GAMEID)
        mo.setParam("clientId", util.getClientId(userId))
        mo.setParam("userId", userId)
        mo.setParam("roomId", roomId)
        mo.setParam("tableId", tableId)
        mo.setParam("seatId", seatId)
        mo.setParam("productId", productId)
        router.sendTableServer(mo, roomId)


def _makeUserLevelUp(userId, level):
    """
    礼包奖励为提升至指定等级
    """
    originLevel = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.level)
    if originLevel >= level:
        return
    lastLevel = level - 1
    lastLevelConf = config.getUlevel(lastLevel)
    ftlog.debug("_userLevelUp->", lastLevelConf)
    gamedata.setGameAttrs(userId, FISH_GAMEID, [GameData.level, GameData.exp, GameData.gunLevel], [level, lastLevelConf.get("totalExp", 0) + 1, 2100 + level])


def getLimitTimeGift(userId, clientId, popup=0):
    """
    获取限时礼包配置（已废弃）
    """
    pass
    # limitTimeGiftData = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.limitTimeGift, {})
    # availableGift = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.availableGift, [])
    # limitTimeGift = {}
    # if limitTimeGiftData and util.isFinishAllNewbieTask(userId):
    #     lastGiftId = limitTimeGiftData["lastGiftId"]
    #     lastActivate = limitTimeGiftData["lastActivate"]
    #     giftConf = config.getGiftConf(clientId, lastGiftId)
    #     if giftConf["giftId"] in availableGift or \
    #        (int(time.time()) - lastActivate < giftConf["lifetime"] and limitTimeGiftData.get("complete", 0) == 0):
    #         available = 1 if giftConf["giftId"] in availableGift else 0
    #         endTime = lastActivate + giftConf["lifetime"]
    #         limitTimeGift = getGiftDetail(giftConf, available, popup, endTime)
    # return limitTimeGift


def getWxFishGift(userId):
    """
    获取给微信公众号充值页展示的礼包
    """
    clientId = util.getClientId(userId)
    # 旧版礼包
    # normalGift = NormalGift(userId, clientId).getGiftInfo()
    # monthCardGift = []
    # if normalGift and normalGift["available"] != 0:
    #     normalGift = {}
    # 新版礼包
    # _, seriesGift = getSeriesGift(userId, clientId)
    # if seriesGift:
    #     seriesGift = list(filter(lambda x: x["available"] == 0, seriesGift))
    levelGift = doSendLevelGift(userId, clientId)
    # 破产礼包
    bankruptGift, _, _ = BankruptGift(userId, clientId).getGiftInfo()
    if bankruptGift:
        bankruptGift = list(filter(lambda x: x["available"] == 0, bankruptGift))
    # 月卡
    # if monthCardGift:
    #     monthCardGift = list(filter(lambda x: x["available"] == 0, monthCardGift))
    monthGiftInfo = MonthCardGift(userId, clientId).getGiftInfo()
    monthCardGift = [gift[0] for gift in monthGiftInfo]
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    itemPermanent = userBag.getItemByKindId(config.PERMANENT_MONTH_CARD_KINDID)
    if itemPermanent:
        monthCardGift = None
    return levelGift, bankruptGift, monthCardGift


def doSendNewMonthCardGiftInfo(userId, clientId, popup=0):
    """
    获取月卡礼包信息
    """
    message = MsgPack()
    message.setCmd("monthGiftInfo")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    monthGiftData = []
    monthCardGift = {}
    itemId = 0
    state = 0
    remain = 0
    if not util.isVersionLimit(userId) and not util.isPurchaseLimit(userId) and util.isFinishAllNewbieTask(userId):
        giftInfo = MonthCardGift(userId, clientId).getGiftInfo()
        for _info in giftInfo:
            monthCardGift, itemId, state = _info
            userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
            item = userBag.getItemByKindId(itemId)
            remain = 0
            enableBuy = 0 if userBag.getItemByKindId(config.PERMANENT_MONTH_CARD_KINDID) else 1
            if itemId == config.MONTH_CARD_KINDID and item and not item.isDied(int(time.time())):
                remain = max(0, item.expiresTime - int(time.time()))
            monthGiftData.append({
                "monthCardGift": monthCardGift,
                "item": itemId,
                "state": state,
                "remainTime": remain,
                "hasBought": gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.hasBoughtMonthCard),
                "enableBuy": enableBuy
            })
    message.setResult("monthGiftData", monthGiftData)
    # 以下字段兼容使用
    message.setResult("monthCardGift", monthCardGift)
    message.setResult("item", itemId)
    message.setResult("state", state)
    message.setResult("remainTime", remain)
    message.setResult("hasBought", gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.hasBoughtMonthCard))
    router.sendToUser(message, userId)


def doRefreshFishGift(userId):
    """
    让客户端重新刷新礼包数据
    """
    ftlog.debug("doRefreshFishGift", userId)
    message = MsgPack()
    message.setCmd("refreshFishGift")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    router.sendToUser(message, userId)


def getGiftConf(clientId, giftId):
    """
    获取礼包配置
    """
    giftConf = config.getGiftConf(clientId, giftId)
    if not giftConf:
        giftConf = config.getGiftAbcTestConf(clientId).get("gift", {}).get(str(giftId))
    return giftConf


def _triggerChargeNotifyEvent(event):
    """
    直充购买商品成功事件
    """
    ftlog.info("gift_system._triggerChargeNotifyEvent->",
               "userId =", event.userId,
               "gameId =", event.gameId,
               "rmbs =", event.rmbs,
               "productId =", event.productId,
               "clientId =", event.clientId)
    userId = event.userId
    productId = event.productId
    allGiftConf = config.getGiftConf(event.clientId)
    abcGiftConf = config.getGiftAbcTestConf(event.clientId).get("gift", {})
    for giftConf in allGiftConf.values() + abcGiftConf.values():
        if giftConf["productId"] == productId:
            doBuyFishGift(userId, event.clientId, giftConf["giftId"])
            break


def _triggerCheckLimitTimeGiftEvent(event):
    """
    是否弹出限时礼包（已废弃）
    """
    ftlog.debug("_triggerCheckLimitTimeGiftEvent->", event.userId, event.level,
                event.chip, event.fishPool, event.clientId)
    # giftConf = config.getLimitTimeGiftConf(event.clientId, event.fishPool)
    # if giftConf and giftConf["minLevelLimit"] <= event.level <= giftConf["maxLevelLimit"] and \
    #    event.chip <= giftConf["coinLimit"]:
    #     limitTimeGift = gamedata.getGameAttrJson(event.userId, FISH_GAMEID, GameData.limitTimeGift, {})
    #     ftlog.debug("_triggerCheckLimitTimeGiftEvent->limitTimeGift =", limitTimeGift)
    #     currTime = int(time.time())
    #     if not limitTimeGift or (limitTimeGift and currTime - limitTimeGift["lastActivate"] >= 24 * 3600 and
    #        currTime - limitTimeGift.get(str(event.fishPool), 0) >= 48 * 3600):
    #         limitTimeGift["lastGiftId"] = giftConf["giftId"]
    #         limitTimeGift["lastActivate"] = currTime
    #         limitTimeGift["complete"] = 0
    #         limitTimeGift[str(event.fishPool)] = currTime
    #         gamedata.setGameAttr(event.userId, FISH_GAMEID, GameData.limitTimeGift, json.dumps(limitTimeGift))
    #         doSendFishGift(event.userId, event.clientId)


def _triggerUserLoginEvent(event):
    """
    用户登录事件
    """
    # 每次登录后重置
    gamedata.setGameAttr(event.userId, FISH_GAMEID, GameData.alreadyTakenNormalGift, 0)
    gamedata.delGameAttr(event.userId, FISH_GAMEID, GameData.futureExpiredGift)


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