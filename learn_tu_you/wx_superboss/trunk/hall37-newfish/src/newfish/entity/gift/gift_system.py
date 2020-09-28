# -*- coding=utf-8 -*-
"""
Created by lichen on 16/12/13.
"""

import time
import json

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack

from poker.protocol import router
from poker.entity.dao import gamedata, userchip
from hall.entity import hallitem, hallvip
from newfish.entity import config, util, weakdata, share_system, store
from newfish.entity.redis_keys import GameData, WeakData
from newfish.entity.config import FISH_GAMEID, MULTIPLE_MODE
from newfish.entity.chest import chest_system
from newfish.entity.gun import gun_system
from newfish.entity.honor import honor_system


SECONDOFDAY = 86400
DAYOFMONTH = 30


class GiftType:
    BANKRUPT = 3    # 破产礼包
    MONTHCARD = 4   # 月卡礼包


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
        gift["giftId"] = giftConf["giftId"]                                 # 礼包Id
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
        gift["items"] = giftConf["items"]                                   # 购买的奖励
        # 首次购买奖励
        gift["firstBuyRewards"] = giftConf.get("firstBuyRewards", [])       # 首次购买奖励
        # 购买立得
        gift["getAfterBuy"] = giftConf.get("getAfterBuy", [])               # 金币
        return gift


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
        if not isIn:
            return [], ""
        mode = util.getGiftDTestMode(self.userId)
        fishPool = util.getFishPoolByBigRoomId(util.getBigRoomId(roomId)[0])
        grade, nextGrade = self._getGrade(fishPool)                             # 获取礼包档位
        giftAbcTestConf = config.getGiftAbcTestConf(self.clientId)
        giftListConf = giftAbcTestConf.get("data", {}).get(str(fishPool), {}).get(grade, {}).get("giftList", {}).get(mode, [])
        nextGiftListConf = giftAbcTestConf.get("data", {}).get(str(fishPool), {}).get(nextGrade, {}).get("giftList", {}).get(mode, [])
        buyTimes = self._getBuyTimes(fishPool)
        recommonGift = []
        # 当前房间可以使用的破产礼包列表.
        for idx, giftGroup in enumerate(zip(giftListConf, nextGiftListConf)):
            if not set(self.availableGift) & set(giftGroup):                    # 优先展示可领取的礼包
                continue
            if buyTimes - 1 != idx:
                continue
            for giftId in giftGroup:
                giftConf = giftAbcTestConf.get("gift", {}).get(str(giftId))
                if not giftConf:
                    continue
                recommonGift.append(giftConf)
        if ftlog.is_debug():
            ftlog.debug("BankruptGift_getCurrentGiftConf", fishPool, giftListConf, nextGiftListConf, grade, nextGrade, recommonGift)
        # 没有可领取礼包则按照已购买次数显示礼包.
        if not recommonGift:
            if 0 <= buyTimes < len(giftListConf):
                listConf2 = giftAbcTestConf.get("data", {}).get(str(fishPool), {}).get(nextGrade, {}).get("giftList", {}).get(mode, [])
                giftId1, giftId2 = giftListConf[buyTimes], listConf2[buyTimes]
                recommonGift = [giftAbcTestConf.get("gift", {}).get(str(giftId1)), giftAbcTestConf.get("gift", {}).get(str(giftId2))]
        lang = util.getLanguage(self.userId, self.clientId)
        remainTimes = max(0, len(giftListConf) - buyTimes)
        if recommonGift:
            gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.bankruptGiftInfo, json.dumps([fishPool, grade, nextGrade]))
            tip = config.getMultiLangTextConf("ID_BANKRUPT_GIFT_TIP", lang=lang).format(remainTimes)
        else:
            tip = ""
        return recommonGift, tip

    def getGiftInfo(self):
        """
        获取礼包信息
        """
        dailyGift = []
        giftConf, tip = self.getCurrentGiftConf()
        for _giftConf in giftConf:
            available = 1 if _giftConf["giftId"] in self.availableGift else 0
            dailyGift.append(self.getGiftDetail(_giftConf, available))
        return dailyGift, tip

    def addGiftData(self, giftId):
        """
        使礼包变为可领取状态并添加礼包数据
        """
        code = 1
        mode = util.getGiftDTestMode(self.userId)
        giftConf = config.getGiftAbcTestConf(self.clientId)
        bankruptGiftInfo = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.bankruptGiftInfo)
        isValid = False
        if bankruptGiftInfo:
            fishPool, grade, nextGrade = bankruptGiftInfo
            buyTimes = self._getBuyTimes(fishPool)
            # 检查礼包是否存在以及购买次数.
            giftAbcTestConf = giftConf.get("data", {})
            giftListConf = giftAbcTestConf.get(str(fishPool), {}).get(grade, {}).get("giftList", {}).get(mode, [])
            if 0 <= buyTimes < len(giftListConf):
                if str(giftId) == str(giftListConf[buyTimes]):
                    isValid = True
                else:
                    ListConf2 = giftAbcTestConf.get(str(fishPool), {}).get(nextGrade, {}).get("giftList", {}).get(mode, [])
                    if str(giftId) == str(ListConf2[buyTimes]):
                        # 后续会用这个数据做上一次购买的档位记录，所以在这里进行修改
                        bankruptGiftInfo[1] = bankruptGiftInfo[2]
                        gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.bankruptGiftInfo, json.dumps(bankruptGiftInfo))
                        isValid = True
        if isValid:
            self.addToAvailableGift(giftId)
            code = 0
        return code

    def _getGrade(self, fishPool):
        """
        获取abc测试中的礼包档位
        """
        buyBankruptGift = weakdata.getDayFishData(self.userId, WeakData.buyBankruptGiftTimesPerPool, {})
        grade = buyBankruptGift.get(str(fishPool), {}).get("grade")
        # 根据当前的消费能力计算礼包档位.
        if str(fishPool) not in buyBankruptGift:
            grade, nextGrade = "low", "mid"
        else:
            if grade == "mid" or grade == "high":
                grade, nextGrade = "mid", "high"
            else:
                grade, nextGrade = "low", "mid"
        return grade, nextGrade

    def _getBuyTimes(self, fishPool):
        """
        获取d测试中礼包购买次数
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
                    available = 0           # 0：未购买月卡 1：未领取 2：已领取
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
                if reward["type"] == 3:                     # 资产/道具
                    extraRwards.append({"name": reward["itemId"], "count": reward["count"]})
        # 购买立得
        for reward in giftConf.get("getAfterBuy", []):
            if reward["type"] == 3:                         # 资产/道具
                extraRwards.append({"name": reward["itemId"], "count": reward["count"]})
        rewards.extend(extraRwards)
        util.addRewards(self.userId, rewards, "BI_NFISH_BUY_ITEM_GAIN", int(giftId), param01=int(giftId))
        gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.hasBoughtMonthCard, json.dumps(1))
        honor_system.checkMonthCardHonor(self.userId)
        return 0, extraRwards


################################################################################################################
def doSendFishGift(userId, clientId):
    """
    发送礼包消息
    """
    message = MsgPack()
    message.setCmd("fishGift")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    if not util.isVersionLimit(userId):                                     # 提审版本限制
        bankruptGift, tip = BankruptGift(userId, clientId).getGiftInfo()    # 破产礼包
        if bankruptGift:
            message.setResult("dailyGiftMode", util.getGiftDTestMode(userId))
            message.setResult("dailyGift", bankruptGift)                    # 破产礼包
            message.setResult("dailyGiftTxt", tip)                          # 提示信息
    alms = share_system.AlmsCoin(userId)                                    # 救济金分享
    gotTimes = alms.shareData[share_system.INDEX_FINISH_COUNT]
    # 今日领取救济金次数
    message.setResult("gotAlmsCoinTimes", gotTimes)
    enterFishPoolTimes = weakdata.getDayFishData(userId, WeakData.enterFishPoolTimes, 0)
    # 今日进入渔场次数
    message.setResult("enterFishPoolTimes", enterFishPoolTimes)
    giftTestMode = config.getPublic("giftTestMode", None)                   # b测试模式 b显示钻石 a显示元
    if giftTestMode is None:
        giftTestMode = "a"
    message.setResult("testMode", giftTestMode)                             # 显示钻石或元测试
    router.sendToUser(message, userId)


def doBuyFishGift(userId, clientId, giftId, buyType=None, itemId=0):
    """
    购买礼包
    """
    if ftlog.is_debug():
        ftlog.debug("doBuyFishGift===>", userId, clientId, giftId, buyType, itemId)
    giftConf = getGiftConf(clientId, giftId)
    if not giftConf:
        return
    buyType = buyType or giftConf.get("buyType")
    # 使用钻石购买
    if buyType == config.BT_DIAMOND:
        price = giftConf.get("discountPrice", 0)
        price, isSucc = store.getUseRebateItemPrice(userId, itemId, price, buyType, giftId, clientId)   # 满减券之后的钻石 满减券
        if price > 0:
            consumeCount = 0
            if isSucc:
                store.autoConvertVoucherToDiamond(userId, price)                                        # 代购券
                consumeCount, final = userchip.incrDiamond(userId, FISH_GAMEID, -abs(price), 0, "BI_NFISH_BUY_ITEM_CONSUME", int(giftId), util.getClientId(userId), param01=giftId)
            if not isSucc or abs(consumeCount) != price:
                _sendBuyFishGiftRet(userId, clientId, giftId, 1)                                        # 钻石购买结果
                return
    # 使礼包变为可领取状态
    code, extraRwards = 1, None
    if giftConf["giftType"] == GiftType.BANKRUPT:                                                       # 破产礼包
        code = BankruptGift(userId, clientId).addGiftData(int(giftId))
        if code == 0:
            # 购买成功后更新破产礼包购买次数并存储礼包等级.
            bankruptGiftInfo = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.bankruptGiftInfo, [])
            if bankruptGiftInfo:
                fishPool, grade = bankruptGiftInfo[:2]
                buyBankruptGift = weakdata.getDayFishData(userId, WeakData.buyBankruptGiftTimesPerPool, {})
                buyBankruptGift.setdefault(str(fishPool), {}).setdefault("count", 0)
                buyBankruptGift[str(fishPool)]["count"] += 1                                            # 购买次数
                buyBankruptGift[str(fishPool)]["grade"] = grade                                         # 购买等级
                weakdata.setDayFishData(userId, WeakData.buyBankruptGiftTimesPerPool, json.dumps(buyBankruptGift))
        gamedata.delGameAttr(userId, FISH_GAMEID, GameData.bankruptGiftInfo)
    elif giftConf["giftType"] == GiftType.MONTHCARD:                                                    # 月卡|永久月卡礼包
        code, extraRwards = MonthCardGift(userId, clientId).addGiftData(int(giftId))
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
        doSendNewMonthCardGiftInfo(userId, clientId)                        # 刷新月卡礼包
    else:
        doSendFishGift(userId, clientId)                                    # 刷新系列礼包


def doGetFishGiftReward(userId, clientId, giftId):
    """
    领取礼包
    """
    giftConf = getGiftConf(clientId, giftId)
    if not giftConf:
        return
    code = 1
    chestId = 0
    commonRewards = []
    chestRewards = []
    availableGift = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.availableGift, [])
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

    if not canGetRewards:
        return

    eventId = "BI_NFISH_BUY_ITEM_GAIN"
    for item in giftConf.get("items", []):
        if item["type"] == 1:                       # 宝箱
            chestId = item["itemId"]
            rewards = chest_system.getChestRewards(userId, chestId)
            code = chest_system.deliveryChestRewards(userId, chestId, rewards, eventId)
            chestRewards.extend(rewards)
        elif item["type"] == 2:                     # 等级
            _makeUserLevelUp(userId, item["count"])
            code = 0
        elif item["type"] == 3:                     # 资产/道具
            rewards = [{"name": item["itemId"], "count": item["count"]}]
            code = util.addRewards(userId, rewards, eventId, int(giftId), param01=int(giftId))
            commonRewards.extend(rewards)
        elif item["type"] == 5:                     # 皮肤炮皮肤
            skinId = item["itemId"]
            ret = gun_system.addEquipGunSkinSkin(userId, skinId, clientId)
            if ret:
                code = 0
                rewards = [{"name": item["itemId"], "count": item["count"], "type": item["type"]}]
                commonRewards.extend(rewards)
        elif item["type"] == 6:                     # 直升炮台
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
    gamedata.setGameAttrs(userId, FISH_GAMEID, [GameData.level, GameData.exp, GameData.gunLevel], [level, lastLevelConf.get("totalExp", 0) + 1, 2100 + level])


def getWxFishGift(userId):
    """
    获取给微信公众号充值页展示的礼包
    """
    return [], [], []
    # clientId = util.getClientId(userId)
    # levelGift = doSendLevelGift(userId, clientId)
    # # 破产礼包
    # bankruptGift,  _ = BankruptGift(userId, clientId).getGiftInfo()
    # if bankruptGift:
    #     bankruptGift = list(filter(lambda x: x["available"] == 0, bankruptGift))
    # monthGiftInfo = MonthCardGift(userId, clientId).getGiftInfo()
    # monthCardGift = [gift[0] for gift in monthGiftInfo]
    # userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    # itemPermanent = userBag.getItemByKindId(config.PERMANENT_MONTH_CARD_KINDID)
    # if itemPermanent:
    #     monthCardGift = None
    # return levelGift, bankruptGift, monthCardGift


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
    if not util.isVersionLimit(userId) and not util.isPurchaseLimit(userId):    # and util.isFinishAllNewbieTask(userId)
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
                "state": state,                                         # 状态
                "remainTime": remain,                                   # 剩余时间
                "hasBought": gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.hasBoughtMonthCard),
                "enableBuy": enableBuy                                  # 能否买永久月卡
            })
    message.setResult("monthGiftData", monthGiftData)
    # 以下字段兼容使用
    message.setResult("monthCardGift", monthCardGift)
    message.setResult("item", itemId)
    message.setResult("state", state)
    message.setResult("remainTime", remain)
    message.setResult("hasBought", gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.hasBoughtMonthCard))
    router.sendToUser(message, userId)


def getGiftConf(clientId, giftId):
    """
    获取礼包配置
    """
    giftConf = config.getGiftConf(clientId, giftId)                                         # 获取购买月卡|永久月卡
    if not giftConf:
        giftConf = config.getGiftAbcTestConf(clientId).get("gift", {}).get(str(giftId))     # 破产礼包
    return giftConf


_inited = False


def initialize():
    ftlog.debug("newfish gift_system initialize begin")
    global _inited
    if not _inited:
        _inited = True
    ftlog.debug("newfish gift_system initialize end")
