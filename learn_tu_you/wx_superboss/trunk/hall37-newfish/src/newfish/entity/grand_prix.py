#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/29

"""
大奖赛
"""

import time
import json
from datetime import date, timedelta

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from newfish.entity import util, config, weakdata
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData, WeakData
from newfish.entity.ranking import ranking_system
from newfish.entity.ranking.ranking_base import RankType


def isGrandPrixOpenTime():
    """
    是否为大奖赛开放时段 00:00 —— 23: 30
    """
    curTime = int(time.time())
    dayStartTS = util.getDayStartTimestamp(curTime)
    openTimeRange = config.getGrandPrixConf("openTimeRange")
    return util.timeStrToInt(openTimeRange[0]) < curTime - dayStartTS < util.timestampToStr(openTimeRange[1])


def getPlayAddition(playTimes):
    """
    获取游戏次数积分加成 1: 0.01, 2: 0.02, ... 5: 0.05
    """
    playAddition = 0
    for val in config.getGrandPrixConf("playAddition"):
        if playTimes >= val["playTimes"]:
            playAddition = val["addition"]
    return playAddition


def saveGrandPrixData(userId, startTs, fireCount, fishPoint, useSkillTimes, targetFish, levelFpMultiple):
    """
    保存大奖赛数据
    :param userId: 玩家Id
    :param startTs: 大奖赛开始的时间戳
    :param fireCount: 大奖赛剩余开火次数
    :param fishPoint: 捕鱼积分
    :param useSkillTimes: 大奖赛剩余技能使用次数
    :param targetFish: 大奖赛目标鱼捕获数量
    :param levelFpMultiple: 大奖赛火炮等级和倍率
    :return:
    """
    weakdata.setDayFishData(userId, WeakData.grandPrix_startTS, startTs)
    weakdata.setDayFishData(userId, WeakData.grandPrix_fireCount, fireCount)
    weakdata.setDayFishData(userId, WeakData.grandPrix_fishPoint, fishPoint)
    weakdata.setDayFishData(userId, WeakData.grandPrix_useSkillTimes, json.dumps(useSkillTimes))
    weakdata.setDayFishData(userId, WeakData.grandPrix_targetFish, json.dumps(targetFish))
    weakdata.setDayFishData(userId, WeakData.grandPrix_levelFpMultiple, json.dumps(levelFpMultiple))


def sendGrandPrixInfo(userId):
    """
    发送大奖赛信息
    """
    # 捕鱼积分
    grandPrixFishPoint = weakdata.getDayFishData(userId, WeakData.grandPrix_fishPoint, 0)
    # 大奖赛剩余开火次数
    grandPrixFireCount = weakdata.getDayFishData(userId, WeakData.grandPrix_fireCount, 0)
    # 大奖赛剩余技能使用次数
    grandPrixUseSkillTimes = weakdata.getDayFishData(userId, WeakData.grandPrix_useSkillTimes, [])
    # 大奖赛目标鱼捕获数量
    grandPrixTargetFish = weakdata.getDayFishData(userId, WeakData.grandPrix_targetFish, {})
    # 大奖赛火炮等级和倍率
    grandPrixLevelFpMultiple = weakdata.getDayFishData(userId, WeakData.grandPrix_levelFpMultiple)
    # 大奖赛开始的时间戳
    grandPrixStartTS = weakdata.getDayFishData(userId, WeakData.grandPrix_startTS, 0)
    # 大奖赛免费游戏次数 大奖赛付费游戏次数
    _freeTimes = weakdata.getDayFishData(userId, WeakData.grandPrix_freeTimes, 0)
    _paidTimes = weakdata.getDayFishData(userId, WeakData.grandPrix_paidTimes, 0)

    if not isGrandPrixOpenTime():
        grandPrixStartTS = 0
        grandPrixFireCount = 0
        grandPrixTargetFish = {}
        grandPrixUseSkillTimes = []
        grandPrixFishPoint = 0
        grandPrixLevelFpMultiple = []
        saveGrandPrixData(userId, grandPrixStartTS, grandPrixFireCount, grandPrixFishPoint, grandPrixUseSkillTimes,
                          grandPrixTargetFish, grandPrixLevelFpMultiple)
        _freeTimes = _paidTimes = 0
        weakdata.setDayFishData(userId, WeakData.grandPrix_freeTimes, 0)
        weakdata.setDayFishData(userId, WeakData.grandPrix_paidTimes, 0)

    vipLevel = util.getVipRealLevel(userId)
    signUpState = 1 if grandPrixStartTS > 0 else 0
    playTimes = _freeTimes + _paidTimes
    playAddition = getPlayAddition(playTimes) if signUpState == 1 else getPlayAddition(playTimes + 1)
    remainFreeTimes = config.getVipConf(vipLevel).get("grandPrixFreeTimes", 0) - _freeTimes
    openTime = "-".join(config.getGrandPrixConf("openTimeRange"))

    mo = MsgPack()
    mo.setCmd("grand_prix_info")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("remainFreeTimes", remainFreeTimes)
    mo.setResult("fee", config.getGrandPrixConf("fee"))
    mo.setResult("playAddition", ("%d%%" % int(playAddition * 100)))
    mo.setResult("openTime", openTime)
    mo.setResult("isInOpenTime", 1 if isGrandPrixOpenTime() else 0)
    mo.setResult("signUpState", signUpState)                            # 注册状态
    weekPointList = json.loads(weakdata.getWeekFishData(userId, WeakData.grandPrix_weekPointList, "[0, 0, 0, 0, 0, 0, 0]"))     # 大奖赛周积分数据
    weekPoint = sum(sorted(weekPointList)[-3:])
    mo.setResult("weekPoint", weekPoint)
    mo.setResult("todayRankType", RankType.TodayGrandPrix)
    mo.setResult("todayDate", util.timestampToStr(int(time.time()), "%m/%d"))
    mo.setResult("yesterdayRankType", RankType.LastGrandPrix)
    mo.setResult("yesterdayDate", util.timestampToStr(int(time.time() - 86400), "%m/%d"))
    mo.setResult("weekRankType", RankType.WeekGrandPrix)
    # mo.setResult("des", config.getGrandPrixConf("info").get("des"))
    lang = util.getLanguage(userId)
    mo.setResult("des", config.getMultiLangTextConf(config.getGrandPrixConf("info").get("des"), lang=lang))
    st = time.localtime(int(time.time()))
    monday = date.today() - timedelta(days=st.tm_wday)
    mondayTimestamp = int(time.mktime(monday.timetuple()))              # 周一
    mondayStr = util.timestampToStr(mondayTimestamp, "%m/%d")
    sundayStr = util.timestampToStr((mondayTimestamp + 86400 * 6), "%m/%d")
    mo.setResult("weekDate", "%s-%s" % (mondayStr, sundayStr))
    router.sendToUser(mo, userId)
    if ftlog.is_debug():
        ftlog.debug("FishGrandPrixPlayer, userId =", userId, "mo =", mo)
    # 已经报名则直接开始大奖赛
    # if signUpState == 1:
    #     self.startGrandPrix(signUpState)
