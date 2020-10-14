# -*- coding=utf-8 -*-
"""
超级boss玩法
"""
# @Author  : Kangxiaopeng
# @Time    : 2020/4/2


import json
import random
import time

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.dao import userchip, userdata, gamedata, daobase
from newfish.entity.config import FISH_GAMEID
from newfish.entity.ranking.ranking_base import RankType
from newfish.entity import util, config, weakdata, module_tip
from newfish.entity.redis_keys import MixData


def sendGameplayInfo(roomId, userId, clientId, mode):
    """
    发送玩法相关信息
    """
    bigRoomId, _ = util.getBigRoomId(roomId)
    key = "%s_%d" % (bigRoomId, mode)
    lang = util.getLanguage(userId, clientId)
    conf = config.getSuperBossCommonConf()
    tabs = conf.get(str(key), {}).get("tabs", [])
    tabs = [{"title": config.getMultiLangTextConf(v["title"], lang=lang), "data": v["data"], "param": v.get("param", 0)} for v in tabs]
    mo = MsgPack()
    mo.setCmd("superboss_gameplay_info")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("roomId", roomId)
    mo.setResult("mode", mode)
    mo.setResult("tabs", tabs)
    router.sendToUser(mo, userId)
    checkModuleTip(bigRoomId, userId, mode)
    if ftlog.is_debug():
        ftlog.debug("gameplay, userId =", userId, "mo =", mo)


def _getSuperbossKey():
    """
    竞赛活动存档主key: key_44
    """
    return MixData.superbossBonus % FISH_GAMEID


def incrCompBonusPool(bigRoomId, mode, pool, ts=None):
    """
    增加超级boss奖池
    """
    return 0
    ts = ts or int(time.time())
    dayStartTS = util.getDayStartTimestamp(ts)
    subKey = "%d_%s" % (dayStartTS, (MixData.superbossBonuspool % bigRoomId))
    if mode == 1:
        subKey = "%d_%s" % (dayStartTS, (MixData.superbossBonusRingpool % bigRoomId))
    if pool:
        bonusPool = daobase.executeMixCmd("HINCRBY", _getSuperbossKey(), subKey, pool)
    else:
        bonusPool = daobase.executeMixCmd("HGET", _getSuperbossKey(), subKey)

    if ftlog.is_debug():
        ftlog.debug("gameplay, bonusPool =", bonusPool, "key =", subKey)
    return bonusPool


def getSuperbossBonusPool(bigRoomId, mode, ts=None):
    """
    获取超级boss奖池
    """
    return 0
    if not bigRoomId:
        ftlog.error("gameplay, bigRoomId error !", bigRoomId, ts)
        return 0
    ts = ts or int(time.time())
    dayStartTS = util.getDayStartTimestamp(ts)
    subKey = "%d_%s" % (dayStartTS, MixData.superbossBonuspool % bigRoomId)
    if mode == 1:
        subKey = "%d_%s" % (dayStartTS, (MixData.superbossBonusRingpool % bigRoomId))
    # 获取指定时间的奖池
    bonusPool = daobase.executeMixCmd("HGET", _getSuperbossKey(), subKey)
    # 当奖池为空时（首次开启奖池）添加初始奖池,后续每天的初始奖池从前一天的房间奖池中划分一部分.
    if bonusPool is None:
        bonusPool = 100000
        daobase.executeMixCmd("HSET", _getSuperbossKey(), subKey, bonusPool)
    if ftlog.is_debug():
        ftlog.debug("gameplay, bonusPool =", bonusPool, "key =", subKey)
    return bonusPool


def removeExpiredData(bigRoomId):
    """
    去除过期的存档数据
    """
    curDayStartTS = util.getDayStartTimestamp(int(time.time()))
    # subKey = (MixData.superbossBonuspool % bigRoomId)
    datas = daobase.executeMixCmd("HGETALL", _getSuperbossKey())
    delKeys = []
    for key in datas[0::2]:
        val = key.split('_')
        if len(val) == 2 and int(val[0]) < curDayStartTS - 2 * 86400 and (val[1] == (MixData.superbossBonuspool % bigRoomId) or val[1] == (MixData.superbossBonuspool % bigRoomId)):
            delKeys.append(key)
    for key in delKeys:
        daobase.executeMixCmd("HDEL", _getSuperbossKey(), key)


def checkModuleTip(bigRoomId, userId, mode):
    """
    检查兑换和小游戏红点状态
    """
    from newfish.entity.superboss import item_exchange, minigame
    module_tip.resetModuleTipEvent(userId, "superboss")
    subkey = "%s_%d" % (bigRoomId, mode)
    mgType = config.getSuperBossCommonConf().get(str(subkey), {}).get("mgType", "")
    item_exchange.checkModuleTip(mgType, userId, mode)
    minigame.checkModuleTip(bigRoomId, userId, mode)