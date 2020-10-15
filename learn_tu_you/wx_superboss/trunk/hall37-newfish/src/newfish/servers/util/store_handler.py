# -*- coding=utf-8 -*-
"""
Created by lichen on 2018/10/16.
"""

from datetime import datetime
from sre_compile import isstring

from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from poker.entity.biz import orderid
import poker.util.timestamp as pktimestamp
from poker.entity.biz.exceptions import TYBizException
from poker.entity.biz.store.exceptions import TYBuyProductUnknownException
from poker.entity.biz.store.store import TYChargeInfo, TYProductBuyType, TYBuyConditionRegister
from poker.entity.configure import pokerconf, configure
from poker.entity.configure.configure import DEFAULT_CLIENT_ID
from poker.entity.dao import sessiondata, paydata
from poker.entity.events.tyevent import ChargeNotifyEvent
from poker.protocol import router, runcmd
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from poker.util import strutil
from hall.entity import hallstore, hallitem, datachangenotify, \
    hall_first_recharge, hallvip
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.hallusercond import UserConditionRegister
from hall.entity.todotask import TodoTaskPayOrder, TodoTaskShowInfo, \
    TodoTaskHelper, TodoTaskGotoShop, TodoTaskRegister
from hall.entity.hallpopwnd import findTodotaskTemplate
from hall.game import TGHall
from hall.servers.common.base_checker import BaseMsgPackChecker
from newfish.entity import config, store


@markCmdActionHandler
class StoreTcpHandler(BaseMsgPackChecker):

    def __init__(self):
        self.orderSeq = 0

    def _check_param_chargeType(self, msg, key, params):
        chargeType = msg.getParam(key)
        if chargeType and not isstring(chargeType):
            return "ERROR of chargeType !" + str(chargeType), None
        return None, chargeType or ""

    def _check_param_consumeMap(self, msg, key, params):
        consumeMap = msg.getParam(key)
        if consumeMap and not isinstance(consumeMap, dict):
            return "ERROR of consumeMap !" + str(consumeMap), None
        if consumeMap:
            for k, v in consumeMap.iteritems():
                if not isstring(k):
                    return "consumeMap.key must be string !" + str(consumeMap), None
                if not isinstance(v, (int, float)):
                    return "consumeMap.value must be int or float !" + str(consumeMap), None
        return None, consumeMap or {}

    def _check_param_chargeMap(self, msg, key, params):
        chargeMap = msg.getParam(key)
        if chargeMap and not isinstance(chargeMap, dict):
            return "ERROR of chargeMap !" + str(chargeMap), None
        if chargeMap:
            for k, v in chargeMap.iteritems():
                if not isstring(k):
                    return "chargeMap.key must be string !" + str(chargeMap), None
                if not isinstance(v, (int, float)):
                    return "chargeMap.value must be int or float !" + str(chargeMap), None
        return None, chargeMap or {}

    def _check_param_orderId(self, msg, key, params):
        orderId = msg.getParam(key)
        if (isstring(orderId)
                and (orderid.is_valid_orderid_str(orderId)
                     or orderId in ("ios_compensate", "momo_compensate"))):
            return None, orderId
        return "ERROR of orderId !" + str(orderId), None

    def _check_param_productId(self, msg, key, params):
        productId = msg.getParam(key)
        if isstring(productId) and productId:
            return None, productId
        return "ERROR of productId !" + str(productId), None

    def _check_param_prodId(self, msg, key, params):
        productId = msg.getParam(key)
        if isstring(productId) and productId:
            return None, productId
        return "ERROR of prodId !" + str(productId), None

    def _check_param_diamonds(self, msg, key, params):
        diamonds = msg.getParam(key)
        try:
            diamonds = int(diamonds)
            return None, diamonds
        except:
            return "ERROR of diamonds !" + str(diamonds), None

    def _check_param_rmbs(self, msg, key, params):
        rmbs = msg.getParam(key)
        try:
            rmbs = float(rmbs)
            return None, rmbs
        except:
            return "ERROR of rmbs !" + str(rmbs), None

    def _check_param_realGameId(self, msg, key, params):
        value = msg.getParam(key, 0)
        try:
            value = int(value)
        except:
            value = 0
        return None, value

    def _check_param_count(self, msg, key, params):
        value = msg.getParam(key, 0)
        try:
            value = int(value)
        except:
            value = 0
        if value <= 0:
            return "ERROR of count!" + str(value), None
        return None, value

    def _check_param_actionType(self, msg, key, params):
        actionType = msg.getParam("actionType")
        if isinstance(actionType, int):
            return None, actionType
        return "ERROR of actionType !" + str(actionType), None

    def _check_param_refresh(self, msg, key, params):
        refresh = msg.getParam("refresh", 0)
        if isinstance(refresh, int):
            return None, refresh
        return "ERROR of refresh !" + str(refresh), None

    def _check_param_itemId(self, msg, key, params):
        itemId = msg.getParam("itemId")
        if itemId:
            return None, itemId
        return "ERROR of itemId !" + str(itemId), None

    def _check_param_rebateItemId(self, msg, key, params):
        rebateItemId = msg.getParam("rebateItemId", 0)
        if isinstance(rebateItemId, int) and rebateItemId >= 0:
            return None, rebateItemId
        return "ERROR of rebateItemId !" + str(rebateItemId), None

    def _check_param_productIdA(self, msg, key, params):
        productIdA = msg.getParam("productIdA")
        if isinstance(productIdA, (int, str, unicode)):
            return None, productIdA
        return "ERROR of productIdA !" + str(productIdA), None

    def _check_param_productIdB(self, msg, key, params):
        productIdB = msg.getParam("productIdB")
        if isinstance(productIdB, (int, str, unicode)):
            return None, productIdB
        return "ERROR of productIdB !" + str(productIdB), None

    @markCmdActionMethod(cmd="store_config_fish", action="update", clientIdVer=0, scope="game", lockParamName="")
    def doStoreConfigUpdateFish(self, gameId, userId, clientId, actionType, refresh=0):
        """获取捕鱼商店"""
        ftlog.debug("doStoreConfigUpdateFish", gameId, userId, clientId, actionType, bool(refresh == 1))
        store.getStoreTabsFish(userId, clientId, actionType, bool(refresh == 1))

    @markCmdActionMethod(cmd="store_config_fish", action="convertItem", clientIdVer=0, scope="game", lockParamName="")
    def doStoreConvertItem(self, gameId, userId, clientId, count, itemId, rebateItemId):
        """使用钻石转换为物品"""
        ftlog.debug("doStoreConvertItem", gameId, userId, clientId, count, itemId, rebateItemId)
        store.convertItemByDiamond(userId, count, itemId, True, rebateItemId, clientId)

    @markCmdActionMethod(cmd="store_config_fish", action="autoBuyAferSDKPay", clientIdVer=0, scope="game", lockParamName="")
    def doStoreAutoBuyAferSDKPay(self, gameId, userId, clientId, productIdA, productIdB, count, actionType):
        """设置自动购买钻石触发自动发奖的逻辑"""
        ftlog.debug("doStoreAutoBuyAferSDKPay", gameId, userId, clientId, productIdA, productIdB, count, actionType)
        store.setAutoBuyAfterSDKPayData(userId, productIdA, productIdB, actionType, count)

    @markCmdActionMethod(cmd="charge_notify", action="", clientIdVer=5)
    def doChargeNotify5(self, gameId, userId, prodId, rmbs, diamonds, clientId):
        """
        人民币购买商品成功回调
        """
        # from newfish.entity import vip_system
        # if diamonds > 0 and prodId not in config.getPublic("notVipExpProductIds", []):
        #     vip_system.addUserVipExp(gameId, userId, diamonds, "BUY_PRODUCT", pokerconf.productIdToNumber(prodId), rmbs=rmbs)
        ftlog.debug("doChargeNotify5", gameId, userId, prodId, rmbs, diamonds)
        # TGHall.getEventBus().publishEvent(ChargeNotifyEvent(userId, gameId, rmbs, diamonds, prodId, clientId))
        from newfish.entity.event import NFChargeNotifyEvent
        from newfish.game import TGFish
        TGFish.getEventBus().publishEvent(NFChargeNotifyEvent(userId, gameId, rmbs, diamonds, prodId, clientId, True))
        mo = MsgPack()
        mo.setCmd("charge_notify")
        mo.setResult("userId", userId)
        mo.setResult("gameId", gameId)
        return mo