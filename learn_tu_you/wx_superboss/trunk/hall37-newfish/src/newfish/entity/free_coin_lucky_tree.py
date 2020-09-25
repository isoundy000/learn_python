# -*- coding: utf-8 -*-
"""
Created by zhanglin on：2020-04-09
免费金币摇钱树模块，玩家每隔一段时间可以领取奖励，看视频可以加速，但是最终领奖时还需要看视频
"""
import time
import json

from hall.entity import hallvip
from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.dao import daobase
from newfish.entity.chest import chest_system
from newfish.entity import config, util, weakdata
from newfish.entity.redis_keys import GameData, UserData
from newfish.entity.config import FISH_GAMEID

# copperCount:铜币数量，rewardTs:可领奖时间戳，
# luckyTreeData:44:s:s:107001 : {"copperCount": 100, "rewardTs": 1000010203, "skipAdTimes": 1}


def _getLuckyTreeKey(userId):
    """
    获取存储免费金币摇钱树数据的key
    """
    return UserData.luckyTreeData % (FISH_GAMEID, userId)


def sendLuckyTreeInfo(userId, clientId):
    """
    发送免费金币摇钱树详情
    """
    isAppClient = util.isAppClient(userId)                                          # 判断是否为单包客户端
    luckyTreeConf = config.getLuckyTreeConf()
    accelerateTimes, rewardTs, copperCount = getRewardTsAndCopperCount(userId)
    vipLevel = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
    vipLimit = luckyTreeConf.get("vipLimit")
    maxAcceleratetimes = luckyTreeConf.get("maxAcceleratetimes")
    state = 4
    if accelerateTimes < maxAcceleratetimes:
        if vipLevel >= vipLimit:
            state = 1
        else:
            state = 3 if isAppClient else 0
    else:
        state = 2
    message = MsgPack()
    message.setCmd("lucky_tree_info")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    message.setResult("rule", config.getMultiLangTextConf(str(luckyTreeConf.get("rule")), lang=util.getLanguage(userId, clientId)))
    message.setResult("copperCount", copperCount)
    message.setResult("state", state)
    message.setResult("rewardTs", rewardTs)
    message.setResult("rewardCount", luckyTreeConf.get("rewardCount", 0))
    message.setResult("rewardsList", getAllRewardList())
    router.sendToUser(message, userId)


def getRewardTsAndCopperCount(userId):
    """
    获取可领奖时间戳和铜币数量
    """
    curTime = int(time.time())
    luckyTreeData = getLuckyTreeData(userId)
    copperCount = luckyTreeData.get("copperCount", 0)
    accelerateTimes = weakdata.getDayFishData(userId, "accelerateTimes", 0)
    # 第一次玩家直接可领
    if not luckyTreeData:
        luckyTreeData["rewardTs"] = curTime
        luckyTreeData["copperCount"] = 0
        luckyTreeData["accelerate"] = 0
        saveLuckyTreeData(userId, luckyTreeData)
    return accelerateTimes, luckyTreeData["rewardTs"], copperCount


def getAllRewardList():
    """
    获取奖励列表，摇钱树界面左边显示的界面
    """
    temRewardList = []
    rewardListConf = config.getLuckyTreeConf("rewardList")
    for _val in rewardListConf:
        itemId = _val.get("reward", {}).get("name", 0)
        if util.isChestRewardId(itemId):
            chestReward = chest_system.getChestInfo(itemId)
            _val["reward"] = chestReward
        temRewardList.append(_val)
    return temRewardList


def getReward(userId):
    """
    领取铜币奖励
    """
    code = 0
    curTime = int(time.time())
    luckyTreeConf = config.getLuckyTreeConf()

    luckyTreeData = getLuckyTreeData(userId)
    if curTime < luckyTreeData["rewardTs"]:
        return 0, 1
    luckyTreeData["rewardTs"] = curTime + luckyTreeConf.get("interval", 3) * 3600
    rewardsCount = luckyTreeConf.get("rewardCount", 0)
    luckyTreeData["copperCount"] += rewardsCount
    saveLuckyTreeData(userId, luckyTreeData)
    return rewardsCount, code


def getExchangeReward(userId, idx):
    """
    获取兑换奖励
    """
    rewards = []
    code = 1
    rewardListConf = getAllRewardList()
    rewardConf = {}
    targetVal = 0
    for _val in rewardListConf:
        if idx == _val.get("id", 0):
            rewardConf = _val.get("reward", {})
            targetVal = _val.get("targetVal", 0)
            break
    luckyTreeData = getLuckyTreeData(userId)
    if luckyTreeData.get("copperCount", 0) < targetVal:
        return rewards, code
    if rewardConf:
        itemId = rewardConf.get("name", 0)
        if util.isChestRewardId(itemId):
            rewards = chest_system.getChestRewards(userId, itemId)
        else:
            rewards = [rewardConf]
        code = util.addRewards(userId, rewards, "BI_NFISH_LUCKY_TREE_REWARDS", int(idx))
        if code != 0:
            ftlog.error("lucky_tree, userId =", userId, "idx =", idx, "rewards =", rewards, "code =", code)
        luckyTreeData["copperCount"] = max(0, luckyTreeData["copperCount"] - targetVal)
        saveLuckyTreeData(userId, luckyTreeData)
    return rewards, code


def sendLuckyTreeReward(userId, actType=1, idx=1):
    """
    发送领取摇钱树奖励结果, actType=1表示领取铜币奖励，actType=2表示兑换奖励
    """
    message = MsgPack()
    message.setCmd("lucky_tree_reward")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    if actType == 1:
        rewards, code = getReward(userId)
    else:
        rewards, code = getExchangeReward(userId, idx)
        message.setResult("id", idx)
    message.setResult("actType", actType)
    message.setResult("code", code)
    message.setResult("rewards", rewards)
    router.sendToUser(message, userId)


def sendLuckyTreeAccelerate(userId):
    """
    发送看视频加速结果
    """
    message = MsgPack()
    message.setCmd("lucky_tree_accelerate")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    rewardTs, code = accelerateReward(userId)
    message.setResult("rewardTs", rewardTs)
    message.setResult("code", code)
    router.sendToUser(message, userId)


def accelerateReward(userId):
    """
    前端通知后端看广告加速
    """
    luckyTreeConf = config.getLuckyTreeConf()
    maxAcceleratetimes = luckyTreeConf.get("maxAcceleratetimes")
    accelerateTimes = weakdata.getDayFishData(userId, "accelerateTimes", 0)
    curTime = int(time.time())
    luckyTreeConf = config.getLuckyTreeConf()
    luckyTreeData = getLuckyTreeData(userId)
    rewardTs = luckyTreeData.get("rewardTs")   # 当前的可领奖时间
    if accelerateTimes < maxAcceleratetimes:
        code = 0
    else:
        code = 1
        return luckyTreeData["rewardTs"], code
    # 看一次广告加速的时间,单位 /h
    accelerateTsConf = luckyTreeConf.get("accelerateTime", 1)
    accelerateTs = accelerateTsConf * 60 * 60
    if curTime + accelerateTs < rewardTs:
        rewardTs = rewardTs - accelerateTs
    else:
        rewardTs = curTime
    luckyTreeData["rewardTs"] = rewardTs
    weakdata.incrDayFishData(userId, "accelerateTimes", 1)
    saveLuckyTreeData(userId, luckyTreeData)
    return luckyTreeData["rewardTs"], code


def saveLuckyTreeData(userId, val):
    """
    存储免费金币摇钱树数据
    """
    if val:
        daobase.executeUserCmd(userId, "SET", _getLuckyTreeKey(userId), json.dumps(val))


def getLuckyTreeData(userId):
    """
    获取免费金币摇钱树数据
    """
    val = daobase.executeUserCmd(userId, "GET", _getLuckyTreeKey(userId))
    if not val:
        val = "{}"
    return json.loads(val)