# -*- coding=utf-8 -*-
"""
大奖赛
"""
# @Author  : Kangxiaopeng
# @Time    : 2019/11/2


import time
import json

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from newfish.entity import util, config, weakdata
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData, WeakData
from newfish.entity.ranking.ranking_base import RankType


def isGrandPrixOpenTime():
    """
    是否为大奖赛开放时段 00:00 -- 23:00
    """
    curTime = int(time.time())
    dayStartTS = util.getDayStartTimestamp(curTime)
    openTimeRange = config.getGrandPrixConf("openTimeRange")
    return util.timeStrToInt(openTimeRange[0]) < (curTime - dayStartTS) < util.timeStrToInt(openTimeRange[1])


def getPointInfo(userId):
    """
    获取阶段积分奖励
    """
    pointsInfo = []
    stageInfo = config.getGrandPrixConf("stageInfo")
    for info in stageInfo:
        point = info["point"]
        if point in weakdata.getDayFishData(userId, WeakData.grandPrix_getPointsInfo, []):
            pointsInfo.append({"score": point, "reward": info["rewards"][0], "isGet": 1})
        else:
            pointsInfo.append({"score": point, "reward": info["rewards"][0], "isGet": 0})
    new_s = sorted(pointsInfo, key=lambda e: e.__getitem__('score'))
    return new_s


def saveGrandPrixData(userId, startTs, fireCount, fishPoint, useSkillTimes, targetFish, getPointsInfo, todayMaxPoints, freeTimes):
    """
    保存大奖赛数据
    """
    weakdata.setDayFishData(userId, WeakData.grandPrix_startTS, startTs)
    weakdata.setDayFishData(userId, WeakData.grandPrix_fireCount, fireCount)
    weakdata.setDayFishData(userId, WeakData.grandPrix_fishPoint, fishPoint)
    weakdata.setDayFishData(userId, WeakData.grandPrix_useSkillTimes, json.dumps(useSkillTimes))
    weakdata.setDayFishData(userId, WeakData.grandPrix_targetFish, json.dumps(targetFish))
    # weakdata.setDayFishData(userId, WeakData.grandPrix_levelFpMultiple, json.dumps(levelFpMultiple))
    weakdata.setDayFishData(userId, WeakData.grandPrix_getPointsInfo, json.dumps(getPointsInfo))
    weakdata.setDayFishData(userId, WeakData.grandPrix_point, todayMaxPoints)
    weakdata.setDayFishData(userId, WeakData.grandPrix_freeTimes, freeTimes)


def sendGrandPrixInfo(userId):
    """
    发送大奖赛信息
    """
    if not isGrandPrixOpenTime():
        grandPrixStartTS = 0
        grandPrixFireCount = 0
        grandPrixTargetFish = {}
        grandPrixUseSkillTimes = []
        grandPrixFishPoint = 0
        # grandPrixLevelFpMultiple = []
        getPointsInfo = []
        todayMaxPoints = 0
        freeTimes = 0
        saveGrandPrixData(userId, grandPrixStartTS, grandPrixFireCount, grandPrixFishPoint, grandPrixUseSkillTimes,
                          grandPrixTargetFish, getPointsInfo, todayMaxPoints, freeTimes)

    vipLevel = util.getVipRealLevel(userId)
    # 大奖赛剩余免费次数
    remainFreeTimes = config.getVipConf(vipLevel).get("grandPrixFreeTimes", 0) - weakdata.getDayFishData(userId, WeakData.grandPrix_freeTimes, 0)
    mo = MsgPack()
    mo.setCmd("grand_prix_info")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("remainFreeTimes", remainFreeTimes)
    mo.setResult("fee", config.getGrandPrixConf("fee"))
    mo.setResult("openTime", "-".join(config.getGrandPrixConf("openTimeRange")))
    mo.setResult("isInOpenTime", 1 if isGrandPrixOpenTime() else 0)
    mo.setResult("signUpState", 1 if weakdata.getDayFishData(userId, WeakData.grandPrix_startTS, 0) > 0 else 0)
    mo.setResult("todayRankType", RankType.TodayGrandPrix)
    mo.setResult("todayDate", util.timestampToStr(int(time.time()), "%m/%d"))
    mo.setResult("yesterdayRankType", RankType.LastGrandPrix)
    mo.setResult("yesterdayDate", util.timestampToStr(int(time.time() - 86400), "%m/%d"))
    mo.setResult("pointsInfo", getPointInfo(userId))    # 奖励积分 道具Id、道具数量、是否领取了奖励0|1
    mo.setResult("todayMaxPoints", weakdata.getDayFishData(userId, WeakData.grandPrix_point, 0))      # 今日最高积分
    router.sendToUser(mo, userId)
