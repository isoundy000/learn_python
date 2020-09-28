# -*- coding=utf-8 -*-
"""
Created by hhx on 17/8/14.
"""

import random
import time

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.dao import gamedata
from hall.entity import hallvip, hallitem, datachangenotify
from newfish.entity import util, config
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData


Bonus_Consum = {1: {"name": 3106, "count": 200}, 5: {"name": 3106, "count": 960}}
LuckyAdd = 16


# 获取抽奖结果
def _getBonusResult(userId, count):
    acConfig = config.getActivityConfigById("activity_starfishGame_20170817")
    userVip = int(hallvip.userVipSystem.getUserVip(userId).vipLevel.level)
    if not acConfig or acConfig.get("limitVip", 1) > userVip:
        return 1, [], None
    luckyNum = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.wishLuckyValue)
    configInfo = config.getStarfishBonusConf()

    resultIndex = []
    code = 0

    # 海星消耗
    consumeItem = Bonus_Consum[1]
    if Bonus_Consum.has_key(count):
        consumeItem = Bonus_Consum[count]
    else:
        consumeItem["count"] = consumeItem["count"]*count

    # 用户减海星
    curTime = int(time.time())
    userAssets = hallitem.itemSystem.loadUserAssets(userId)
    _, consumeCount, final = userAssets.consumeAsset(FISH_GAMEID, "item:" + str(consumeItem["name"]), int(consumeItem["count"]), curTime, "ITEM_USE", 0)
    if consumeCount != consumeItem["count"]:  # 海星不够
        code = 1
        return code, None, None

    # 计算抽取结果
    for index in range(count):
        code, index, itemId, clearLucky = _getOnceResult(userId, luckyNum, configInfo)
        if code != 0:
            break
        elif clearLucky:
            luckyNum = 0
        else:
            luckyNum = luckyNum + 1
        resultIndex.append(index)
    gamedata.setGameAttr(userId, FISH_GAMEID, GameData.wishLuckyValue, luckyNum)
    # 更新道具个数
    datachangenotify.sendDataChangeNotify(FISH_GAMEID, userId, ["item"])
    return code, resultIndex, luckyNum


def _testResult10000():
    luckyNum = 0
    configInfo = config.getStarfishBonusConf()
    itemInfo = [{"count": 0, "luckyIndex": []}, {"count": 0, "luckyIndex": []}, {"count": 0, "luckyIndex": []},
                {"count": 0, "luckyIndex": []}, {"count": 0, "luckyIndex": []},
                {"count": 0, "luckyIndex": []}, {"count": 0, "luckyIndex": []},
                {"count": 0, "luckyIndex": []}, {"count": 0, "luckyIndex": []},
                {"count": 0, "luckyIndex": []}]
    chipValueArray = [3000000, 500000, 200000, 250000, 90000, 300000, 100000, 40000, 8888, 8888]
    totalChip = 0
    for index in range(10000):
        _, index, itemId, clearLucky = _getOnceResult(None, luckyNum, configInfo)
        luckyArray = itemInfo[index]["luckyIndex"]
        luckyArray.append(luckyNum + 1)
        itemInfo[index] = {"count": itemInfo[index]["count"]+1, "luckyIndex": luckyArray}
        totalChip = totalChip + chipValueArray[index]
        if clearLucky:
            luckyNum = 0
        else:
            luckyNum = luckyNum + 1
    for index in range(10):
        totalNum = sum(itemInfo[index]["luckyIndex"])
        totalNum = totalNum/len(itemInfo[index]["luckyIndex"])
        itemInfo[index]["Average"] = totalNum


# 获取一次抽奖结果
def _getOnceResult(userId, luckyNum, configInfo):
    itemTotalWeight = int(sum([dict(rewardInfo)["weight"] for rewardInfo in configInfo if rewardInfo]) + luckyNum / LuckyAdd)
    code = 0
    if itemTotalWeight > 0:
        itemWeight = random.randint(1, itemTotalWeight)
        for j, rewardInfo in enumerate(configInfo):
            _weight = rewardInfo["weight"]
            if rewardInfo["Id"] == 1:     # 微信红包权重增加
                _weight = _weight + luckyNum / LuckyAdd
            if rewardInfo and itemWeight - _weight <= 0:
                if userId:
                    code = util.addRewards(userId, rewardInfo["rewards"], "BI_NFISH_WISH_REWARDS")
                return code, j, rewardInfo["rewards"][0]["name"], rewardInfo["clearLucky"]
            itemWeight -= _weight
    return code, -1, 0


def _getBonusGameInfo():
    rewardInfos = []
    configInfo = config.getStarfishBonusConf()
    for rewardInfo in configInfo:
        rewardInfos.append(rewardInfo["rewards"])
    rewardDetails = _buildRewards(rewardInfos)
    return rewardDetails


def _buildRewards(rewardList):
    rewards = []
    for r in rewardList:
        r = r[0]
        rewardId = "item:" + str(r["name"])
        if r["name"] == config.COUPON_KINDID:
            rewardId = "user:coupon"
        elif r["name"] == config.CHIP_KINDID:
            rewardId = "user:chip"
        assetKind = hallitem.itemSystem.findAssetKind(rewardId)
        if r["count"] > 0 and assetKind:
            rewards.append({
                "name": assetKind.displayName,
                "kindId": assetKind.kindId,
                "count": r["count"],
                "unit": assetKind.units,
                "desc": assetKind.displayName + "x" + str(r["count"]) + assetKind.units,
                "img": assetKind.pic,
                "rare": r["rare"]
            })
    ftlog.debug("_buildRewards", rewards)
    return rewards


# 获取游戏结果
def doGetBonusResult(userId, count):
    message = MsgPack()
    message.setCmd("fishStarGameResult")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    code_, rewards, luckyNum = _getBonusResult(userId, count)
    message.setResult("code", code_)
    if code_ == 0:
        message.setResult("gameResult", rewards)
        message.setResult("starBonusNum", luckyNum)
    router.sendToUser(message, userId)


# 获取游戏数据
def doGetBonusInfo(userId):
    message = MsgPack()
    message.setCmd("fishStarGameInfo")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    message.setResult("code", 0)
    wishLuckyValue = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.wishLuckyValue)
    gamedata.setGameAttr(userId, FISH_GAMEID, GameData.wishLuckyValue, wishLuckyValue)
    message.setResult("starBonusNum", wishLuckyValue)
    message.setResult("gameInfo", _getBonusGameInfo())
    message.setResult("consumInfo", Bonus_Consum)
    router.sendToUser(message, userId)