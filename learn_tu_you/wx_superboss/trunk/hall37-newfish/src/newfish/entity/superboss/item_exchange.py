# -*- coding=utf-8 -*-
"""
超级boss兑换功能
"""
# @Author  : Kangxiaopeng
# @Time    : 2019/11/22


import json
import random
import time
import copy

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from newfish.entity.config import FISH_GAMEID
from newfish.entity.ranking.ranking_base import RankType
from newfish.entity import util, config, weakdata, module_tip
from newfish.entity.redis_keys import WeakData
from newfish.entity.event import MiniGameBossExchange
from poker.entity.biz import bireport


def _getExchangeData(userId, mgType, mode=-1):
    """
    获取兑换数据
    """
    conf = config.getSuperBossExchangeConf()
    superbossExchangedTimes = weakdata.getDayFishData(userId, WeakData.superbossExchangedTimes, {})
    showItemsList = []
    exchangeItems = []
    # 0金币模式, 1金环模式.
    for _mode in [config.GOLD_COIN, config.GOLD_RING]:
        if mode != -1 and mode != _mode:
            continue
        # TODO.还需要判断相应模式是否已经解锁
        isLocked = False
        if isLocked:
            continue
        key = "%s_%d" % (mgType, _mode)
        exchangedTimes = superbossExchangedTimes.get(key, {})
        showItemsList.extend(conf.get("info", {}).get(key, {}).get("currencyList", []))
        for idx, val in enumerate(conf.get("exchange", {}).get(key, {}).get("exchangeItems", [])):
            remainTimes = val["exchangeTimes"]
            remainTimes = max(0, remainTimes - exchangedTimes.get(str(val["idx"]), 0)) if remainTimes >= 0 else remainTimes
            exchangeItems.append({"costItems": val["costItems"], "gainItems": val["gainItems"], "remainTimes": remainTimes, "mode": _mode, "idx": val["idx"]})
    return list(set(showItemsList)), exchangeItems


def sendConvertInfo(roomId, userId, mode):
    """
    发送兑换信息
    """
    bigRoomId, _ = util.getBigRoomId(roomId)
    key = "%s_%d" % (bigRoomId, mode)
    mgType = config.getSuperBossCommonConf().get(str(key), {}).get("mgType", "")
    mo = MsgPack()
    mo.setCmd("superboss_convert_info")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("roomId", roomId)
    mo.setResult("mode", mode)
    showItemsList, exchangeItems = _getExchangeData(userId, mgType, mode)
    mo.setResult("showItemsList", showItemsList)
    mo.setResult("convertItems", exchangeItems)
    router.sendToUser(mo, userId)


def sendStoreConvertInfo(userId, mgType):
    """
    从商城获取超级boss兑换数据
    """
    mo = MsgPack()
    mo.setCmd("store_superboss_convert_info")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("mgType", mgType)
    showItemsList, exchangeItems = _getExchangeData(userId, mgType)
    mo.setResult("showItemsList", showItemsList)
    mo.setResult("convertItems", exchangeItems)
    router.sendToUser(mo, userId)


def _exchange(userId, mgType, mode, idx, count):
    """
    兑换逻辑, 通过mgType+mode+idx可以唯一确定兑换数据.
    """
    code = 1
    key = "%s_%d" % (mgType, mode)
    exchangedTimes = weakdata.getDayFishData(userId, WeakData.superbossExchangedTimes, {})
    exchangedTimes.setdefault(key, {})
    conf = config.getSuperBossExchangeConf("exchange").get(key, {})
    rewards = []
    reList = ""
    costList = ""
    lang = util.getLanguage(userId)
    info = config.getMultiLangTextConf("ID_EXCHANGE_ERR_INFO_8", lang=lang)
    # 根据兑换类型找到bigRoomId,用于bi事件参数.
    bigRoomId = 0
    for _bigRoomId, val in config.getSuperBossCommonConf().iteritems():
        if val["mgType"] == mgType:
            bigRoomId = int(str(_bigRoomId)[0:5])
            break
    for _exchangeItem in conf.get("exchangeItems", []):
        _id = _exchangeItem["idx"]
        if _id != idx:
            continue
        remainTimes = _exchangeItem["exchangeTimes"]
        remainTimes = max(0, remainTimes - exchangedTimes[key].get(str(_id), 0)) if remainTimes >= 0 else remainTimes
        if not (count >= 1 and (remainTimes == -1 or remainTimes >= count)):
            continue
        costItems = _exchangeItem.get("costItems", [])
        gainItems = _exchangeItem.get("gainItems", [])
        for _val in costItems:
            _val["count"] *= count
            kindName = config.getMultiLangTextConf("ID_CONFIG_KINDID_ITEM:%s" % _val["name"], lang=lang)
            costDes = kindName + "x" + str(_val["count"])
            costList = costList + costDes + " "
            if util.balanceItem(userId, _val["name"]) < _val["count"]:
                code = 2
                break
        _ret = util.consumeItems(userId, costItems, "BI_NFISH_SUPERBOSS_EXCHANGE", bigRoomId, mode)
        if not _ret:
            code = 2
        else:
            code = 0
            if remainTimes > 0:
                exchangedTimes[key][str(_id)] = exchangedTimes[key].setdefault(str(_id), 0) + count
                weakdata.setDayFishData(userId, WeakData.superbossExchangedTimes, json.dumps(exchangedTimes))
            reDict = {}
            for i in range(count):
                for val in gainItems:
                    if val.get("minCount", 0) and val.get("maxCount", 0):
                        reDict.setdefault(val["name"], 0)
                        reDict[val["name"]] += random.randint(val["minCount"], val["maxCount"])
            for k, v in reDict.iteritems():
                rewards.append({"name": k, "count": v})
                if k == config.CHIP_KINDID:
                    kindName = config.getMultiLangTextConf("ID_CONFIG_KINDID_USER:CHIP", lang=lang)
                else:
                    kindName = config.getMultiLangTextConf("ID_CONFIG_KINDID_ITEM:%s" % k, lang=lang)
                reDes = kindName + "x" + str(v)
                reList = reList + reDes + " "
            if util.addRewards(userId, rewards, "BI_NFISH_SUPERBOSS_EXCHANGE", bigRoomId, mode) != 0:
                ftlog.error("item_exchange, userId =", userId, "bigRoomId =", bigRoomId, "mode =", mode,
                                "idx =", idx, "count =", count, "rewards =", rewards, "key =", key)
    if code == 0:
        bireport.reportGameEvent("BI_NFISH_GE_ITEM_EXCHANGE", userId, FISH_GAMEID, 0, 0, 0, 0, 0, 0, [userId, mgType, mode, idx], util.getClientId(userId))
        from newfish.game import TGFish
        event = MiniGameBossExchange(userId, config.FISH_GAMEID, count)
        TGFish.getEventBus().publishEvent(event)
        info = config.getMultiLangTextConf("ID_EXCHANGE_RESULT_INFO_1", lang=lang).format(time.strftime("%X", time.localtime()), reList, costList)
    return code, rewards, info


def convertItem(roomId, idx, count, userId, mode):
    """
    兑换
    """
    bigRoomId, _ = util.getBigRoomId(roomId)
    key = "%s_%d" % (bigRoomId, mode)
    mgType = config.getSuperBossCommonConf().get(str(key), {}).get("mgType", "")
    code, rewards, info = _exchange(userId, mgType, mode, idx, count)
    mo = MsgPack()
    mo.setCmd("superboss_convert")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("roomId", roomId)
    mo.setResult("code", code)
    mo.setResult("idx", idx)
    mo.setResult("mode", mode)
    mo.setResult("count", count)
    mo.setResult("info", info)
    mo.setResult("rewards", rewards)
    router.sendToUser(mo, userId)
    if code == 0:
        sendConvertInfo(roomId, userId, mode)
        mgType = config.getSuperBossCommonConf().get(str(key), {}).get("mgType", "")
        checkModuleTip(mgType, userId, mode)


def storeConvertItem(userId, mgType, mode, idx, count):
    """
    在商城中兑换
    """
    code, rewards, info = _exchange(userId, mgType, mode, idx, count)
    mo = MsgPack()
    mo.setCmd("store_superboss_convert")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("mgType", mgType)
    mo.setResult("code", code)
    mo.setResult("idx", idx)
    mo.setResult("mode", mode)
    mo.setResult("count", count)
    mo.setResult("info", info)
    mo.setResult("rewards", rewards)
    router.sendToUser(mo, userId)
    if code == 0:
        sendStoreConvertInfo(userId, mgType)
        checkModuleTip(mgType, userId, mode)


def _isExchangeChance(userId, remainTimes, costItems):
    """
    判断是否存在兑换机会，兑换材料和次数是否充足
    """
    isTimeEnough = remainTimes == -1 or remainTimes > 0
    if not isTimeEnough:
        return False
    isItemEnough = False
    for _val in costItems:
        if util.balanceItem(userId, _val["name"]) < _val["count"]:
            break
    else:
        isItemEnough = True
    return isItemEnough


def checkModuleTip(mgType, userId, mode):
    """
    检查是否可以兑换
    """
    key = "%s_%d" % (mgType, mode)
    exchangedTimes = weakdata.getDayFishData(userId, WeakData.superbossExchangedTimes, {})
    exchangedTimes = exchangedTimes.get(key, {})
    conf = config.getSuperBossExchangeConf()
    exchangeItems = []
    isCanExchanged = False
    for idx, val in enumerate(conf.get("exchange", {}).get(key, {}).get("exchangeItems", [])):
        remainTimes = val["exchangeTimes"]
        remainTimes = max(0, remainTimes - exchangedTimes.get(str(val["idx"]), 0)) if remainTimes >= 0 else remainTimes
        exchangeItems.append({"costItems": val["costItems"], "gainItems": val["gainItems"], "remainTimes": remainTimes})
        if not isCanExchanged and _isExchangeChance(userId, remainTimes, val["costItems"]):
            isCanExchanged = True
    tipKey = "convert"
    if isCanExchanged:
        module_tip.addModuleTipEvent(userId, "superboss", tipKey)