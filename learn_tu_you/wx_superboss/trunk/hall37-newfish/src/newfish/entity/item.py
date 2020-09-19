#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/30
# 原则上每个商品购买对应一个BuyAction，每个BuyAction对应一个BaseProduct，
# 但是HotStoreBuyAction中的商品购买根据pt类型对应不用的BaseProduct!

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
        """检查条件"""
        if self.price <= 0 or not self.product or not self.buyType:                     # 商品价格
            self.code = BuyResultState.BRS_FAILED
        elif self.guideLimit and not util.isFinishAllNewbieTask(self.userId):
            self.code = BuyResultState.BRS_NEWBIE_LIMIT
        elif self.userVip < self.vipLimit:
            self.code = BuyResultState.BRS_VIP_LIMIT

    def _checkServerCount(self):
        """
        检查商品服务器数量限制,此检测会尝试购买次数,所以需要在检测完其他条件后再检测！！！
        """
        ftlog.debug("checkServerCount0000", self.tabName, "userId =", self.userId, "buyType =", self.buyType,
                    "price =", self.price, "name =", self.name, "itemId =", self.itemId, "itemCount =", self.itemCount)
        if self.code != BuyResultState.BRS_SUCC:
            return
        if self.actionType == store.StoreTabType.STT_COUPON:            # 奖券
            serverBuyCount = self.product.get("limitCond", {}).get("serverDailyCountLimit", -1)
            key = MixData.buyProductServerCount % FISH_GAMEID
        else:
            serverBuyCount = self.product.get("limitCond", {}).get("hotServerDailyCountLimit", -1)
            key = MixData.buyHotProductServerCount % FISH_GAMEID




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
    store.StoreTabType.STT_EXCHANGE: ExchangeStoreBuyAction
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