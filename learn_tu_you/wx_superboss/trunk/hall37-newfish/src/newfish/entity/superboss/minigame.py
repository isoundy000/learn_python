# -*- coding=utf-8 -*-
"""
选宝箱玩法
"""
# @Author  : Kangxiaopeng
# @Time    : 2020/4/1

import json
import random

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from hall.entity import hallvip
from newfish.entity.msg import GameMsg
from newfish.entity.config import FISH_GAMEID
from newfish.entity import util, config, weakdata, module_tip
from newfish.entity.redis_keys import WeakData, GameData
from newfish.entity.util import getGunLevelVal
from newfish.entity.event import PlayMiniGame
from newfish.servers.table.rpc import table_remote

# 小游戏类型.
MINIGAME_TYPE_LIST = ["box", "octopus", "queen", "dragon"]


def sendMinigameInfo(roomId, userId, mode):
    """
    发送小游戏信息
    """
    bigRoomId, _ = util.getBigRoomId(roomId)
    subkey = "%s_%d" % (bigRoomId, mode)
    mgType = config.getSuperBossCommonConf().get(str(subkey), {}).get("mgType", "")
    key = "%s_%d" % (mgType, mode)
    mo = MsgPack()
    mo.setCmd("superboss_minigame_info")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("roomId", roomId)
    mo.setResult("mode", mode)
    mo.setResult("type", mgType)
    data = {}
    if mgType in MINIGAME_TYPE_LIST:
        conf = config.getSuperBossMiniGameConf()
        superbossPlayedTimes = weakdata.getDayFishData(userId, WeakData.superbossMGPlayedTimes, {})
        playedTimes = superbossPlayedTimes.get(key, 0)
        vipLevel = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
        maxTimesList = conf.get("info", {}).get(key, {}).get("maxTimes", [])
        maxTimes = maxTimesList[vipLevel] if maxTimesList and len(maxTimesList) > vipLevel else 0
        remainTimes = max(0, maxTimes - playedTimes) if maxTimes >= 0 else -1
        currencyList = conf.get("info", {}).get(key, {}).get("currencyList", [])
        items = config.rwcopy(conf.get("game", {}).get(key, []))
        gunLevelVal = getGunLevelVal(userId, 1)
        lang = util.getLanguage(userId)
        itemsinfo = []
        for item in items:
            if gunLevelVal >= item["level"]:
                item["des"] = config.getMultiLangTextConf(item["des"], lang=lang) if item["des"] else ""
                itemsinfo.append(item)
        if mgType == "box":
            for iteminfo in itemsinfo:
                rewards = iteminfo["rewards"]
                groupIdx = util.selectIdxByWeight([int(reward.keys()[0]) for reward in rewards])
                iteminfo["rewards"] = rewards[groupIdx].values()[0]
                iteminfo["groupIdx"] = groupIdx
        mo.setResult("showItemsList", currencyList)
        data = {"remainTimes": remainTimes, "items": itemsinfo}
    else:
        ftlog.warn("minigame, type error, userId =", userId, "roomId =", roomId, "mode =", mode, "mgType =", mgType)
    mo.setResult("data", data)
    router.sendToUser(mo, userId)
    if ftlog.is_debug():
        ftlog.debug("minigame, userId =", userId, "mode =", mode, "mo =", mo)


def playMinigameShow(roomId, userId, idx, mode, userIds):
    """
    巨龙转盘展示盘面
    """
    bigRoomId, _ = util.getBigRoomId(roomId)
    subkey = "%s_%d" % (bigRoomId, mode)
    mgType = config.getSuperBossCommonConf().get(str(subkey), {}).get("mgType", "")
    key = "%s_%d" % (mgType, mode)
    mo = MsgPack()
    mo.setCmd("superboss_minigame_show")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("roomId", roomId)
    mo.setResult("mode", mode)
    mo.setResult("idx", idx)
    mo.setResult("type", mgType)
    data = {}
    code = 1
    gainItems = []
    if mgType == "dragon":
        superbossPlayedTimes = weakdata.getDayFishData(userId, WeakData.superbossMGPlayedTimes, {})
        playedTimes = superbossPlayedTimes.setdefault(key, 0)
        conf = config.getSuperBossMiniGameConf()
        vipLevel = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
        maxTimesList = conf.get("info", {}).get(key, {}).get("maxTimes", [])
        isCanPlay = True
        items = conf.get("game", {}).get(key, [])
        maxTimes = maxTimesList[vipLevel] if maxTimesList and len(maxTimesList) > vipLevel else 0
        if 0 <= idx < len(items) and (maxTimes == -1 or maxTimes > playedTimes) and isCanPlay:
            costItems = items[idx]["costs"]
            gainItems = items[idx]["rewards"]
            for _val in costItems:
                if util.balanceItem(userId, _val["name"]) < _val["count"]:
                    code = 2
                    break
            else:
                code = 0
        turntable_rewards = []
        if code == 0:
            for gainItem in gainItems:
                for key in gainItem.keys():
                    if key == "count":
                        turntable_rewards.append(gainItem[key])
            data["turntable_rewards"] = turntable_rewards
            mo.setResult("data", data)
    mo.setResult("code", code)
    userIds.append(userId)
    GameMsg.sendMsg(mo, userIds)


def playMinigame(roomId, userId, idx, mode, userIds, groupIdx):
    """
    点击小游戏
    """
    bigRoomId, _ = util.getBigRoomId(roomId)
    subkey = "%s_%d" % (bigRoomId, mode)
    mgType = config.getSuperBossCommonConf().get(str(subkey), {}).get("mgType", "")
    key = "%s_%d" % (mgType, mode)
    mo = MsgPack()
    mo.setCmd("superboss_minigame")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("roomId", roomId)
    mo.setResult("mode", mode)
    mo.setResult("idx", idx)
    mo.setResult("type", mgType)
    code = 1
    data = {}
    gainItems =[]
    if mgType in MINIGAME_TYPE_LIST:
        superbossPlayedTimes = weakdata.getDayFishData(userId, WeakData.superbossMGPlayedTimes, {})
        playedTimes = superbossPlayedTimes.setdefault(key, 0)
        conf = config.getSuperBossMiniGameConf()
        vipLevel = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
        maxTimesList = conf.get("info", {}).get(key, {}).get("maxTimes", [])
        maxTimes = maxTimesList[vipLevel] if maxTimesList and len(maxTimesList) > vipLevel else 0
        items = conf.get("game", {}).get(key, [])
        rewards = []
        _idx = 0
        isCanPlay = True
        # 只能抽取满足消耗的最高等级抽奖.
        # if mgType == "queen":
        #     # 抽奖消耗由多到少配置。
        #     for _idx, _val in enumerate(itemsinfo):
        #         # 检查消耗是否满足条件
        #         for v in _val["costs"]:
        #             if util.balanceItem(userId, v["name"]) < v["count"]:
        #                 break
        #         else:
        #             isCanPlay = (idx == _idx)
        #             break
        if 0 <= idx < len(items) and (maxTimes == -1 or maxTimes > playedTimes) and isCanPlay:
            costItems = items[idx]["costs"]
            if mgType == "box":
                gainItems = items[idx]["rewards"][groupIdx].values()[0]
            else:
                gainItems = items[idx]["rewards"]
            for _val in costItems:
                if util.balanceItem(userId, _val["name"]) < _val["count"]:
                    code = 2
                    break
            else:
                _ret = util.consumeItems(userId, costItems, "BI_NFISH_SUPERBOSS_EXCHANGE", bigRoomId, mode)
                if not _ret:
                    code = 2
                else:
                    superbossPlayedTimes[key] += 1
                    weakdata.setDayFishData(userId, WeakData.superbossMGPlayedTimes, json.dumps(superbossPlayedTimes))
                    _idx = util.selectIdxByWeight([v["probb"] for v in gainItems])
                    if _idx >= 0:
                        rewards = [{"name": gainItems[_idx]["name"], "count": gainItems[_idx]["count"]}]
                        isIn, roomId, tableId, _ = util.isInFishTable(userId)
                        if isIn:
                            code = table_remote.addRewardsToTable(roomId, tableId, userId, rewards, "BI_NFISH_SUPERBOSS_BOX", mode)
                        else:
                            code = util.addRewards(userId, rewards, "BI_NFISH_SUPERBOSS_BOX", bigRoomId, mode)
                        if code != 0:
                            ftlog.error("minigame, userId =", userId, "bigRoomId =", key, "idx =", idx, "rewards =", rewards)
            playedTimes = superbossPlayedTimes.get(key, 0)
            remainTimes = max(0, maxTimes - playedTimes) if maxTimes >= 0 else -1
            data = {"remainTimes": remainTimes, "rewards": rewards, "rewardIndex": _idx}
    else:
        ftlog.warn("minigame, type error, userId =", userId, "roomId =", roomId, "mode =", mode, "idx =", idx, "mgType =", mgType)
    mo.setResult("code", code)
    turntable_rewards = []
    if mgType == "dragon":
        for gainItem in gainItems:
            for key in gainItem.keys():
                if key == "count":
                    turntable_rewards.append(gainItem[key])
        data["turntable_rewards"] = turntable_rewards
    mo.setResult("data", data)
    router.sendToUser(mo, userId)
    if mgType == "dragon" and code == 0:
        userIds = userIds
        GameMsg.sendMsg(mo, userIds)
    if code == 0:
        from newfish.game import TGFish
        event = PlayMiniGame(userId, config.FISH_GAMEID)
        TGFish.getEventBus().publishEvent(event)
    checkModuleTip(bigRoomId, userId, mode)


def checkModuleTip(bigRoomId, userId, mode):
    """
    检查是否可以玩小游戏
    """
    subkey = "%s_%d" % (bigRoomId, mode)
    mgType = config.getSuperBossCommonConf().get(str(subkey), {}).get("mgType", "")
    key = "%s_%d" % (mgType, mode)
    isCanPlay = False
    if mgType in MINIGAME_TYPE_LIST:
        conf = config.getSuperBossMiniGameConf()
        superbossPlayedTimes = weakdata.getDayFishData(userId, WeakData.superbossMGPlayedTimes, {})
        playedTimes = superbossPlayedTimes.get(key, 0)
        vipLevel = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
        maxTimesList = conf.get("info", {}).get(key, {}).get("maxTimes", [])
        maxTimes = maxTimesList[vipLevel] if maxTimesList and len(maxTimesList) > vipLevel else 0
        remainTimes = max(0, maxTimes - playedTimes) if maxTimes >= 0 else -1
        items = conf.get("items", {}).get(key, [])
        isCanPlay = False
        if remainTimes == -1 or remainTimes > 0:
            for _item in items:
                for _val in _item.get("costs"):
                    if util.balanceItem(userId, _val["name"]) < _val["count"]:
                        break
                else:
                    isCanPlay = True
                    break
    tipKey = "minigame"
    if isCanPlay:
        module_tip.addModuleTipEvent(userId, "superboss", tipKey)
    if ftlog.is_debug():
        ftlog.debug("minigame, userId =", userId, "tipKey =", tipKey, isCanPlay, "key =", key)