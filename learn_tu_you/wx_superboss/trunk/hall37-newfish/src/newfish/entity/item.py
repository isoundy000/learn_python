# -*- coding=utf-8 -*-
"""
Created by lichen on 17/2/8.

原则上每个商品购买对应一个BuyAction，每个BuyAction对应一个BaseProduct，
但是HotStoreBuyAction中的商品购买根据pt类型对应不用的BaseProduct!
"""

import time
import json
from operator import itemgetter
from distutils.version import StrictVersion

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
import poker.util.timestamp as pktimestamp
from poker.protocol import router
from poker.entity.dao import userchip, gamedata, daobase
from poker.entity.configure import pokerconf
from hall.entity import hallitem, hallvip, hallexchange, datachangenotify
from hall.entity.hallconf import HALL_GAMEID
from hall.servers.util.item_handler import ItemHelper
from newfish.entity import config, weakdata, util, module_tip, vip_system, \
    drop_system, store, mail_system
from newfish.entity.config import FISH_GAMEID, REDPACKET_KINDID, WX_APPID, \
    PEARL_KINDID, VOUCHER_KINDID, RUBY_KINDID, OCEANSTAR_KINDID
from newfish.entity.redis_keys import GameData, MixData, WeakData, UserData
from newfish.entity.chest import chest_system
from newfish.servers.util.rpc import user_rpc
from newfish.entity.event import StoreBuyEvent
from newfish.entity.msg import GameMsg
from newfish.entity.fishactivity.fish_activity_system import VIP_ITEMS
from newfish.entity.skill import skill_system
from newfish.entity.fishactivity import super_egg_activity, competition_activity, pass_card_activity
from newfish.entity.level_funds import doBuyLevelFunds
from newfish.entity.gift.level_gift import doBuyLevelGift
from newfish.entity.gun import gun_system
from poker.entity.biz import bireport


class BuyResultState:
    """
    购买结果状态
    """
    BRS_SUCC = 0                            # 成功购买
    BRS_COIN_NOTENOUGH = 1                  # 金币不足
    BRS_PEARL_NOTENOUGH = 2                 # 珍珠不足
    BRS_DIAMOND_NOTENOUGH = 3               # 钻石不足
    BRS_COUPON_NOTENOUGH = 4                # 奖券不足
    BRS_NEWBIE_LIMIT = 5                    # 新手任务限制
    BRS_VIP_LIMIT = 6                       # vip等级限制
    BRS_DAILY_USER_BUY_COUNT_LIMIT = 7      # 每日玩家购买次数限制
    BRS_FAILED = 8                          # 购买失败
    BRS_VOUCHER_NOTENOUGH = 9               # 代购券不足
    BRS_RUBY_NOTENOUGH = 10                 # 红宝石不足
    BRS_TOTAL_BUY_COUNT_LIMIT = 11          # 总购买次数限制
    BRS_DAILY_SERVER_BUY_COUNT_LIMIT = 12   # 每日全服购买次数限制
    BRS_USER_BUY_COUNT_LIMIT = 13           # 购买次数限制
    BRS_UNLOCK = 14                         # 需要解锁
    BRS_OCEANSTAR_NOTENOUGH = 15            # 海洋之星不足
    BRS_VIP_DAILY_USER_BUY_COUNT_LIMIT = 16  # vip每日玩家购买次数限制


class BuyAction(object):
    """
    购买动作基类
    """
    def __init__(self, userId, clientId, actionType, productId, count, buyType=None, rebateItemId=0):
        self.userId = userId
        self.clientId = clientId
        self.productId = productId
        self.buyCount = count
        self.actionType = actionType                                                    # 商城
        self.code = BuyResultState.BRS_SUCC
        self.ret = {}
        self.info = u""
        self.storeConf = None
        self.product = None
        self.name = None
        self.itemId = None
        self.itemType = None
        self.itemCount = None
        self.buyType = buyType
        self.buyTypeStr = None
        self.price = 0
        self.vipLimit = 0
        self.guideLimit = 0
        self.rebateItemId = rebateItemId
        self.userVip = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
        self.lang = util.getLanguage(userId, clientId)
        self.tabName = store.storeTabConfName.get(self.actionType)
        self._setConf()
        self.dayRefreshTime = "00:00"                                                   # 每日数据刷新时间点.
        self.curTime = int(time.time())
        self.allInfo = {}
        self.vipDailyCountLimit = []
        self._initData()

    def _setConf(self):
        """
        设置商品配置
        """
        if self.actionType in [store.StoreTabType.STT_HOT, store.StoreTabType.STT_COIN, store.StoreTabType.STT_DIAMOND,
                               store.StoreTabType.STT_ITEM, store.StoreTabType.STT_CHEST, store.StoreTabType.STT_COUPON]:
            self.storeConf = config.getStoreConf(self.clientId).get(self.tabName).get("items")
        else:
            self.storeConf = config.getStoreConf(self.clientId).get(self.tabName)

    def _initData(self):
        """
        初始化商品信息数据
        """
        self.product = self.storeConf.get(str(self.productId), {})                      # 商城的商品
        self.itemId = self.product.get("itemId", 0)                                     # 道具Id
        self.itemType = self.product.get("extendData", {}).get("itemType", 0)
        if self.buyType not in self.product.get("otherBuyType", {}):                    # 购买类型
            self.buyType = self.product.get("buyType", None)
        self.vipLimit = self.product.get("vip", 0) or self.product.get("limitCond", {}).get("vipLimit", 0)
        self.guideLimit = self.product.get("guideLimit", 0) or self.product.get("limitCond", {}).get("guideLimit", 0)
        self.vipDailyCountLimit = self.product.get("limitCond", {}).get("vipDailyCountLimit", [])
        self.dayBuyNum = self.product.get("limitCond", {}).get("userDailyCountLimit", 0)
        self.thirdBuyType = config.isThirdBuyType(self.buyType)
        self.buyTypeStr = config.getBuyTypeConf(self.buyType)
        self.productObj = store.CreateProduct(None, self.actionType, self.productId, self.product, self.userId, self.clientId)      # 创建商品
        if self.productObj:
            self.name = self.productObj.getName()
            self.itemCount = self.productObj.getItemCount()
            self.price = self.productObj.getPrice(self.buyType)
        else:
            self.name = self.product.get("name", "")
            self.itemCount = self.product.get("count", 0)
        if ftlog.is_debug():
            ftlog.debug("BuyAction->tabName", self.tabName, "userId =", self.userId, "buyType =", self.buyType,
                        "price =", self.price, "name =", self.name, "itemId =", self.itemId, "itemCount =", self.itemCount)

    def _checkCondition(self):
        """
        检查是否满足购买条件
        """
        if self.price <= 0 or not self.product or not self.buyType:
            self.code = BuyResultState.BRS_FAILED
        elif self.guideLimit and not util.isFinishAllNewbieTask(self.userId):
            self.code = BuyResultState.BRS_NEWBIE_LIMIT
        elif self.userVip < self.vipLimit:
            self.code = BuyResultState.BRS_VIP_LIMIT

    def _checkServerCount(self):
        """
        检查商品服务器数量限制,此检测会尝试购买次数,所以需要在检测完其他条件后再检测！！！
        """
        if ftlog.is_debug():
            ftlog.debug("checkServerCount", self.tabName, "userId =", self.userId, "buyType =", self.buyType,
                        "price =", self.price, "name =", self.name, "itemId =", self.itemId, "itemCount =", self.itemCount)
        if self.code != BuyResultState.BRS_SUCC:
            return
        if self.actionType == store.StoreTabType.STT_COUPON:            # 奖券
            serverBuyCount = self.product.get("limitCond", {}).get("serverDailyCountLimit", -1)
            key = MixData.buyProductServerCount % FISH_GAMEID
        else:
            serverBuyCount = self.product.get("limitCond", {}).get("hotServerDailyCountLimit", -1)
            key = MixData.buyHotProductServerCount % FISH_GAMEID
        if serverBuyCount != -1:
            serverPurchaseNum = daobase.executeMixCmd("HGET", key, self.productId) or 0
            if serverBuyCount <= serverPurchaseNum:
                self.code = BuyResultState.BRS_DAILY_SERVER_BUY_COUNT_LIMIT
            else:
                serverPurchaseNum = daobase.executeMixCmd("HINCRBY", key, self.productId, 1)
                if serverBuyCount < serverPurchaseNum:
                    self.code = BuyResultState.BRS_DAILY_SERVER_BUY_COUNT_LIMIT
            if self.code == BuyResultState.BRS_DAILY_SERVER_BUY_COUNT_LIMIT:
                store.getStoreTabsFish(self.userId, self.clientId, self.actionType)             # 刷新捕鱼商店

    def _checkUserCount(self):
        """
        检查商品每日购买数量限制
        """
        if self.code != BuyResultState.BRS_SUCC:
            return
        # 检测是否有每日购买限制.
        if self.dayBuyNum <= 0 and len(self.vipDailyCountLimit) > self.userVip and self.vipDailyCountLimit[self.userVip] <= 0:
            return
        _key = UserData.buyProductCount % (FISH_GAMEID, self.userId)
        _subKey = self._getDayCountSubKey()
        dayBuyCount = daobase.executeUserCmd(self.userId, "HGET", _key, str(_subKey))
        dayBuyCount = json.loads(dayBuyCount) if dayBuyCount else {}
        dayPurchaseNum = dayBuyCount.get(self.productId, 0)
        if 0 < self.dayBuyNum < (dayPurchaseNum + self.buyCount):                               # 已经购买 + 要购买
            self.code = BuyResultState.BRS_DAILY_USER_BUY_COUNT_LIMIT
        if len(self.vipDailyCountLimit) > self.userVip and 0 < self.vipDailyCountLimit[self.userVip] < (dayPurchaseNum + self.buyCount):    # vip每日购买次数
            self.code = BuyResultState.BRS_VIP_DAILY_USER_BUY_COUNT_LIMIT
        if self.code in [BuyResultState.BRS_DAILY_USER_BUY_COUNT_LIMIT, BuyResultState.BRS_VIP_DAILY_USER_BUY_COUNT_LIMIT]:
            store.getStoreTabsFish(self.userId, self.clientId, self.actionType)

    def _getDayCountSubKey(self):
        """
        获取每日购买次数的subKey
        """
        curTime = int(time.time())
        dayStartTS = util.getDayStartTimestamp(curTime)
        refreshTS = dayStartTS + util.timeStrToInt(self.dayRefreshTime)
        if curTime < refreshTS:
            keyTS = dayStartTS
        else:
            keyTS = dayStartTS + 86400
        return keyTS

    def _increaseDayBuyCount(self):
        """
        更新每日购买数据存档
        """
        # 检测是否有每日购买限制.
        if self.dayBuyNum <= 0 and len(self.vipDailyCountLimit) > self.userVip and self.vipDailyCountLimit[self.userVip] <= 0:
            return
        dayStartTS = util.getDayStartTimestamp(self.curTime)
        _key = UserData.buyProductCount % (FISH_GAMEID, self.userId)
        # 清理过期keys
        datas = daobase.executeUserCmd(self.userId, "HGETALL", _key)
        if datas:
            for ts in datas[0::2]:
                if int(ts) < dayStartTS - 2 * 86400:
                    daobase.executeUserCmd(self.userId, "HDEL", _key, ts)
        _subKey = self._getDayCountSubKey()
        dayBuyCount = daobase.executeUserCmd(self.userId, "HGET", _key, str(_subKey))
        dayBuyCount = json.loads(dayBuyCount) if dayBuyCount else {}
        dayBuyCount[self.productId] = dayBuyCount.setdefault(self.productId, 0) + self.buyCount
        daobase.executeUserCmd(self.userId, "HSET", _key, str(_subKey), json.dumps(dayBuyCount))

    def _refreshHotStoreShop(self):
        """
        刷新热卖商店
        """
        hotStoreConf = config.getStoreConf(self.clientId).get("hotStore", {}).get("items")
        if self.productId in hotStoreConf:
            store.getStoreTabsFish(self.userId, self.clientId, store.StoreTabType.STT_HOT)

    def _pay(self):
        """
        支付
        """
        if self.thirdBuyType:
            return
        if self.buyType != "direct":
            consumeCount, final = 0, 0
            gameId = FISH_GAMEID
            itemKind = hallitem.itemSystem.findItemKind(self.itemId)
            price = self.price * self.buyCount
            isSucc = True
            if itemKind:
                gameId = itemKind.gameId
            if self.buyType == config.BT_COIN:
                consumeCount, final = userchip.incrChip(self.userId, gameId, -abs(price), 0,
                                                        "BI_NFISH_BUY_ITEM_CONSUME", int(self.itemId),
                                                        self.clientId, param01=self.productId)
            elif self.buyType == config.BT_DIAMOND:
                price, isSucc = store.getUseRebateItemPrice(self.userId, self.rebateItemId, price,
                                                            self.buyType, self.productId, self.clientId)
                if price > 0 and isSucc:
                    store.autoConvertVoucherToDiamond(self.userId, abs(price))
                    consumeCount, final = userchip.incrDiamond(self.userId, gameId, -abs(price), 0,
                                                           "BI_NFISH_BUY_ITEM_CONSUME", int(self.itemId),
                                                           self.clientId, param01=self.productId)
            elif self.buyType == config.BT_COUPON:
                consumeCount, final = userchip.incrCoupon(self.userId, gameId, -abs(price), 0,
                                                          "BI_NFISH_BUY_ITEM_CONSUME", int(self.itemId),
                                                          self.clientId, param01=self.productId)
            elif self.buyType == config.BT_PEARL:
                _consume = [{"name": PEARL_KINDID, "count": abs(price)}]
                _ret = util.consumeItems(self.userId, _consume, "BI_NFISH_BUY_ITEM_CONSUME",
                                         intEventParam=int(self.itemId), param01=self.productId)
                consumeCount, final = (_ret[0][1], _ret[0][2]) if _ret else (0, 0)
            elif self.buyType == config.BT_VOUCHER:
                _consume = [{"name": VOUCHER_KINDID, "count": abs(price)}]
                _ret = util.consumeItems(self.userId, _consume, "BI_NFISH_BUY_ITEM_CONSUME",
                                         intEventParam=int(self.itemId), param01=self.productId)
                consumeCount, final = (_ret[0][1], _ret[0][2]) if _ret else (0, 0)
                vip_system.addUserVipExp(FISH_GAMEID, self.userId, abs(self.price * self.buyCount) * 10,
                                         "BUY_PRODUCT", pokerconf.productIdToNumber(self.productId),
                                         self.productId, rmbs=abs(price))
            elif self.buyType == config.BT_RUBY:
                _consume = [{"name": RUBY_KINDID, "count": abs(price)}]
                _ret = util.consumeItems(self.userId, _consume, "BI_NFISH_BUY_ITEM_CONSUME",
                                         intEventParam=int(self.itemId), param01=self.productId)
                consumeCount, final = (_ret[0][1], _ret[0][2]) if _ret else (0, 0)
            elif self.buyType == config.BT_OCEANSTAR:
                _consume = [{"name": OCEANSTAR_KINDID, "count": abs(price)}]
                _ret = util.consumeItems(self.userId, _consume, "BI_NFISH_BUY_ITEM_CONSUME",
                                         intEventParam=int(self.itemId), param01=self.productId)
                consumeCount, final = (_ret[0][1], _ret[0][2]) if _ret else (0, 0)
            if ftlog.is_debug():
                ftlog.debug("pay result =", consumeCount, final)
            if not isSucc or abs(consumeCount) != price:
                if self.buyType == config.BT_COIN:
                    self.code = BuyResultState.BRS_COIN_NOTENOUGH
                elif self.buyType == config.BT_PEARL:
                    self.code = BuyResultState.BRS_PEARL_NOTENOUGH
                elif self.buyType == config.BT_DIAMOND:
                    self.code = BuyResultState.BRS_DIAMOND_NOTENOUGH
                elif self.buyType == config.BT_COUPON:
                    self.code = BuyResultState.BRS_COUPON_NOTENOUGH
                elif self.buyType == config.BT_VOUCHER:
                    self.code = BuyResultState.BRS_VOUCHER_NOTENOUGH
                elif self.buyType == config.BT_RUBY:
                    self.code = BuyResultState.BRS_RUBY_NOTENOUGH
                elif self.buyType == config.BT_OCEANSTAR:
                    self.code = BuyResultState.BRS_OCEANSTAR_NOTENOUGH

    def _add(self):
        """
        购买成功发货
        """
        raise NotImplementedError

    def _setErrorInfo(self):
        """
        设置error文本
        """
        self.allInfo = {
            BuyResultState.BRS_SUCC:
                config.getMultiLangTextConf("ID_BUY_RESULT_INFO_0", lang=self.lang).format(time.strftime("%X", time.localtime()), self.name, self.price, config.getMultiLangTextConf(self.buyTypeStr, lang=self.lang)),
            BuyResultState.BRS_COIN_NOTENOUGH:
                config.getMultiLangTextConf("ID_EXCHANGE_ERR_COIN_NOT_ENOUGH", lang=self.lang),
            BuyResultState.BRS_PEARL_NOTENOUGH:
                config.getMultiLangTextConf("ID_EXCHANGE_ERR_PEARL_NOT_ENOUGH", lang=self.lang),
            BuyResultState.BRS_DIAMOND_NOTENOUGH:
                config.getMultiLangTextConf("ID_EXCHANGE_ERR_DIAMOND_NOT_ENOUGH", lang=self.lang),
            BuyResultState.BRS_COUPON_NOTENOUGH:
                config.getMultiLangTextConf("ID_EXCHANGE_ERR_COUPON_NOT_ENOUGH", lang=self.lang),
            BuyResultState.BRS_NEWBIE_LIMIT:
                config.getMultiLangTextConf("ID_BUY_ERR_INFO_5", lang=self.lang),
            BuyResultState.BRS_VIP_LIMIT:
                config.getMultiLangTextConf("ID_BUY_ERR_INFO_6", lang=self.lang),
            BuyResultState.BRS_DAILY_USER_BUY_COUNT_LIMIT:
                config.getMultiLangTextConf("ID_BUY_ERR_INFO_7", lang=self.lang) % self.dayBuyNum,
            BuyResultState.BRS_FAILED:
                config.getMultiLangTextConf("ID_BUY_ERR_INFO_8", lang=self.lang),
            BuyResultState.BRS_VOUCHER_NOTENOUGH:
                config.getMultiLangTextConf("ID_EXCHANGE_ERR_VOUCHER_NOT_ENOUGH", lang=self.lang),
            BuyResultState.BRS_RUBY_NOTENOUGH:
                config.getMultiLangTextConf("ID_EXCHANGE_ERR_RUBY_NOT_ENOUGH", lang=self.lang),
            BuyResultState.BRS_OCEANSTAR_NOTENOUGH:
                config.getMultiLangTextConf("ID_EXCHANGE_ERR_OCEANSTAR_NOT_ENOUGH", lang=self.lang),
            BuyResultState.BRS_TOTAL_BUY_COUNT_LIMIT:
                config.getMultiLangTextConf("ID_BUY_ERR_INFO_11", lang=self.lang),
            BuyResultState.BRS_DAILY_SERVER_BUY_COUNT_LIMIT:
                config.getMultiLangTextConf("ID_EXCHANGE_UNDER_STOCK", lang=self.lang),
            BuyResultState.BRS_VIP_DAILY_USER_BUY_COUNT_LIMIT:
                config.getMultiLangTextConf("ID_BUY_ERR_INFO_16", lang=self.lang).format(self.userVip, self.vipDailyCountLimit[self.userVip] if len(self.vipDailyCountLimit) > self.userVip else 0)
        }

    def _setInfo(self):
        """
        设置购买结果
        """
        self._setErrorInfo()
        self.info = self.allInfo[self.code]

    def buy(self):
        """
        购买
        """
        self._checkCondition()
        if self.code == BuyResultState.BRS_SUCC:
            self._pay()
        if self.code == BuyResultState.BRS_SUCC:
            util.addProductBuyEvent(self.userId, self.productId, self.clientId, self.buyCount)          # 商品购买事件
            self._add()                                                                                 # 发货
            if self.price > 0:
                from newfish.game import TGFish
                event = StoreBuyEvent(self.userId, FISH_GAMEID, self.actionType, self.productId)
                TGFish.getEventBus().publishEvent(event)
            bireport.reportGameEvent("BI_NFISH_GE_BUY_PRODUCT_ID", self.userId, FISH_GAMEID, 0, 0, 0, 0, 0, 0, [self.userId, self.productId], util.getClientId(self.userId))
        self._setInfo()
        self.ret["code"] = self.code
        self.ret["info"] = self.info
        return self.itemId, self.ret

    def error(self):
        """
        默认错误
        """
        ret = {
            "code": BuyResultState.BRS_FAILED,
            "info": config.getMultiLangTextConf("ID_BUY_ERR_INFO_8", lang=self.lang)  # u"很抱歉，购买失败，请重试"
        }
        return ret

    def _addGameRecord(self, rewards):
        """
        添加游戏记录
        """
        name = self.name
        if self.buyType == "voucher":
            message = config.getMultiLangTextConf("ID_EXCHANGE_BY_VOUCHER", lang=self.lang).format(self.price, name, util.buildRewardsDesc(rewards, self.lang))
        else:
            message = config.getMultiLangTextConf("ID_BUY_GIFT_RET_BY_DRIECT", lang=self.lang).format(name, util.buildRewardsDesc(rewards, self.lang))
        if self.product.pt == "diamond" or self.actionType == store.StoreTabType.STT_DIAMOND:
            message = message.replace("\n", "")
        GameMsg.sendPrivate(FISH_GAMEID, self.userId, 0, message)

    def _addShopBuyEvent(self):
        """
        添加购买事件
        """
        from newfish.game import TGFish
        from newfish.entity.event import ShopBuyEvent
        event = ShopBuyEvent(self.userId, FISH_GAMEID, self.productId, self.buyType, self.itemId, self.actionType)
        TGFish.getEventBus().publishEvent(event)


class CoinStoreBuyAction(BuyAction):
    """
    购买金币商店商品
    """
    def __init__(self, userId, clientId, actionType, productId, count, buyType=None, rebateItemId=0):
        super(CoinStoreBuyAction, self).__init__(userId, clientId, actionType, productId, count, buyType, rebateItemId)

    def _checkCondition(self):
        if self.price <= 0 or not self.product or not self.buyType:
            self.code = BuyResultState.BRS_FAILED
        if self.guideLimit and not util.isFinishAllNewbieTask(self.userId):
            self.code = BuyResultState.BRS_NEWBIE_LIMIT
        if self.buyType == config.BT_VOUCHER and self.userVip < self.vipLimit:
            self.code = BuyResultState.BRS_VIP_LIMIT
        self._checkUserCount()
        self._checkServerCount()

    def _add(self):
        rewards = [{"name": self.itemId, "count": self.itemCount}]
        util.addRewards(self.userId, rewards, "BUY_PRODUCT",
                        self.actionType, param01=self.productId)
        # 添加游戏记录
        self._addGameRecord(rewards)
        # 记录购买次数
        buyCoinCountDict = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.buyCoinCount, {})
        buyCoinCountDict[self.productId] = buyCoinCountDict.setdefault(self.productId, 0) + 1
        gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.buyCoinCount, json.dumps(buyCoinCountDict))
        store.getStoreTabsFish(self.userId, self.clientId, self.actionType)     # 刷新商店
        self._refreshHotStoreShop()                                             # 刷新热卖商店
        # 购买事件
        self._addShopBuyEvent()


class DiamondStoreBuyAction(BuyAction):
    """
    购买钻石商店商品
    """
    def __init__(self, userId, clientId, actionType, productId, count, buyType=None, rebateItemId=0):
        super(DiamondStoreBuyAction, self).__init__(userId, clientId, actionType, productId, count, buyType, rebateItemId)

    def _checkCondition(self):
        if self.price <= 0 or not self.product or not self.buyType:
            self.code = BuyResultState.BRS_FAILED
        self._checkUserCount()
        self._checkServerCount()

    def _add(self):
        rewards = [{"name": self.itemId, "count": self.itemCount}]
        util.addRewards(self.userId, rewards, "BUY_PRODUCT",
                        self.actionType, param01=self.productId)
        self._refreshHotStoreShop()
        # 添加游戏记录
        self._addGameRecord(rewards)
        store.getStoreTabsFish(self.userId, self.clientId, self.actionType)


class PearlStoreBuyAction(BuyAction):
    """
    购买珍珠商店商品
    """
    def __init__(self, userId, clientId, actionType, productId, count, buyType=None, rebateItemId=0):
        super(PearlStoreBuyAction, self).__init__(userId, clientId, actionType, productId, count, buyType, rebateItemId)

    def _initData(self):
        """初始化商品信息"""
        super(PearlStoreBuyAction, self)._initData()
        buyPearlCountDict = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.buyPearlCount, {})      # 珍珠商城购买各商品次数
        buyPearlCount = buyPearlCountDict.get(self.productId, 0)
        if buyPearlCount > 0:
            index = 1
            if self.userVip >= self.product.get("additionVip", 0):
                index = 2
        else:
            index = 0
        if index >= len(self.name) or index >= len(self.itemCount):
            index = 0
        # self.name = self.name[index]
        self.name = config.getMultiLangTextConf(self.name[index], lang=self.lang)
        self.itemCount = self.itemCount[index]
        if self.product.get("otherBuyType", {}).get(self.buyType):
            self.price = self.product.get("otherBuyType").get(self.buyType)
        else:
            self.price = self.product.get("price")
        if ftlog.is_debug():
            ftlog.debug("PearlStoreBuyAction->", self.userId, self.buyType, self.price, self.name, self.itemId, self.itemCount)

    def _checkCondition(self):
        if self.price <= 0 or not self.product or not self.buyType:
            self.code = BuyResultState.BRS_FAILED
        if self.guideLimit and not util.isFinishAllNewbieTask(self.userId):
            self.code = BuyResultState.BRS_NEWBIE_LIMIT
        if self.buyType == "voucher" and self.userVip < self.vipLimit:
            self.code = BuyResultState.BRS_VIP_LIMIT

    def _add(self):
        rewards = [{"name": self.itemId, "count": self.itemCount}]
        util.addRewards(self.userId, rewards, "BUY_PRODUCT",
                        self.actionType, param01=self.productId)
        # 添加游戏记录
        self._addGameRecord(rewards)
        # 记录购买次数
        buyPearlCountDict = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.buyPearlCount, {})
        buyPearlCountDict[self.productId] = buyPearlCountDict.setdefault(self.productId, 0) + 1
        gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.buyPearlCount, json.dumps(buyPearlCountDict))
        store.getStoreTabsFish(self.userId, self.clientId, self.actionType)
        self._refreshHotStoreShop()
        # 购买事件
        self._addShopBuyEvent()


class CouponStoreBuyAction(BuyAction):
    """
    购买奖券商店商品
    """
    def __init__(self, userId, clientId, actionType, productId, count, buyType=None, rebateItemId=0):
        super(CouponStoreBuyAction, self).__init__(userId, clientId, actionType, productId, count, buyType, rebateItemId)
        self.isEntity = self.product.get("extendData", {}).get("entityItem", 0)
        self.dayRefreshTime = config.getPublic("couponStoreRefreshTime", "00:00")

    def _checkCondition(self):
        # super(CouponStoreBuyAction, self)._checkCondition()
        if self.price <= 0 or not self.product or not self.buyType:
            self.code = BuyResultState.BRS_FAILED
        elif self.buyType == config.BT_COUPON and userchip.getCoupon(self.userId) < self.price * self.buyCount:
            self.code = BuyResultState.BRS_COUPON_NOTENOUGH
        elif self.guideLimit and not util.isFinishAllNewbieTask(self.userId):
            self.code = BuyResultState.BRS_NEWBIE_LIMIT
        elif self.userVip < self.vipLimit:
            self.code = BuyResultState.BRS_VIP_LIMIT
        self._checkUserCount()
        self._checkServerCount()

    def _setErrorInfo(self):
        """
        设置error文本
        """
        super(CouponStoreBuyAction, self)._setErrorInfo()
        if self.itemId == REDPACKET_KINDID:
            self.allInfo[BuyResultState.BRS_SUCC] = config.getMultiLangTextConf("ID_EXCHANGE_SUCCESS_INFO", lang=self.lang) % self.name
        else:
            self.allInfo[BuyResultState.BRS_SUCC] = config.getMultiLangTextConf("ID_EXCHANGE_RESULT_INFO_0", lang=self.lang).format(
                time.strftime("%X", time.localtime()), self.name, self.price * config.COUPON_DISPLAY_RATE,
                config.getMultiLangTextConf(self.buyTypeStr, lang=self.lang))
        self.allInfo[BuyResultState.BRS_NEWBIE_LIMIT] = \
            config.getMultiLangTextConf("ID_EXCHANGE_ERR_INFO_5", lang=self.lang)
        self.allInfo[BuyResultState.BRS_VIP_LIMIT] = \
            config.getMultiLangTextConf("ID_EXCHANGE_ERR_INFO_6", lang=self.lang).format(self.vipLimit)
        self.allInfo[BuyResultState.BRS_DAILY_USER_BUY_COUNT_LIMIT] = \
            config.getMultiLangTextConf("ID_EXCHANGE_ERR_INFO_7", lang=self.lang) % self.dayBuyNum,
        self.allInfo[BuyResultState.BRS_FAILED] = config.getMultiLangTextConf("ID_EXCHANGE_ERR_INFO_8", lang=self.lang)
        self.allInfo[BuyResultState.BRS_DAILY_SERVER_BUY_COUNT_LIMIT] = \
            config.getMultiLangTextConf("ID_EXCHANGE_ERR_INFO_12", lang=self.lang).format(self.dayRefreshTime)

    def _add(self):
        if util.isChestRewardId(self.itemId):   # 宝箱
            rewards = chest_system.getChestRewards(self.userId, self.itemId)
            chest_system.deliveryChestRewards(self.userId, self.itemId, rewards, "BI_NFISH_BUY_ITEM_GAIN")
            self.ret["rewards"] = rewards
        elif self.itemId == REDPACKET_KINDID:   # 微信红包
            hallexchange.requestExchangeCash(self.userId, self.itemCount, WX_APPID, pktimestamp.getCurrentTimestamp())
        else:                                   # 普通道具
            itemKind = hallitem.itemSystem.findItemKind(self.itemId)
            if itemKind and itemKind.gameId == HALL_GAMEID:
                userAssets = hallitem.itemSystem.loadUserAssets(self.userId)
                userAssets.addAsset(HALL_GAMEID, "item:" + str(self.itemId), abs(self.itemCount), int(time.time()),
                                    "BI_NFISH_BUY_ITEM_GAIN", self.actionType, param01=self.productId)
                datachangenotify.sendDataChangeNotify(FISH_GAMEID, self.userId, ["chip"])
            else:
                util.addRewards(self.userId, [{"name": self.itemId, "count": self.itemCount}], "BI_NFISH_BUY_ITEM_GAIN",
                                self.actionType, param01=self.productId)
        if self.product.get("visible") == 0:    # 新手限定商品（5元话费卡）
            gamedata.incrGameAttr(self.userId, FISH_GAMEID, GameData.exchangeCount, 1)
        if self.buyType == config.BT_COUPON:
            self._addGameRecord(None)
            # 兑换实体物品led广播.
            # if self.isEntity == 1:
            #     userName = util.getNickname(self.userId)
            #     userName = str(userName) if userName else ""
            #     mid = "ID_LED_COUPON_EXCHANGE_ENTITY"
            #     msg = config.getMultiLangTextConf(mid, lang=self.lang).format(
            #             userName, self.price * config.COUPON_DISPLAY_RATE, self.name)
            #     user_rpc.sendLed(FISH_GAMEID, msg, type="new", id=mid, lang=self.lang)
        todayBuyInfo = weakdata.getDayFishData(self.userId, WeakData.shopBuyInfo, {})
        key_ = "%s_%s" % ("couponStore", str(self.productId))
        todayBuyInfo[key_] = todayBuyInfo.get(key_, 0) + 1
        weakdata.setDayFishData(self.userId, WeakData.shopBuyInfo, json.dumps(todayBuyInfo))
        self._increaseDayBuyCount()
        self._refreshHotStoreShop()
        store.getStoreTabsFish(self.userId, self.clientId, self.actionType)

    def error(self):
        ret = {
            "code": BuyResultState.BRS_FAILED,
            "info": config.getMultiLangTextConf("ID_EXCHANGE_RESULT_INFO_8", lang=self.lang)
        }
        return ret

    def _addGameRecord(self, rewards):
        """
        添加游戏记录
        """
        message = config.getMultiLangTextConf("ID_EXCHANGE_BY_COUPON", lang=self.lang)
        message = message.format(self.price * config.COUPON_DISPLAY_RATE, self.name, self.name)
        message = message.replace("\n", "")
        GameMsg.sendPrivate(FISH_GAMEID, self.userId, 0, message)


class ChestStoreBuyAction(BuyAction):
    """
    购买宝箱(道具)商店商品
    """
    def __init__(self, userId, clientId, actionType, productId, count, buyType=None, rebateItemId=0):
        super(ChestStoreBuyAction, self).__init__(userId, clientId, actionType, productId, count, buyType, rebateItemId)
        # self.buyChestCountList = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.buyChestCount, [0, 0, 0, 0, 0, 0, 0])
        self.buyChestCountList = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.buyChestCount1, {})

    def _checkCondition(self):
        if self.price < 0 or not self.product or not self.buyType:
            self.code = BuyResultState.BRS_FAILED
        if self.guideLimit and not util.isFinishAllNewbieTask(self.userId):
            self.code = BuyResultState.BRS_NEWBIE_LIMIT
        if self.userVip < self.vipLimit:
            self.code = BuyResultState.BRS_VIP_LIMIT
        # 已拥有的皮肤商城中不可购买.
        if self.itemType == 5:
            ownGunSkinSkins = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.ownGunSkinSkins, [])
            if self.itemId in ownGunSkinSkins:
                self.code = BuyResultState.BRS_TOTAL_BUY_COUNT_LIMIT
        self._checkUserCount()
        self._checkServerCount()

    def _add(self):
        if util.isChestRewardId(self.itemId):
            rewards = chest_system.getChestRewards(self.userId, self.itemId)
            chest_system.deliveryChestRewards(self.userId, self.itemId, rewards, "BI_NFISH_BUY_ITEM_GAIN")
            self.ret["rewards"] = rewards
            freeData = self.product.get("extendData", {}).get("free")
            # 可以免费获取的商品, 领取免费商品后需要更新下次免费领取的时间戳.
            if freeData and self.price == 0:
                if freeData.get("type") == "day":                   # 按天免费.
                    productFreeTS = weakdata.getDayFishData(self.userId, GameData.productFreeTS, {})
                    buyDailyChestCount = weakdata.incrDayFishData(self.userId, WeakData.buyDailyChestCount, 1)
                    if buyDailyChestCount < len(freeData.get("time", [1])):
                        idx = buyDailyChestCount
                        productFreeTS[str(self.productId)] = int(time.time()) + freeData.get("time")[idx] * 3600
                    else:
                        productFreeTS[str(self.productId)] = util.getDayStartTimestamp(int(time.time())) + 86400
                    # idx = buyDailyChestCount if buyDailyChestCount < len(freeData.get("time", [1])) else -1
                    # productFreeTS[str(self.productId)] = int(time.time()) + freeData.get("time")[idx] * 3600
                    weakdata.setDayFishData(self.userId, WeakData.productFreeTS, json.dumps(productFreeTS))
                    module_tip.cancelModuleTipEvent(self.userId, "store", "chestStore1")
                elif freeData.get("type") == "interval":            # 按固定间隔免费.
                    productFreeTS = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.productFreeTS, {})
                    productFreeTS[str(self.productId)] = int(time.time()) + freeData.get("time", [1])[0] * 3600
                    gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.productFreeTS, json.dumps(productFreeTS))
                    module_tip.cancelModuleTipEvent(self.userId, "store", "chestStore2")
            # 更新商品购买次数.
            if str(self.productId) in self.buyChestCountList:
                self.buyChestCountList[str(self.productId)] += 1
            else:
                self.buyChestCountList[str(self.productId)] = 1
            gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.buyChestCount1, json.dumps(self.buyChestCountList))
            # 监测重要宝箱购买次数.
            if self.product["order"] == 3:
                buySuperChestCount = weakdata.incrDayFishData(self.userId, "buySuperChestCount", 1)
                if buySuperChestCount >= 20:
                    ftlog.error("[WARNING]doBuyItem->buySuperChestCount too many", self.userId, buySuperChestCount)
            store.getStoreTabsFish(self.userId, self.clientId, self.actionType)
            # 购买宝箱事件
            from newfish.game import TGFish
            from newfish.entity.event import BuyChestEvent
            event = BuyChestEvent(self.userId, FISH_GAMEID, self.itemId, self.buyType, self.price)
            TGFish.getEventBus().publishEvent(event)
        else:
            rewards = [{"name": self.itemId, "count": self.itemCount * self.buyCount}]
            # 皮肤炮皮肤
            if self.itemType == 5:
                ret = gun_system.addEquipGunSkinSkin(self.userId, self.itemId, self.clientId)   # 获得并装备皮肤炮皮肤
                if ret:
                    datachangenotify.sendDataChangeNotify(FISH_GAMEID, self.userId, ["chip", "item"])
                else:
                    ftlog.error("item add, skin not support! userId =", self.userId, "clientId =", self.clientId,
                                "productId =", self.productId, "skinId =", self.itemId)
            else:
                util.addRewards(self.userId, rewards, "BI_NFISH_BUY_ITEM_GAIN", param01=self.productId)
                self._increaseDayBuyCount()
            self.ret["rewards"] = rewards
            self._refreshHotStoreShop()
            store.getStoreTabsFish(self.userId, self.clientId, self.actionType)

    def _setErrorInfo(self):
        """
        设置error文本
        """
        super(ChestStoreBuyAction, self)._setErrorInfo()
        storeName = self.name
        if self.itemId in [config.PEARL_KINDID or config.RUBY_KINDID or config.GOLDEN_KEY_KINDID or config.LOCK_KINDID or config.FREEZE_KINDID]:
            storeName = "%sx%d" % (self.name, self.itemCount * self.buyCount)
        self.allInfo[BuyResultState.BRS_SUCC] = config.getMultiLangTextConf("ID_BUY_RESULT_INFO_0", lang=self.lang).format(
            time.strftime("%X", time.localtime()), storeName, self.price * self.buyCount,
            config.getMultiLangTextConf(self.buyTypeStr, lang=self.lang))


class GunSkinStoreBuyAction(BuyAction):
    """
    购买皮肤炮商店商品
    """
    def __init__(self, userId, clientId, actionType, productId, count, buyType=None, rebateItemId=0):
        super(GunSkinStoreBuyAction, self).__init__(userId, clientId, actionType, productId, count, buyType, rebateItemId)
        self.price = self.product.get("discountPrice")[0]
        self.name = config.getMultiLangTextConf(self.name, lang=self.lang)

    def _add(self):
        util.addRewards(self.userId, [{"name": self.itemId, "count": self.itemCount}], "BI_NFISH_BUY_ITEM_GAIN",
                        self.actionType, param01=self.productId)
        buyGunSkinCount = weakdata.incrDayFishData(self.userId, "buyGunSkinCount", self.itemCount)
        if buyGunSkinCount >= 300 * 24:
            ftlog.error("[WARNING]doBuyItem->buyGunSkinCount too many", self.userId, buyGunSkinCount)
        self._refreshHotStoreShop()


class BulletStoreBuyAction(BuyAction):
    """
    购买招财珠商店商品
    """
    def __init__(self, userId, clientId, actionType, productId, count, buyType=None, rebateItemId=0):
        super(BulletStoreBuyAction, self).__init__(userId, clientId, actionType, productId, count, buyType, rebateItemId)
        self.price = self.product.get("price")
        self.name = config.getMultiLangTextConf(self.name, lang=self.lang)

    def _setConf(self):
        """
        设置商品配置
        """
        version = util.getClientIdVer(self.userId)
        versionName = "hall37" if version < 5 else "hall51"
        self.storeConf = self.storeConf.get(versionName, {})

    def _checkCondition(self):
        super(BulletStoreBuyAction, self)._checkCondition()
        code, _ = store.canBuyResult(self.userId, "bulletStore", self.productId, self.product, self.userVip)
        if code != BuyResultState.BRS_SUCC:
            self.code = BuyResultState.BRS_DAILY_USER_BUY_COUNT_LIMIT

    def _add(self):
        rewards = [{"name": self.itemId, "count": self.itemCount}]
        vipAddition = self.product.get("vipAddition")
        if vipAddition and self.userVip >= vipAddition.get("vipLevel"):
            rewards.extend(vipAddition["rewards"])
        util.addRewards(self.userId, rewards, "BUY_PRODUCT", self.actionType, param01=self.productId)
        self._addGameRecord(rewards)
        # 增加招财充值奖池
        from newfish.entity.lotterypool import robbery_lottery_pool
        robbery_lottery_pool.incrRobberyRechargePool(self.userId, self.product.get("robberyBonus", 0))
        # 购买次数预警
        buyBulletCount = weakdata.incrDayFishData(self.userId, "buyBulletCount:%s" % self.itemId, self.buyCount)
        if self.itemId == config.GOLD_BULLET_KINDID and buyBulletCount >= 20:
            ftlog.error("[WARNING]doBuyItem->buyBulletCount too many", self.userId, self.itemId, buyBulletCount)
        todayBuyInfo = weakdata.getDayFishData(self.userId, WeakData.shopBuyInfo, {})
        key_ = "%s_%s" % ("bulletStore", str(self.productId))
        todayBuyInfo[key_] = todayBuyInfo.get(key_, 0) + 1
        weakdata.setDayFishData(self.userId, WeakData.shopBuyInfo, json.dumps(todayBuyInfo))
        # 购买招财珠事件
        from newfish.game import TGFish
        from newfish.entity.event import BulletBuyEvent
        event = BulletBuyEvent(self.userId, FISH_GAMEID, self.itemId, self.itemCount)
        TGFish.getEventBus().publishEvent(event)
        store.getStoreTabsFish(self.userId, self.clientId, self.actionType)
        self._refreshHotStoreShop()

    def _addGameRecord(self, rewards):
        """
        添加游戏记录
        """
        if self.buyType == config.BT_VOUCHER:
            message = config.getMultiLangTextConf("ID_EXCHANGE_BY_VOUCHER", lang=self.lang).format(self.price, self.name, self.name)
        else:
            message = config.getMultiLangTextConf("ID_BUY_GIFT_RET_BY_DRIECT", lang=self.lang).format(self.name, self.name)
        vipAddition = self.product.get("vipAddition")
        if vipAddition and self.userVip >= vipAddition.get("vipLevel"):
            message = u"%s，%s" % (message, config.getMultiLangTextConf(vipAddition["desc"], lang=self.lang))
        GameMsg.sendPrivate(FISH_GAMEID, self.userId, 0, message)


class TimeLimitedStoreBuyAction(BuyAction):
    """
    购买限时商店商品
    """
    def __init__(self, userId, clientId, actionType, productId, count, buyType=None, rebateItemId=0):
        super(TimeLimitedStoreBuyAction, self).__init__(userId, clientId, actionType, productId, count, buyType, rebateItemId)

    def _setConf(self):
        """
        设置商品配置
        """
        self.storeConf = config.getTimeLimitedStoreConf().get("stores", {})

    def _initData(self):
        super(TimeLimitedStoreBuyAction, self)._initData()
        if self.product.get("otherBuyType", {}).get(self.buyType):
            self.price = self.product.get("otherBuyType").get(self.buyType)
        else:
            self.price = int(self.product.get("price", 0))
        self.name = config.getMultiLangTextConf(self.product.get("name"), lang=self.lang)
        if ftlog.is_debug():
            ftlog.debug("TimeLimitedStoreBuyAction->", self.userId, self.buyType, self.price, self.name, self.itemId, self.itemCount)

    def _checkCondition(self):
        if self.price <= 0 or not self.product or not self.buyType:
            self.code = BuyResultState.BRS_FAILED

    def _add(self):
        if util.isChestRewardId(self.itemId):
            rewards = chest_system.getChestRewards(self.userId, self.itemId)
            chest_system.deliveryChestRewards(self.userId, self.itemId, rewards, "BI_NFISH_BUY_ITEM_GAIN")
            self.ret["rewards"] = rewards

            # 购买宝箱事件
            from newfish.game import TGFish
            from newfish.entity.event import BuyChestEvent
            event = BuyChestEvent(self.userId, FISH_GAMEID, self.itemId, self.buyType)
            TGFish.getEventBus().publishEvent(event)
        elif util.isSkillCardItemId(self.itemId):
            _, _rewards = drop_system.getDropItem(self.itemId)
            if isinstance(_rewards, list) and len(_rewards) > 0:
                rewards = [{"name": _rewards[-1]["name"], "count": _rewards[-1]["count"] * self.buyCount}]
            elif isinstance(_rewards, dict):
                rewards = [{"name": _rewards["name"], "count": _rewards["count"] * self.buyCount}]
            else:
                rewards = []
            util.addRewards(self.userId, rewards, "BI_NFISH_BUY_ITEM_GAIN", param01=self.productId)
            self.ret["rewards"] = rewards
        else:
            rewards = [{"name": self.itemId, "count": self.itemCount * self.buyCount}]
            util.addRewards(self.userId, rewards, "BI_NFISH_BUY_ITEM_GAIN", param01=self.productId)
            self.ret["rewards"] = rewards

        self._addGameRecord(rewards)

        key = GameData.timeLimitedStore % (FISH_GAMEID, self.userId)
        buyCount = json.loads(daobase.executeUserCmd(self.userId, "HGET", key, GameData.tls_buyCount) or "{}")
        buyCount.setdefault(self.productId, 0)
        buyCount[self.productId] += 1
        daobase.executeUserCmd(self.userId, "HSET", key, GameData.tls_buyCount, json.dumps(buyCount))
        buyTimeLimitedCountDict = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.buyTimeLimitedCount, {})
        buyTimeLimitedCountDict.setdefault(self.productId, 0)
        buyTimeLimitedCountDict[self.productId] += 1
        gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.buyTimeLimitedCount, json.dumps(buyTimeLimitedCountDict))
        store.getStoreTabsFish(self.userId, self.clientId, self.actionType)
        self._refreshHotStoreShop()

    def _addGameRecord(self, rewards):
        """
        添加游戏记录
        """
        name = self.name
        if self.buyType == "ruby":
            message = config.getMultiLangTextConf("ID_EXCHANGE_BY_RUBY", lang=self.lang).format(self.price, name, util.buildRewardsDesc(rewards, self.lang))
        else:
            message = config.getMultiLangTextConf("ID_BUY_GIFT_RET_BY_DRIECT", lang=self.lang).format(name, util.buildRewardsDesc(rewards, self.lang))
        message = message.replace("\n", "")
        GameMsg.sendPrivate(FISH_GAMEID, self.userId, 0, message)


class HotStoreBuyAction(object):
    """
    购买热销商店商品
    """
    def __init__(self, userId, clientId, actionType, productId, count, buyType=None, rebateItemId=0):
        storeConf = config.getStoreConf(clientId).get("hotStore")
        productId = str(productId)
        self.buyAction = None
        # 根据购买的商品类型创建对应的BuyAction.
        if storeConf.get(productId).get("pt") == "coin":
            self.buyAction = CoinStoreBuyAction(userId, clientId, actionType, productId, count, buyType, rebateItemId)
        elif storeConf.get(productId).get("pt") == "diamond":
            self.buyAction = DiamondStoreBuyAction(userId, clientId, actionType, productId, count, buyType, rebateItemId)
        elif storeConf.get(productId).get("pt") == "chest" or "item":
            self.buyAction = ChestStoreBuyAction(userId, clientId, actionType, productId, count, buyType, rebateItemId)

    def buy(self):
        """
        购买
        """
        if not self.buyAction:
            return 0, False
        return self.buyAction.buy()

    def error(self):
        """
        默认错误
        """
        if not self.buyAction:
            return {}
        return self.buyAction.error()


class ExchangeStoreBuyAction(BuyAction):
    """
    购买兑换商城商品
    """
    def __init__(self, userId, clientId, actionType, productId, count, buyType=None, rebateItemId=0):
        super(ExchangeStoreBuyAction, self).__init__(userId, clientId, actionType, productId, count, buyType, rebateItemId)
        self.categoryId = self.product.get("categoryId", 0)
        self.buyCountLimit = self.product.get("limitCond", {}).get("userCountLimit")

    def _setConf(self):
        """
        设置商品配置
        """
        self.storeConf = config.getExchangeStoreConf().get("items", {})

    @staticmethod
    def _getSubKey():
        """
        获取兑换商城按时间存档的key,使用此次购买阶段的开始时间戳
        """
        startTS = util.getTimestampFromStr(config.getExchangeStoreConf().get("startTS"))
        loopDays = config.getExchangeStoreConf().get("loopDays", 1)
        if loopDays <= 0:
            ftlog.error("ExchangeStoreShop config error! loopDays =", loopDays)
            loopDays = 1
        subKey = startTS
        while subKey + loopDays * 86400 <= int(time.time()):
            subKey += loopDays * 86400
        return subKey

    def _checkCondition(self):
        if self.price <= 0 or not self.product or not self.buyType:
            self.code = BuyResultState.BRS_FAILED
        if self.guideLimit and not util.isFinishAllNewbieTask(self.userId):
            self.code = BuyResultState.BRS_NEWBIE_LIMIT
        if self.buyType == config.BT_OCEANSTAR and self.userVip < self.vipLimit:
            self.code = BuyResultState.BRS_VIP_LIMIT
        _key = UserData.buyExchangeProduct % (FISH_GAMEID, self.userId)
        _subKey = self._getSubKey()
        buyExchangeProduct = json.loads(daobase.executeUserCmd(self.userId, "HGET", _key, str(_subKey)) or "{}")
        highestUnlockedId = buyExchangeProduct.setdefault("highestUnlockedId", 0)
        # 检查当前兑换级别是否解锁.
        if self.categoryId > highestUnlockedId:
            self.code = BuyResultState.BRS_UNLOCK
        # 检查购买次数是否已达上限.
        if self.buyCountLimit and buyExchangeProduct.get("buyCount", {}).get(self.productId, 0) >= self.buyCountLimit and self.buyCountLimit != -1:
            self.code = BuyResultState.BRS_USER_BUY_COUNT_LIMIT
        self._checkUserCount()
        self._checkServerCount()

    def _add(self):
        rewards = [{"name": self.itemId, "count": self.itemCount}]
        util.addRewards(self.userId, rewards, "BUY_PRODUCT", self.actionType, param01=self.productId)
        # 添加游戏记录
        self._addGameRecord(rewards)
        # 记录购买次数
        _key = UserData.buyExchangeProduct % (FISH_GAMEID, self.userId)
        _subKey = self._getSubKey()
        buyExchangeProduct = json.loads(daobase.executeUserCmd(self.userId, "HGET", _key, str(_subKey)) or "{}")
        buyExchangeProduct.setdefault("buyCount", {}).setdefault(str(self.productId), 0)
        buyExchangeProduct["buyCount"][str(self.productId)] += 1
        buyExchangeProduct.setdefault("highestUnlockedId", 0)
        alreadyBuyCount = buyExchangeProduct["buyCount"][str(self.productId)]
        daobase.executeUserCmd(self.userId, "HSET", _key, str(_subKey), json.dumps(buyExchangeProduct))
        if alreadyBuyCount >= self.buyCountLimit and self.buyCountLimit != -1 and buyExchangeProduct["highestUnlockedId"] < 2:
            buyExchangeProduct["highestUnlockedId"] += 1
            for productId, product in self.storeConf.iteritems():
                _categoryId = product.get("categoryId")
                _alreadyBuyCount = buyExchangeProduct.setdefault("buyCount", {}).setdefault(productId, 0)
                _buyCountLimit = product.get("limitCond").get("userCountLimit")
                if _categoryId == self.categoryId:
                    if productId not in buyExchangeProduct["buyCount"] or _alreadyBuyCount < _buyCountLimit:
                        buyExchangeProduct["highestUnlockedId"] -= 1
                        break
            daobase.executeUserCmd(self.userId, "HSET", _key, str(_subKey), json.dumps(buyExchangeProduct))
        store.getStoreTabsFish(self.userId, self.clientId, self.actionType)
        self._refreshHotStoreShop()

    def _setErrorInfo(self):
        """
        设置error文本
        """
        super(ExchangeStoreBuyAction, self)._setErrorInfo()
        self.allInfo[BuyResultState.BRS_USER_BUY_COUNT_LIMIT] = \
            config.getMultiLangTextConf("ID_BUY_ERR_INFO_13", lang=self.lang) % self.buyCountLimit
        self.allInfo[BuyResultState.BRS_UNLOCK] = config.getMultiLangTextConf("ID_BUY_ERR_INFO_14", lang=self.lang)


def doBuyItem(userId, clientId, actionType, itemId, count, buyType, rebateItemId=0):
    try:
        # 特殊处理道具商店中的招财珠商品
        from newfish.entity import store
        if actionType == store.StoreTabType.STT_ITEM and store.isBulletStore(str(itemId)):
            actionType = store.StoreTabType.STT_BULLET
        return allActionType[actionType](userId, clientId, actionType, itemId, count, buyType, rebateItemId).buy()
    except Exception as e:
        ftlog.error("doBuyItem error", e, userId, clientId, actionType, itemId, count, buyType, rebateItemId)
        ret = allActionType[actionType](userId, clientId, actionType, itemId, count, buyType, rebateItemId).error()
        return itemId, ret


def isVipItem(userId, kindId):
    """vip赠送物品数量"""
    if kindId in VIP_ITEMS:
        dayGiveCount = weakdata.getDayFishData(userId, GameData.vipPresentCount % kindId, 0)
        return dayGiveCount
    return 0


def getItemList(userId, clientId):
    """
    获取归属于捕鱼且在背包中显示的道具列表
    """
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    lang = util.getLanguage(userId, clientId)
    timestamp = pktimestamp.getCurrentTimestamp()
    itemList = ItemHelper.encodeUserItemListByGame(FISH_GAMEID, userBag, timestamp)
    itemsTmp = []
    itemConf = config.getItemConf(clientId)
    clientVersion = util.getClientVersion(userId)
    isReviewLimitVersion = util.isVersionLimit(userId, clientVersion)
    for item in itemList:
        if str(item["kindId"]) in itemConf:
            _item = itemConf.get(str(item["kindId"]))
            if _item.get("visibleInBag", 1) == 0:
                continue
            if isReviewLimitVersion and _item.get("reviewVerLimit"):
                continue
            if clientVersion and _item.get("minimumVersion"):
                if StrictVersion(str(_item["minimumVersion"])) > StrictVersion(str(clientVersion)):
                    continue
            item["giveCount"] = isVipItem(userId, item["kindId"])
            item["order"] = _item.get("order", 0)
            item["itemType"] = _item.get("itemType", 1)
            item["typeName"] = config.getMultiLangTextConf(_item.get("typeName", "ID_BAG_LIST_ITEM_TYPENAME_INTABLE"), lang=lang)
            if _item.get("up_skill", 0) == 1:
                actions = _item.get("actions", [])
                item["actions"] = []
                for it in actions:
                    if it["action"] == "up_skill":
                        skill = int(it["params"][0]["skillId"])
                        _, isMax = skill_system.isSkillMax(userId, skill)
                        if not isMax:
                            item["actions"].append(it)
                    else:
                        item["actions"].append(it)
            else:
                item["actions"] = _item.get("actions", [])
            if _item.get("name"):
                item["name"] = config.getMultiLangTextConf(_item.get("name"), lang=lang)
            if _item.get("desc"):
                item["desc"] = config.getMultiLangTextConf(_item.get("desc"), lang=lang)
            itemsTmp.append(item)
    items = sorted(itemsTmp, key=itemgetter("order", "id"))
    return items


def getHallItemList(userId, clientId):
    """
    获取归属于大厅且在背包中显示的道具列表
    """
    itemConf = config.getItemConf(clientId)
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    timestamp = pktimestamp.getCurrentTimestamp()
    itemList = ItemHelper.encodeUserItemList(HALL_GAMEID, userBag, timestamp)
    items = []
    for item in itemList:
        if itemConf.get(str(item["kindId"]), {}).get("visibleInBag", 1) == 0:
            continue
        ignore = False
        for actionDict in item["actions"]:
            if (actionDict["action"] == "exchange" and (actionDict.get("params", {}).get("needAddress", 0) == 1 or
                actionDict.get("params", {}).get("type", "") == "jdActualProduct")):
                ignore = True
        if not ignore:
            items.append(item)
    return items


def saleItem(userId, itemId, kindId, count, clientId):
    """
    出售/打开道具
    """
    reason = 1
    rewards = []
    dropConf = None
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    surplusCount = userAssets.balance(FISH_GAMEID, "item:" + str(kindId), pktimestamp.getCurrentTimestamp())
    if surplusCount < abs(count):
        return reason, rewards, dropConf
    actions = config.getItemConf(clientId, kindId).get("actions", [])
    for action in actions:
        if action["action"] == "sale":
            rewards = action["params"]
            for reward in rewards:
                reward["count"] *= count
            break
        elif action["action"] == "open":
            totalCoin = 0
            for _ in xrange(count):
                totalCoin += util.getEggsOneResultByConfig(kindId, userId)
            rewards = [{"name": config.CHIP_KINDID, "count": totalCoin}]
            weakdata.incrDayFishData(userId, "luckyEggsNum", totalCoin)  # 每日抽取金币增加
            _sendLed(userId, totalCoin, kindId)        # 发led
            from newfish.game import TGFish
            from newfish.entity.event import OpenEggsEvent
            event = OpenEggsEvent(userId, FISH_GAMEID, totalCoin)
            TGFish.getEventBus().publishEvent(event)
            dropConf = config.getEggsBonusDropConf().get(str(kindId), None)
    if rewards:
        consume = {"name": kindId, "count": -abs(count)}
        reward = rewards[0]
        if reward["name"] == config.CHIP_KINDID:
            from newfish.entity import treasure_system
            extraCoin = treasure_system.getSaleItemExtraCoin(userId, reward["count"])
            if extraCoin > 0:
                reward["count"] = reward["count"] + extraCoin
        reason = util.addRewards(userId, [consume, reward], "SALE_ITEM", kindId)
    return reason, rewards, dropConf


def convertItem(userId, kindId, count, convertKindId, clientId):
    """
    兑换道具
    """
    reason = 1
    rewards = []
    params = {}
    actions = config.getItemConf(clientId, kindId).get("actions", [])
    for action in actions:
        if action["action"] == "convert" and action["params"]["convertKindId"] == convertKindId:
            params = action["params"]
            break
    if util.isFinishAllNewbieTask(userId) and params.get("convertKindId", -1) == convertKindId:
        if count >= params["unit"] and count % params["unit"] == 0:
            userAssets = hallitem.itemSystem.loadUserAssets(userId)
            surplusCount = userAssets.balance(FISH_GAMEID, "item:" + str(kindId), pktimestamp.getCurrentTimestamp())
            if surplusCount < abs(count):
                return reason, rewards
            convertCount = params["rate"] * count
            consume = {"name": kindId, "count": -abs(count)}
            reward = {"name": convertKindId, "count": abs(int(convertCount))}
            reason = util.addRewards(userId, [consume, reward], "ASSEMBLE_ITEM", kindId)
            if reason == 0:
                rewards = [reward]
    return reason, rewards


def selectItemRewards(userId, kindId, count, idx, clientId):
    """
    选择道具奖励
    """
    reason = 1
    rewards = []
    actions = config.getItemConf(clientId, kindId).get("actions", [])
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    for action in actions:
        if action["action"] == "select":
            if 0 <= idx < len(action["params"]):
                consume = {"name": kindId, "count": -abs(count)}
                surplusCount = userAssets.balance(FISH_GAMEID, "item:" + str(kindId), pktimestamp.getCurrentTimestamp())
                if surplusCount >= abs(count):
                    reward = action["params"][idx]
                    reason = util.addRewards(userId, [consume, reward], "ASSEMBLE_ITEM", kindId)
                    if reason == 0:
                        rewards = [reward]
            break
    return reason, rewards


def _sendLed(userId, luckyCoin, itemId):
    """打开道具发送金币"""
    luckyCoin = int(luckyCoin)
    rewardId = "item:" + str(itemId)
    assetKind = hallitem.itemSystem.findAssetKind(rewardId)
    if luckyCoin < 1000000 or not assetKind:
        return
    userName = util.getNickname(userId)
    userName = str(userName) if userName else ""
    lang = util.getLanguage(userId)
    coinStr = util.formatScore(luckyCoin, lang=lang)
    if luckyCoin >= 5000000:
        # msg = u"受幸运女神眷恋，今日%s财运满贯，开启%s一次性获得了%s金币，真是羡煞旁人" % (userName,assetKind.displayName, coinStr)
        msg = config.getMultiLangTextConf("ID_LED_LUCKY_COIN_1", lang=lang) % (userName, assetKind.displayName, coinStr)
        mid = "ID_LED_LUCKY_COIN_1"
    else:
        # msg = u"恭喜玩家%s开启%s好运爆发，一次性获得了%s金币" % (userName,assetKind.displayName, coinStr)
        msg = config.getMultiLangTextConf("ID_LED_LUCKY_COIN_2", lang=lang) % (userName, assetKind.displayName, coinStr)
        mid = "ID_LED_LUCKY_COIN_2"
    user_rpc.sendLed(FISH_GAMEID, msg, id=mid, lang=lang)


def buyCoinDelivery(userId, productId, clientId):
    """
    金币商品发货
    """
    product = config.getStoreConf(clientId).get("coinStore").get("items").get(str(productId))
    if product:
        try:
            _, ret = CoinStoreBuyAction(userId, clientId, 1, productId, 1).buy()
        except Exception as e:
            ftlog.error("buyCoinDelivery->error", e, userId, clientId, productId)
            ret = CoinStoreBuyAction(userId, clientId, 1, productId, 1).error()

        mo = MsgPack()
        mo.setCmd("item_fish")
        mo.setResult("action", "buy")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("actionType", 1)
        mo.setResult("itemId", productId)
        mo.setResult("count", 1)
        for k, v in ret.iteritems():
            mo.setResult(k, v)
        router.sendToUser(mo, userId)


def processAutoBuy(userId, productId, clientId):
    """
    人民币购买钻石后再自动购买钻石商品（仅当存在自动购买数据时才生效）
    当玩家购买钻石商品但钻石不足时，记录最终商品ID(productIdB)
    先使用人民币购买钻石(productIdA)，再用钻石购买最终商品ID(productIdB)
    :param userId: 玩家userId
    :param productId: 钻石商店的钻石商品ID
    :param clientId:
    :return:
    """
    key = GameData.autoBuyAfterSDKPay % (FISH_GAMEID, userId)
    autoBuyData = daobase.executeUserCmd(userId, "GET", key)
    if not autoBuyData:
        return False
    autoBuyData = json.loads(autoBuyData)
    if len(autoBuyData) != 4:
        return False
    productIdA, productIdB, actionType, count = autoBuyData
    if str(productId) != str(productIdA):
        return False
    daobase.executeUserCmd(userId, "DEL", key)
    from newfish.entity import piggy_bank, vip_system
    from newfish.entity.gift import daily_gift
    from newfish.entity.gift import gift_system
    giftConf = gift_system.getGiftConf(clientId, str(productIdB))
    dailyGiftConf = config.getDailyGiftConf(clientId).get(str(productIdB), {})
    piggyBank = config.getPiggyBankProduct(clientId, str(productIdB))
    superEggs = [val for val in config.getSuperEggsConf(clientId).get("eggs", []) if val.get("productId") == productIdB]
    inspireItems = [val for val in config.getCompActConf(clientId).get("items", []) if val.get("productId") == productIdB]
    passCard = [val for val in config.getPassCardConf(clientId).get("productInfo", {}).values() if val.get("productId") == productIdB]

    if giftConf:                                                                            # 其他礼包 action_type == -1
        gift_system.doBuyFishGift(userId, clientId, productIdB, config.BT_DIAMOND)
    elif dailyGiftConf:                                                                     # 每日礼包 action_type == -1
        daily_gift.doBuyGift(userId, clientId, productIdB, config.BT_DIAMOND)
    elif piggyBank:                                                                         # 存钱罐 action_type == -2
        piggy_bank.buyPiggyBank(userId, clientId, productId, piggyBank.get("type", ""))
    elif superEggs:                                                                         # 国庆超级扭蛋 actionType = -3
        super_egg_activity.doBuySuperEgg(userId, clientId, config.BT_DIAMOND, productIdB)
    elif inspireItems:                                                                      # 购买竞赛活动商品
       competition_activity.doBuyCompActItem(userId, clientId, config.BT_DIAMOND, productIdB)
    elif passCard:                                                                          # 购买解锁黄金奖励商品
        pass_card_activity.doBuyUnlockProduct(userId, clientId, config.BT_DIAMOND, productIdB)
    elif int(actionType) == -6:
        doBuyLevelFunds(userId, clientId, config.BT_DIAMOND, productIdB)                    # 购买基金
    elif int(actionType) == -7:
        vip_system.buyFishVipGift(userId, productIdB, clientId, config.BT_DIAMOND)          # 购买VIP礼包
    elif int(actionType) == -8:
        doBuyLevelGift(userId, clientId, productIdB, config.BT_DIAMOND)                     # 购买升级礼包
    else:
        itemId, ret = doBuyItem(userId, clientId, actionType, productIdB, count, config.BT_DIAMOND)     # 购买道具
        mo = MsgPack()
        mo.setCmd("item_fish")
        mo.setResult("action", "buy")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("actionType", actionType)
        mo.setResult("itemId", itemId)
        mo.setResult("count", count)
        mo.setResult("buyType", config.BT_DIAMOND)
        for k, v in ret.iteritems():
            mo.setResult(k, v)
        router.sendToUser(mo, userId)
    if ftlog.is_debug():
        ftlog.debug("processAutoBuy, userId =", userId, autoBuyData)
    return True


def buyDiamondDelivery(userId, productId, clientId):
    """
    钻石商品发货
    """
    product = config.getStoreConf(clientId).get("diamondStore").get("items").get(str(productId))
    if product:
        actionType = 2
        try:
            _, ret = DiamondStoreBuyAction(userId, clientId, actionType, productId, 1).buy()
            # 处理自动购买逻辑.
            if processAutoBuy(userId, productId, clientId):                                     # 充值买钻石
                return
        except Exception as e:
            ftlog.error("buyDiamondDelivery->error", e, userId, clientId, productId)
            ret = DiamondStoreBuyAction(userId, clientId, actionType, productId, 1).error()

        mo = MsgPack()
        mo.setCmd("item_fish")
        mo.setResult("action", "buy")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("actionType", actionType)
        mo.setResult("itemId", productId)
        mo.setResult("count", 1)
        for k, v in ret.iteritems():
            mo.setResult(k, v)
        router.sendToUser(mo, userId)


def buyPearlDelivery(userId, productId, clientId):
    """
    珍珠商品发货
    """
    product = config.getStoreConf(clientId).get("pearlStore").get(str(productId))
    if product:
        try:
            _, ret = PearlStoreBuyAction(userId, clientId, 3, productId, 1).buy()
        except Exception as e:
            ftlog.error("buyPearlDelivery->error", e, userId, clientId, productId)
            ret = PearlStoreBuyAction(userId, clientId, 3, productId, 1).error()

        mo = MsgPack()
        mo.setCmd("item_fish")
        mo.setResult("action", "buy")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("actionType", 3)
        mo.setResult("itemId", productId)
        mo.setResult("count", 1)
        for k, v in ret.iteritems():
            mo.setResult(k, v)
        router.sendToUser(mo, userId)


def buyBulletDelivery(userId, productId, clientId):
    """
    招财珠商品发货
    """
    version = util.getClientIdVer(userId)
    versionName = "hall37" if version < 5 else "hall51"
    product = config.getStoreConf(clientId).get("bulletStore").get(versionName, {}).get(str(productId))
    if product:
        try:
            _, ret = BulletStoreBuyAction(userId, clientId, 7, productId, 1).buy()
        except Exception as e:
            ftlog.error("buyBulletDelivery->error", e, userId, clientId, productId)
            ret = BulletStoreBuyAction(userId, clientId, 7, productId, 1).error()

        mo = MsgPack()
        mo.setCmd("item_fish")
        mo.setResult("action", "buy")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("actionType", 7)
        mo.setResult("itemId", productId)
        mo.setResult("count", 1)
        for k, v in ret.iteritems():
            mo.setResult(k, v)
        router.sendToUser(mo, userId)


def buyChestDelivery(userId, productId, clientId):
    """
    道具商品发货
    """
    product = config.getStoreConf(clientId).get("chestStore", {}).get("items", {}).get(str(productId))
    if product:
        actionType = 5
        try:
            _, ret = ChestStoreBuyAction(userId, clientId, actionType, productId, 1).buy()
        except Exception as e:
            ftlog.error("buyChestDelivery->error", e, userId, clientId, productId)
            ret = ChestStoreBuyAction(userId, clientId, actionType, productId, 1).error()

        mo = MsgPack()
        mo.setCmd("item_fish")
        mo.setResult("action", "buy")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("actionType", actionType)
        mo.setResult("itemId", product.get("itemId", 0))
        mo.setResult("count", 1)
        for k, v in ret.iteritems():
            mo.setResult(k, v)
        router.sendToUser(mo, userId)


def _triggerChargeNotifyEvent(event):
    """触发充值通知事件"""
    ftlog.info("item._triggerChargeNotifyEvent->", "userId =", event.userId, "gameId =", event.gameId, "rmbs =",
               event.rmbs, "productId =", event.productId, "clientId =", event.clientId)
    userId = event.userId
    productId = event.productId
    clientId = event.clientId
    rmbs = event.rmbs
    buyCoinDelivery(userId, productId, clientId)
    buyDiamondDelivery(userId, productId, clientId)
    buyBulletDelivery(userId, productId, clientId)
    buyPearlDelivery(userId, productId, clientId)
    buyChestDelivery(userId, productId, clientId)
    dealRechargeRebate(userId, productId, clientId, rmbs)               # 网页充值返利
    # 清理sdk支付后的自动购买数据.
    key = GameData.autoBuyAfterSDKPay % (FISH_GAMEID, userId)
    daobase.executeUserCmd(userId, "DEL", key)
    # if util.getClientIdSys(userId) != CLIENT_SYS_H5.lower():
    #     if event.productId not in config.getPublic("notVipExpProductIds", []) and rmbs > 0:
    #         from newfish.entity.fishactivity import fish_activity_system
    #         fish_activity_system.accumulateRecharge(userId, int(rmbs))
    #         from hall.game import TGHall
    #         vipExp = hallvip.userVipSystem.getUserVip(userId).vipExp
    #         oldVipLevel = hallvip.vipSystem.findVipLevelByVipExp(vipExp - event.diamonds)
    #         userVip = hallvip.userVipSystem.getUserVip(userId)
    #         ftlog.debug("_triggerChargeNotifyEvent", userId, vipExp, event.diamonds, oldVipLevel.level, userVip.vipLevel.level)
    #         if oldVipLevel.level != userVip.vipLevel.level:
    #             invitedInfo = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.inviterInfo, None)
    #             if invitedInfo:
    #                 ftlog.debug("_triggerUserVipChange", userId, invitedInfo)
    #                 fish_activity_system.addInvitationRebateMail(userId, userVip, oldVipLevel, invitedInfo["userId"], invitedInfo["inviteTime"], invitedInfo["vip"])


def dealRechargeRebate(userId, productId, clientId, rmbs):
    """
    网页充值返利
    """
    rechargeRebateConf = config.getPublic("rechargeRebate", {})
    rebateClientIds = rechargeRebateConf.get("clientIds", [])
    rebateProductIds = rechargeRebateConf.get("productIds", [])
    if clientId in rebateClientIds and productId in rebateProductIds:
        rewards = [{"name": config.CHIP_KINDID, "count": int(rmbs * rechargeRebateConf["coinRebateRate"])}]
        # message = u"感谢您对途游休闲捕鱼的喜爱和支持，以下是您充值获得的金币奖励，祝您游戏愉快！"
        message = config.getMultiLangTextConf("ID_WEBPAGE_RECHARGE_REBATE_MESSAGE", lang=util.getLanguage(userId, clientId))
        mail_system.sendSystemMail(userId, mail_system.MailRewardType.SystemReward, rewards, message)


def _triggerExchangeEvent(event):
    ftlog.debug("_triggerExchangeEvent->", event.userId, event.item)
    # message = u"您成功使用%s，系统审核成功后奖励将通过短信发放"
    lang = util.getLanguage(event.userId)
    message = config.getMultiLangTextConf("ID_EXCHANGE_SUCCESS_EVENT_MSG", lang=lang) % (event.item.itemKind.displayName)
    GameMsg.sendPrivate(FISH_GAMEID, event.userId, 0, message)


def _triggerSaleItemEvent(event):
    ftlog.debug("_triggerSaleItemEvent->", event.userId, event.saledItem, event.gotAssetList)
    from poker.entity.biz.item.item import TYAssetUtils
    gotContent = TYAssetUtils.buildContent(event.gotAssetList[0])
    # message = u"您成功出售%s，获得%s"
    lang = util.getLanguage(event.userId)
    message = config.getMultiLangTextConf("ID_SAIL_ITEM_SUCCESS_EVENT_MSG", lang=lang).format(event.saledItem.itemKind.displayName, gotContent)
    GameMsg.sendPrivate(FISH_GAMEID, event.userId, 0, message)


_inited = False


allActionType = {
    store.StoreTabType.STT_HOT: HotStoreBuyAction,
    store.StoreTabType.STT_CHEST: ChestStoreBuyAction,
    store.StoreTabType.STT_ITEM: ChestStoreBuyAction,
    store.StoreTabType.STT_COIN: CoinStoreBuyAction,
    store.StoreTabType.STT_DIAMOND: DiamondStoreBuyAction,
    store.StoreTabType.STT_PEARL: PearlStoreBuyAction,
    store.StoreTabType.STT_COUPON: CouponStoreBuyAction,
    store.StoreTabType.STT_GUNSKIN: GunSkinStoreBuyAction,
    store.StoreTabType.STT_BULLET: BulletStoreBuyAction,
    store.StoreTabType.STT_TIMELIMITED: TimeLimitedStoreBuyAction,
    store.StoreTabType.STT_CONVERT: ExchangeStoreBuyAction
}


def initialize():
    ftlog.debug("newfish item initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from poker.entity.events.tyevent import ChargeNotifyEvent
        from hall.game import TGHall
        from hall.entity.hallitem import TYItemExchangeEvent, TYSaleItemEvent
        from newfish.game import TGFish
        from newfish.entity.event import NFChargeNotifyEvent
        TGHall.getEventBus().subscribe(TYItemExchangeEvent, _triggerExchangeEvent)
        TGHall.getEventBus().subscribe(TYSaleItemEvent, _triggerSaleItemEvent)
        TGHall.getEventBus().subscribe(ChargeNotifyEvent, _triggerChargeNotifyEvent)
        TGFish.getEventBus().subscribe(NFChargeNotifyEvent, _triggerChargeNotifyEvent)
    ftlog.debug("newfish item initialize end")