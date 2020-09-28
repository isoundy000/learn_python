# -*- coding=utf-8 -*-
"""
存钱罐模块
"""
# @Author  : Kangxiaopeng
# @Time    : 2019/6/11

import time
import json

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.entity.configure import pokerconf
from poker.protocol import router
from hall.entity import hallvip
from poker.entity.dao import userchip, daobase
from newfish.entity import config, util, store, vip_system, weakdata
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData, UserData


FREE_PIGGY_BANK_COOLDOWN_INTERVAL = 60 * 60 * 20


def _getResetTime(resetTime):
    if resetTime not in range(24):
        return -1
    else:
        return resetTime


def _getDataKey(ts, resetTime):
    """
    获取数据存储key值
    """
    curDayStartTS = util.getDayStartTimestamp(ts)
    if resetTime == -1:
        return str(curDayStartTS)
    resetTS = curDayStartTS + resetTime * 3600
    if ts < resetTS:
        _key = str(resetTS - 86400)
    else:
        _key = str(resetTS)
    return _key


def _initSaveLoad(userId, clientId):
    """
    初始化存档
    """
    _ts = int(time.time()) / 60 * 60
    vipLevel = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
    piggyBankconf = config.getPiggyBankConf(clientId, vipLevel)
    key = UserData.piggyBankData % (FISH_GAMEID, userId)
    if not daobase.executeUserCmd(userId, "EXISTS", key):
        curDayStartTS = util.getDayStartTimestamp(_ts)
        freeData = {GameData.pb_enable: 1, GameData.pb_saveMoneyTS: _ts,
                    GameData.pb_moneyCount: piggyBankconf.get("free", {}).get("initVal", 0),
                    GameData.pb_getMoneyTS: 0., GameData.pb_savedMoneyCount: {str(curDayStartTS): 0.}}
        paidData = {GameData.pb_enable: 0, GameData.pb_saveMoneyTS: _ts,
                    GameData.pb_moneyCount: piggyBankconf.get("paid", {}).get("initVal", 0),
                    GameData.pb_getMoneyTS: 0., GameData.pb_savedMoneyCount: {str(curDayStartTS): 0.}}
        daobase.executeUserCmd(userId, "HSET", key, "free", json.dumps(freeData))
        daobase.executeUserCmd(userId, "HSET", key, "paid", json.dumps(paidData))
    if True:
        freeData = daobase.executeUserCmd(userId, "HGET", key, "free")
        freeData = json.loads(freeData or "{}")
        resetTime = _getResetTime(piggyBankconf.get("free", {}).get("resetTime", -1))
        if resetTime != -1:
            resetKey = _getDataKey(_ts, resetTime)
            freeData.setdefault(GameData.pb_moneyCountDict, {})
            freeData[GameData.pb_moneyCountDict].setdefault(resetKey, piggyBankconf.get("free", {}).get("initVal", 0))
            freeData[GameData.pb_moneyCount] = freeData[GameData.pb_moneyCountDict][resetKey]
            daobase.executeUserCmd(userId, "HSET", key, "free", json.dumps(freeData))
            ftlog.debug("piggy_bank, userId =", userId, "free", freeData)
        else:
            # 之前是重置的存钱罐,使用最近一次的存档存档.
            ts_keys = freeData.get(GameData.pb_moneyCountDict, {}).keys()
            if isinstance(ts_keys, list) and len(ts_keys) > 0:
                ts_keys = [int(_t) for _t in ts_keys]
                ts_keys.sort()
                freeData[GameData.pb_moneyCount] = freeData[GameData.pb_moneyCountDict][str(ts_keys[-1])]
                del freeData[GameData.pb_moneyCountDict]
                daobase.executeUserCmd(userId, "HSET", key, "free", json.dumps(freeData))
                ftlog.debug("piggy_bank, use old saveload, userId =", userId, "free =", freeData)
        paidData = daobase.executeUserCmd(userId, "HGET", key, "paid")
        paidData = json.loads(paidData or "{}")
        resetTime = _getResetTime(piggyBankconf.get("paid", {}).get("resetTime", -1))
        if resetTime != -1:
            resetKey = _getDataKey(_ts, resetTime)
            paidData.setdefault(GameData.pb_moneyCountDict, {})
            paidData[GameData.pb_moneyCountDict].setdefault(resetKey, piggyBankconf.get("paid", {}).get("initVal", 0))
            paidData[GameData.pb_moneyCount] = paidData[GameData.pb_moneyCountDict][resetKey]
            daobase.executeUserCmd(userId, "HSET", key, "paid", json.dumps(paidData))
            ftlog.debug("piggy_bank, userId =", userId, "paid", paidData)
        else:
            # 之前是重置的存钱罐,使用最近一次的存档存档.
            ts_keys = paidData.get(GameData.pb_moneyCountDict, {}).keys()
            if isinstance(ts_keys, list) and len(ts_keys) > 0:
                ts_keys = [int(_t) for _t in ts_keys]
                ts_keys.sort()
                paidData[GameData.pb_moneyCount] = paidData[GameData.pb_moneyCountDict][str(ts_keys[-1])]
                del paidData[GameData.pb_moneyCountDict]
                daobase.executeUserCmd(userId, "HSET", key, "paid", json.dumps(paidData))
                ftlog.debug("piggy_bank, use old saveload, userId =", userId, "paid =", paidData)


def addMoneyToPiggyBank(userId, clientId, type, addCount, ts=None):
    """
    向存钱罐加钱
    """
    isFire = (ts is None)
    vipLevel = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
    piggyBankconf = config.getPiggyBankConf(clientId, vipLevel)
    conf = piggyBankconf.get(type, {})
    curtime = int(time.time())
    key = UserData.piggyBankData % (FISH_GAMEID, userId)
    # 初始化存档.
    _initSaveLoad(userId, clientId)

    piggyBankData = daobase.executeUserCmd(userId, "HGET", key, type)
    if piggyBankData:
        piggyBankData = json.loads(piggyBankData)
    else:
        piggyBankData = {}
    # if piggyBankData.get(GameData.pb_enable, 0) and conf:
    if conf:
        resetTime = _getResetTime(conf.get("resetTime", -1))
        if ts:
            piggyBankData[GameData.pb_saveMoneyTS] = ts
        else:
            ts = int(time.time())
        resetKey = _getDataKey(ts, resetTime)  # str(util.getDayStartTimestamp(ts))
        if resetTime != -1:
            piggyBankData.setdefault(GameData.pb_moneyCountDict, {})
            piggyBankData[GameData.pb_moneyCountDict].setdefault(resetKey, conf.get("initVal", 0))
            piggyBankData[GameData.pb_moneyCount] = piggyBankData[GameData.pb_moneyCountDict][resetKey]
        # 开火消耗等在冷却开启时未达到冷却结束时不累积存钱罐.时间累积在计算的地方处理.
        if isFire and conf.get("iscooling", 0) and curtime <= piggyBankData.get(GameData.pb_endcoolingTS, 0):
            daobase.executeUserCmd(userId, "HSET", key, type, json.dumps(piggyBankData))
            ftlog.debug("piggy_bank, userId =", userId, "is cooling !")
            return
        if addCount > 0:
            if resetTime == -1:
                totalMoney = int(piggyBankData.get(GameData.pb_moneyCount, 0))
            else:
                totalMoney = int(piggyBankData.get(GameData.pb_moneyCountDict, {}).get(resetKey, 0))
            dailyMoney = piggyBankData[GameData.pb_savedMoneyCount].setdefault(resetKey, 0)
            if totalMoney < conf.get("maxCount", 0):
                if conf.get("maxDailyCount", 0) > 0:
                    if dailyMoney < conf["maxDailyCount"]:
                        realAddMoney = min(addCount, conf["maxDailyCount"] - dailyMoney)
                    else:
                        realAddMoney = 0
                else:
                    realAddMoney = addCount
                realAddMoney = min(realAddMoney, conf["maxCount"] - totalMoney)
                if realAddMoney > 0:
                    if resetTime == -1:
                        piggyBankData[GameData.pb_moneyCount] += realAddMoney
                    else:
                        piggyBankData[GameData.pb_moneyCountDict][resetKey] += realAddMoney
                        piggyBankData[GameData.pb_moneyCount] = piggyBankData[GameData.pb_moneyCountDict][resetKey]
                    piggyBankData[GameData.pb_savedMoneyCount][resetKey] += realAddMoney
                ftlog.debug("piggy_bank, userId =", userId, "type =", type, "vip =", vipLevel,
                            "realAddMoney =", realAddMoney, "addCount =", addCount, "piggyBankData =", piggyBankData)
        daobase.executeUserCmd(userId, "HSET", key, type, json.dumps(piggyBankData))


def saveMoneyToPiggyBank(userId, clientId):
    """
    向存钱罐存钱
    """
    vipLevel = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
    conf = config.getPiggyBankConf(clientId, vipLevel)
    key = UserData.piggyBankData % (FISH_GAMEID, userId)
    ts = int(time.time()) / 60 * 60
    curDayStartTS = util.getDayStartTimestamp(ts)
    # 初始化存档.
    _initSaveLoad(userId, clientId)

    for k, v in conf.iteritems():
        piggyBankData = daobase.executeUserCmd(userId, "HGET", key, k)
        if piggyBankData:
            piggyBankData = json.loads(piggyBankData)
        else:
            piggyBankData = {}
        # ftlog.debug("piggy_bank, userId =", userId, piggyBankData)
        lastTS = piggyBankData.get(GameData.pb_saveMoneyTS, 0)
        if lastTS == 0:
            continue
        endcoolingTs = piggyBankData.get(GameData.pb_endcoolingTS, 0)
        unitCount = v.get("outroom", 0)
        resetTime = _getResetTime(v.get("resetTime", -1))
        # 处理跨天逻辑.
        while lastTS < curDayStartTS:
            if resetTime != -1:
                resetTS = util.getDayStartTimestamp(lastTS) + resetTime * 3600
                if lastTS < endcoolingTs < resetTS:
                    lastTS = endcoolingTs
                elif resetTS < endcoolingTs:
                    lastTS = resetTS
                if lastTS < resetTS:
                    interval = (resetTS - lastTS) / 60
                    addCount = interval * unitCount
                    if interval > 0:
                        ftlog.debug("piggy_bank, userId =", userId, "type =", k, "interval =", interval, "vip =",
                                    vipLevel,
                                    "addCount =", addCount, piggyBankData, util.timestampToStr(lastTS),
                                    util.timestampToStr(resetTS))
                        addMoneyToPiggyBank(userId, clientId, k, addCount, resetTS - 1)
                    lastTS = resetTS
            nextStartDayTS = util.getDayStartTimestamp(lastTS) + 86400
            if lastTS < endcoolingTs < nextStartDayTS:
                lastTS = endcoolingTs
            elif nextStartDayTS < endcoolingTs:
                lastTS = nextStartDayTS
            interval = (nextStartDayTS - lastTS) / 60
            addCount = interval * unitCount
            if interval > 0:
                ftlog.debug("piggy_bank, userId =", userId, "type =", k, "interval =", interval, "vip =", vipLevel,
                            "addCount =", addCount, piggyBankData, util.timestampToStr(lastTS), util.timestampToStr(nextStartDayTS))
                addMoneyToPiggyBank(userId, clientId, k, addCount, nextStartDayTS - 1)
            lastTS = nextStartDayTS
        if resetTime != -1:
            resetTS = util.getDayStartTimestamp(lastTS) + resetTime * 3600
            if lastTS < resetTS < ts:
                if lastTS < endcoolingTs < resetTS:
                    lastTS = endcoolingTs
                elif resetTS < endcoolingTs:
                    lastTS = resetTS
                interval = (resetTS - lastTS) / 60
                addCount = interval * unitCount
                if interval > 0:
                    ftlog.debug("piggy_bank, userId =", userId, "type =", k, "interval =", interval, "vip =",
                                vipLevel,
                                "addCount =", addCount, piggyBankData, util.timestampToStr(lastTS),
                                util.timestampToStr(resetTS))
                    addMoneyToPiggyBank(userId, clientId, k, addCount, resetTS - 1)
                lastTS = resetTS
        if lastTS < endcoolingTs < ts:
            lastTS = endcoolingTs
        elif ts < endcoolingTs:
            lastTS = ts
        interval = (ts - lastTS) / 60
        addCount = interval * unitCount
        if interval > 0:
            ftlog.debug("piggy_bank, userId =", userId, "type =", k, "interval =", interval, "vip =", vipLevel,
                        "addCount =", addCount, piggyBankData, util.timestampToStr(lastTS), util.timestampToStr(ts))
            addMoneyToPiggyBank(userId, clientId, k, addCount, ts)

    # 清理过期的每日积累上线key
    for k, v in conf.iteritems():
        piggyBankData = daobase.executeUserCmd(userId, "HGET", key, k)
        if piggyBankData:
            piggyBankData = json.loads(piggyBankData)
        else:
            piggyBankData = {}
        isChanged = False
        resetTime = _getResetTime(v.get("resetTime", -1))
        _resetTS = int(_getDataKey(int(time.time()), resetTime))
        ts_keys = piggyBankData[GameData.pb_savedMoneyCount].keys()
        for ts in ts_keys:
            if int(ts) < _resetTS:
                ftlog.debug("piggy_bank, delete pb_savedMoneyCount expired ts key, userId =", userId, "type =", k,
                            "ts =", util.timestampToStr(int(ts)), "val =", piggyBankData[GameData.pb_savedMoneyCount][ts])
                del piggyBankData[GameData.pb_savedMoneyCount][ts]
                isChanged = True
        if resetTime != -1:
            ts_keys = piggyBankData.get(GameData.pb_moneyCountDict, {}).keys()
            for ts in ts_keys:
                if int(ts) < _resetTS:
                    ftlog.debug("piggy_bank, delete pb_moneyCountDict expired ts key, userId =", userId, "type =", k,
                                "ts =", util.timestampToStr(int(ts)), "val =",
                                piggyBankData[GameData.pb_moneyCountDict][ts])
                    del piggyBankData[GameData.pb_moneyCountDict][ts]
                    isChanged = True
        if isChanged:
            # ftlog.debug("piggy_bank, piggyBankData changed, userId =", userId, piggyBankData)
            daobase.executeUserCmd(userId, "HSET", key, k, json.dumps(piggyBankData))


def getMoney(userId, clientId, productId):
    """
    取钱
    """
    key = UserData.piggyBankData % (FISH_GAMEID, userId)
    vipLevel = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
    conf = config.getPiggyBankProduct(clientId, productId)
    type = conf.get("type")
    iscooling = conf.get("iscooling", 0)
    ts = int(time.time()) / 60 * 60
    endcoolingTS = 0
    if iscooling:
        endcoolingTime = conf.get("endcoolingTime", 0)
        endcoolingTS = util.getDayStartTimestamp(ts) + endcoolingTime * 60 * 60
        if ts >= endcoolingTS:
            endcoolingTS += 86400
    piggyBankData = daobase.executeUserCmd(userId, "HGET", key, type)
    if piggyBankData:
        piggyBankData = json.loads(piggyBankData)
    else:
        piggyBankData = {}
    code = 4
    totalMoney = 0
    getMoneyCount = 0
    rewards = []
    if piggyBankData.get(GameData.pb_enable, 0) == 1 and piggyBankData.get(GameData.pb_getMoneyTS, 0) <= ts:
        code = 0
        resetTime = _getResetTime(conf.get("resetTime", -1))
        _resetKey = _getDataKey(ts, resetTime)  # str(util.getDayStartTimestamp(ts))
        if resetTime == -1:
            totalMoney = int(piggyBankData.get(GameData.pb_moneyCount, 0))
        else:
            totalMoney = int(piggyBankData.get(GameData.pb_moneyCountDict, {}).get(_resetKey, 0))
        getMoneyCount = min(totalMoney, conf.get("maxCount", 0))
        if getMoneyCount > 0:
            piggyBankData[GameData.pb_savedMoneyCount].setdefault(_resetKey, 0)
            piggyBankData[GameData.pb_savedMoneyCount][_resetKey] = 0
            # piggyBankData[GameData.pb_moneyCount] -= getMoneyCount
            if type == "free":
                piggyBankData[GameData.pb_getMoneyTS] = ts + FREE_PIGGY_BANK_COOLDOWN_INTERVAL
            else:
                if iscooling:
                    piggyBankData[GameData.pb_endcoolingTS] = endcoolingTS
                    piggyBankData[GameData.pb_getMoneyTS] = piggyBankData[GameData.pb_endcoolingTS]
                else:
                    piggyBankData[GameData.pb_getMoneyTS] = 0
                piggyBankData[GameData.pb_enable] = 0
                piggyBankData[GameData.pb_saveMoneyTS] = ts
            conf = config.getPiggyBankConf(clientId, vipLevel).get(type, {})
            if resetTime == -1:
                piggyBankData[GameData.pb_moneyCount] = conf.get("initVal", 0)
            else:
                piggyBankData.setdefault(GameData.pb_moneyCountDict, {})
                piggyBankData[GameData.pb_moneyCountDict][_resetKey] = conf.get("initVal", 0)
                piggyBankData[GameData.pb_moneyCount] = piggyBankData[GameData.pb_moneyCountDict][_resetKey]

            daobase.executeUserCmd(userId, "HSET", key, type, json.dumps(piggyBankData))
            rewards = [{"name": config.CHIP_KINDID, "count": getMoneyCount}]
            util.addRewards(userId, rewards, "BI_NFISH_GET_PIGGY_BANK", vipLevel)
    ftlog.debug("piggy_bank, userId =", userId, "type =", type, "totalMoney =", totalMoney, "getMoneyCount =",
                getMoneyCount, "code =", code, "piggyBankData =", piggyBankData, util.timestampToStr(ts))
    return code, rewards


def getMoneyFromPiggyBank(userId, clientId, productId):
    """
    从存钱罐中取钱
    """
    saveMoneyToPiggyBank(userId, clientId)

    code, rewards = getMoney(userId, clientId, productId)

    mo = MsgPack()
    mo.setCmd("piggyBankGet")
    mo.setResult("gameId", config.FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("productId", productId)
    mo.setResult("code", code)
    mo.setResult("reward", rewards)
    router.sendToUser(mo, userId)

    getPiggyBankInfo(userId, clientId)


def getPiggyBankInfo(userId, clientId):
    """
    获取存钱罐数据
    """
    saveMoneyToPiggyBank(userId, clientId)

    vipLevel = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
    key = UserData.piggyBankData % (FISH_GAMEID, userId)
    conf = config.getPiggyBankConf(clientId, vipLevel)
    info = {}
    ts = int(time.time())
    lang = util.getLanguage(userId)
    for k, v in conf.iteritems():
        piggyBankData = daobase.executeUserCmd(userId, "HGET", key, k)
        piggyBankData = json.loads(piggyBankData)
        info[k] = {}
        resetTime = _getResetTime(v.get("resetTime", -1))
        _resetKey = _getDataKey(ts, resetTime)# str(util.getDayStartTimestamp(ts))
        info[k]["productId"] = v.get("productId", "")
        info[k]["productName"] = v.get("productName", "")
        info[k]["maxDailyCount"] = v.get("maxDailyCount", 0)
        info[k]["maxCount"] = v.get("maxCount", 0)
        info[k]["price"] = v.get("price", 0)
        info[k]["price_direct"] = v.get("price_direct", 0)
        info[k]["price_diamond"] = v.get("price_diamond", 0)
        info[k]["rule"] = 0
        ruleId = v.get("rule", 0)
        if ruleId:
            info[k]["rule"] = config.getMultiLangTextConf(str(ruleId), lang=lang)
        #info[k]["rule"] = v.get("rule", 0)
        info[k]["enable"] = piggyBankData.get(GameData.pb_enable, 0)
        if resetTime == -1:
            curCount = int(piggyBankData.get(GameData.pb_moneyCount, 0))
        else:
            curCount = int(piggyBankData.get(GameData.pb_moneyCountDict, {}).get(_resetKey, 0))
        info[k]["curCount"] = min(v.get("maxCount", 0), curCount)
        info[k]["dailyCount"] = int(piggyBankData[GameData.pb_savedMoneyCount].setdefault(_resetKey, 0))
        dailyMaxTimes = v.get("dailyTimes", 0)
        if weakdata.getDayFishData(userId, "pb_buyTimes", 0) < dailyMaxTimes:
            info[k]["leftTime"] = 0
        else:
            info[k]["leftTime"] = max(piggyBankData.get(GameData.pb_getMoneyTS, 0) - ts, 0)
        info[k]["buyType"] = v.get("buyType")
        info[k]["other_buy_type"] = v.get("otherBuyType", {})
        info[k]["otherProductInfo"] = store.getOtherBuyProduct(v.get("otherBuyType", {}), v.get("buyType"))
        if resetTime != -1:
            info[k]["resetTime"] = resetTime
    mo = MsgPack()
    mo.setCmd("piggyBankInfo")
    mo.setResult("gameId", config.FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("bankInfo", info)
    router.sendToUser(mo, userId)
    ftlog.debug("piggy_bank, userId =", userId, "vip =", vipLevel, "info =", info)


def buyPiggyBank(userId, clientId, productId, buyType=None, itemId=0):
    """
    购买存钱罐
    """
    code = 3
    rewards = []
    product = config.getPiggyBankProduct(clientId, productId)
    if product is None:
        mo = MsgPack()
        mo.setCmd("piggyBankBuy")
        mo.setResult("gameId", config.FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("productId", productId)
        mo.setResult("code", code)
        router.sendToUser(mo, userId)
        ftlog.warn("piggy_bank, userId =", userId, "productId =", productId, "buyType =", buyType, "code =", code)
        return
    # if buyType:
    #     if buyType not in product.get("otherBuyType", {}):
    #         return
    # else:
    #     buyType = product.get("buyType")
    type = product.get("type")
    key = UserData.piggyBankData % (FISH_GAMEID, userId)
    piggyBankData = daobase.executeUserCmd(userId, "HGET", key, type)
    dailyMaxTimes = product.get("dailyTimes", 0)
    if piggyBankData:
        piggyBankData = json.loads(piggyBankData)
    else:
        piggyBankData = {}
    ts = int(time.time()) / 60 * 60
    if piggyBankData.get(GameData.pb_enable, 0) == 0 and weakdata.getDayFishData(userId, "pb_buyTimes", 0) < dailyMaxTimes:
        isSucc = False
        if buyType in product.get("otherBuyType", {}):
            price = product["otherBuyType"].get(buyType, 0)
            if buyType == config.BT_VOUCHER and price > 0:
                _consume = [{"name": config.VOUCHER_KINDID, "count": abs(price)}]
                _ret = util.consumeItems(userId, _consume, "BI_NFISH_BUY_ITEM_CONSUME",
                                         pokerconf.productIdToNumber(productId),
                                         param01=productId)
                vip_system.addUserVipExp(config.FISH_GAMEID, userId, abs(price) * 10,
                                         "BUY_PRODUCT", pokerconf.productIdToNumber(productId),
                                         productId, rmbs=abs(price))
                if _ret:
                    isSucc = True
                else:
                    code = 2
            else:
                isSucc = True
        elif buyType == config.BT_DIRECT or config.isThirdBuyType(buyType):
            isSucc = True
        elif buyType == config.BT_DIAMOND:
            price = product.get("price_diamond", 0)
            price, _ret = store.getUseRebateItemPrice(userId, itemId, price, buyType, productId,
                                                        clientId)  # 满减券之后的钻石 满减券
            if price > 0:
                consumeCount = 0
                if _ret:
                    store.autoConvertVoucherToDiamond(userId, price)  # 代购券
                    consumeCount, final = userchip.incrDiamond(userId, FISH_GAMEID, -abs(price), 0,
                                                                "BI_NFISH_BUY_ITEM_CONSUME", int(config.DIAMOND_KINDID),
                                                               util.getClientId(userId), param01=productId)
                if not _ret or abs(consumeCount) != price:
                    code = 2
                else:
                    isSucc = True
        if isSucc:
            piggyBankData[GameData.pb_enable] = 1
            # piggyBankData[GameData.pb_saveMoneyTS] = ts
            piggyBankData[GameData.pb_getMoneyTS] = 0
            # piggyBankData[GameData.pb_moneyCount] = conf.get("initVal", 0)
            pb_buyTimes = weakdata.incrDayFishData(userId, "pb_buyTimes", 1)
            # piggyBankData[GameData.pb_buyTimes] = piggyBankData.get(GameData.pb_buyTimes, 0) + 1
            daobase.executeUserCmd(userId, "HSET", key, type, json.dumps(piggyBankData))
            code, rewards = getMoney(userId, clientId, productId)

    mo = MsgPack()
    mo.setCmd("piggyBankBuy")
    mo.setResult("gameId", config.FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("productId", productId)
    mo.setResult("code", code)
    if code == 0:
        util.addProductBuyEvent(userId, productId, clientId)
        mo.setResult("reward", rewards)
    router.sendToUser(mo, userId)
    vipLevel = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
    ftlog.debug("piggy_bank, userId =", userId, "vip =", vipLevel, "type =", type, "code =", code,
                "piggyBankData =", piggyBankData, util.timestampToStr(ts), product)

    getPiggyBankInfo(userId, clientId)


def _triggerUserVipChange(event):
    ftlog.info("_triggerUserVipChange", event.userId)
    saveMoneyToPiggyBank(event.userId, util.getClientId(event.userId))


def _triggerGameTimeEvent(event):
    userId = event.userId
    ftlog.debug("piggy_bank, userId =", userId)
    vipLevel = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
    clientId = util.getClientId(userId)
    conf = config.getPiggyBankConf(clientId, vipLevel)
    for k, v in conf.iteritems():
        addCount = v.get("inroom", 0)
        if addCount > 0:
            addMoneyToPiggyBank(userId, clientId, k, addCount)


def fireCostChip(userId, clientId, vipLevel, chip):
    """
    存入开火消耗
    """
    ftlog.debug("piggy_bank, userId =", userId, "vip =", vipLevel, "chip =", chip)
    conf = config.getPiggyBankConf(clientId, vipLevel)
    for k, v in conf.iteritems():
        addCount = chip * v.get("firePct", 0)
        if addCount > 0:
            addMoneyToPiggyBank(userId, clientId, k, addCount)


def LossCoin(userId, clientId, vipLevel, coin):
    """
    存入亏损值
    """
    ftlog.debug("piggy_bank, userId =", userId, "vip =", vipLevel, "coin =", coin)
    conf = config.getPiggyBankConf(clientId, vipLevel)
    for k, v in conf.iteritems():
        addCount = coin * v.get("profitPct", 0)
        if addCount > 0:
            addMoneyToPiggyBank(userId, clientId, k, addCount)


def _triggerFireEvent(event):
    pass
    # if util.getRoomTypeName(event.roomId) not in config.NORMAL_ROOM_TYPE:
    #     return
    # userId = event.userId
    # clientId = util.getClientId(userId)
    # ftlog.debug("piggy_bank, userId =", userId, "costChip =", event.costChip)
    # vipLevel = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
    # fireCostChip(userId, clientId, vipLevel, event.costChip)


def _triggerUseSkillEvent(event):
    if util.getRoomTypeName(event.roomId) not in config.NORMAL_ROOM_TYPE:
        return
    userId = event.userId
    clientId = util.getClientId(userId)
    ftlog.debug("piggy_bank, userId =", userId, "chip =", event.chip)
    vipLevel = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
    fireCostChip(userId, clientId, vipLevel, event.chip)


def _triggerUserLoginEvent(event):
    userId = event.userId
    ftlog.debug("piggy_bank, userId =", userId)
    saveMoneyToPiggyBank(userId, event.clientId)


def _triggerChargeNotifyEvent(event):
    """
    充值发货事件
    """
    ftlog.info("piggy_bank._triggerChargeNotifyEvent->",
               "userId =", event.userId,
               "gameId =", event.gameId,
               "rmbs =", event.rmbs,
               "productId =", event.productId,
               "clientId =", event.clientId,
               "isAddVipExp", getattr(event, "isAddVipExp", False))

    productId = event.productId
    if config.getPiggyBankProduct(event.clientId, productId):
        userId = event.userId
        buyPiggyBank(userId, event.clientId, productId)


_inited = False


def initialize():
    ftlog.debug("newfish piggy_bank initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from poker.entity.events.tyevent import ChargeNotifyEvent, EventUserLogin
        from hall.entity.hallvip import TYUserVipLevelUpEvent
        from newfish.entity.event import GameTimeEvent, FireEvent, UseSkillEvent, NFChargeNotifyEvent
        from hall.game import TGHall
        TGHall.getEventBus().subscribe(TYUserVipLevelUpEvent, _triggerUserVipChange)
        from newfish.game import TGFish
        TGFish.getEventBus().subscribe(GameTimeEvent, _triggerGameTimeEvent)
        # TGFish.getEventBus().subscribe(FireEvent, _triggerFireEvent)
        TGFish.getEventBus().subscribe(UseSkillEvent, _triggerUseSkillEvent)
        TGHall.getEventBus().subscribe(ChargeNotifyEvent, _triggerChargeNotifyEvent)
        TGFish.getEventBus().subscribe(NFChargeNotifyEvent, _triggerChargeNotifyEvent)
        TGFish.getEventBus().subscribe(EventUserLogin, _triggerUserLoginEvent)
    ftlog.debug("newfish piggy_bank initialize end")