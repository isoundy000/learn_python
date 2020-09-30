# -*- coding=utf-8 -*-
"""
Created by lichen on 2017/7/24.
"""

import random
import json
import time
from datetime import date
from collections import OrderedDict

import freetime.util.log as ftlog
from poker.entity.dao import daobase, userdata
from poker.entity.configure import gdata
import poker.util.timestamp as pktimestamp
from newfish.entity import config, util, redis_keys
from newfish.entity.config import CLIENTID_ROBOT
from newfish.servers.room.rpc import room_remote
from newfish.entity.ranking.ranking_base import TodayStarfishRanking, YesterdayStarfishRanking, \
    BulletRanking, TodayLuckyRanking, WeekLuckyRanking, TodayRobberyRanking, YestodayRobberyRanking, \
    WeekRobberyRanking, MatchRanking, RankType, RankDefineIndex, SlotMachineIntegralRanking, \
    MoneyTreeRanking, TodayGrandPrixRanking, YestodayGrandPrixRanking, WeekGrandPrixRanking, ProfitCoinRanking, \
    FestivalTurntableIntegralRanking, TodayRankingBase, CollectItemRanking, TodayPoseidonRanking, \
    YestodayPoseidonRanking, WeekPoseidonRanking, CompActTeamRanking, CompActPointRanking, \
    YestordayCompActTeamRanking, CompActRankTypeDefineIndexDict, ItemHappyDoubleRanking, SuperbossPointRanking, \
    YestordaySuperbossPointRanking, SbossPointRankTypeDefineIndexDict, LastSbossPointRankTypeDefineIndexDict, \
    SbossRankDefineIdxBigRoomIdDict
from newfish.entity.mail_system import MailRewardType


def getAllTabs(userId):
    """
    获取所有可以显示的排行榜
    """
    confs = []
    isVerLimit = util.isVersionLimit(userId)            # 是否是提审版本
    lang = util.getLanguage(userId)
    rankRewardConf = config.getAllRankConfs()
    # rankRewardConf = OrderedDict(sorted(rankRewardConf.iteritems(), key=lambda d: d[1]["order"]))
    # for rankType, conf in rankRewardConf.iteritems():
    #     if (isVerLimit is False or conf.get("reviewVerLimit", 0) == 0) and conf["visible"] and conf["showInCommon"]:
    #         confs.append({"rankType": int(rankType), "rankName": config.getMultiLangTextConf(str(conf["rankName"]), lang=lang)})
    for _tab in rankRewardConf.get("tabs"):
        ranks = []
        for _rankType in _tab["rankList"]:
            conf = rankRewardConf.get("ranks", {}).get(str(_rankType))
            if conf and (not isVerLimit or not conf.get("reviewVerLimit", 0)) and conf["visible"] and conf["showInCommon"]:
                ranks.append({"rankType": int(_rankType), "rankName": config.getMultiLangTextConf(str(conf["rankName"]), lang=lang)})
        if ranks:
            confs.append({"tabName": config.getMultiLangTextConf(str(_tab["tabName"]), lang=lang), "ranks": ranks})
    return confs


def getRankingInfoByType(userId, clientId, rankType, httpRequest=False, rankDetail=False):
    """通过排行榜类型获取排行榜信息"""
    rankClass = _getRankingClass(rankType, userId, clientId, httpRequest)
    if rankDetail:
        return rankClass.getRankingInfo2()
    else:
        return rankClass.getRankingInfo() if rankClass else {}


def getRankingTabs(userId, clientId, rankType, httpRequest=False, rankDetail=False):
    """
    获取指定排行榜信息
    :param userId:
    :param clientId:
    :param rankType: 排行榜类型
    :param httpRequest:
    :return:
    """
    tabs = []
    ranking = {}
    rankRewardConf = config.getRankRewardConf(rankType)
    if not rankRewardConf or not rankRewardConf["visible"]:
        return tabs
    if util.isVersionLimit(userId) and rankRewardConf.get("reviewVerLimit", 0) == 1:  # 提审版本不可见
        return tabs
    lang = util.getLanguage(userId, clientId)
    ranking["rankType"] = rankType
    ranking["rankName"] = config.getMultiLangTextConf(str(rankRewardConf.get("rankName")), lang=lang)
    rankDescId = rankRewardConf.get("rankDesc")
    if rankDescId:
        ranking["rankDesc"] = config.getMultiLangTextConf(str(rankDescId), lang=lang)
    else:
        ranking["rankDesc"] = ""
    ranking = getRankingInfoByType(userId, clientId, rankType, httpRequest, rankDetail) or ranking
    tabs.append(ranking)
    if ftlog.is_debug():
        ftlog.debug("getrankingtabs", tabs, "ranking =", ranking)
    return tabs


# def _getMatchRoomRankList(userId, roomId):
#     if gdata.roomIdDefineMap().get(roomId):
#         rankData = room_remote.getRankList(userId, roomId)
#     else:
#         rankData = [
#             {"userId": userId,
#              "name": "",
#              "sex": 0,
#              "score": 0,
#              "rank": 0,
#              "avatar": "",
#              "vip": 0,
#              "rewards": []}
#         ]
#     return rankData


def _refreshStarfishRankData(event):
    """
    刷新海星收集榜
    """
    rankClass = _getRankingClass(RankType.TodayStarfish, event.userId, CLIENTID_ROBOT)
    rankClass.refreshRankingData(event)


def _refreshBulletRankData(event):
    """
    刷新招财珠榜
    """
    rankClass = _getRankingClass(RankType.Bullet, event.userId, CLIENTID_ROBOT)
    rankClass.refreshRankingData(event)


def _refreshLuckyBonusRankData(event):
    """
    刷新玩家幸运榜，七日幸运榜
    """
    if ftlog.is_debug():
        ftlog.debug("_refreshLuckyBonusRankData", event.coinNum)
    if not event.coinNum:
        return
    # 今日榜
    rankClass = _getRankingClass(RankType.TodayLucky, event.userId, CLIENTID_ROBOT)
    rankClass.refreshRankingData(event)
    # 七日榜
    rankClass = _getRankingClass(RankType.WeekLucky, event.userId, CLIENTID_ROBOT)
    rankClass.refreshRankingData(event)


def refreshMatchRankData(roomId, userScores):
    """
    刷新回馈赛排行榜
    """
    rankType = RankType.XiuXianMatch                # 休闲回馈赛榜
    if roomId == 44101:
        rankType = RankType.ChuJiMatch              # 初级回馈赛榜
    elif roomId == 44102:
        rankType = RankType.ZhongJiMatch            # 中级回馈赛榜
    elif roomId == 44103:
        rankType = RankType.GaoJiMatch              # 高级回馈赛榜

    rankClass = _getRankingClass(rankType, config.ROBOT_MAX_USER_ID, CLIENTID_ROBOT)
    rankClass.refreshRankingData(userScores)


def _refreshSlotMachineRankData(event):
    """
    刷新老虎机积分榜
    """
    if ftlog.is_debug():
        ftlog.debug("_refreshSlotMachineRankData---->", event.userId, event.integral)
    rankClass = _getRankingClass(RankType.SlotMachine, event.userId, CLIENTID_ROBOT)
    rankClass.refreshRankingData(event)


def _refreshMoneyTreeRankData(event):
    """
    刷新摇钱树摇动次数排行榜
    """
    if ftlog.is_debug():
        ftlog.debug("_refreshMoneyTreeRankData->", event.userId, event.count)
    rankClass = _getRankingClass(RankType.MoneyTree, event.userId, CLIENTID_ROBOT)
    rankClass.refreshRankingData(event)


def refreshGrandPrixPoint(userId, userPoint):
    """
    刷新大奖赛日榜和周榜
    """
    rankClass = _getRankingClass(RankType.TodayGrandPrix, userId, CLIENTID_ROBOT)
    userPointData = [userId, userPoint]
    rankClass.refreshRankingData(userPointData)

    # rankClass = _getRankingClass(RankType.WeekGrandPrix, userId, CLIENTID_ROBOT)
    # rankClass.refreshRankingData(userPointData)


def _refreshFestivalTurntableRankData(event):
    """
    刷新节日转盘抽大奖积分榜
    """
    if ftlog.is_debug():
        ftlog.debug("_refreshFestivalTurntableRankData---->", event.userId, event.integral)
    rankClass = _getRankingClass(RankType.FestivalTurntable, event.userId, CLIENTID_ROBOT)
    rankClass.refreshRankingData(event)


def _refreshProfitCoinRankData(event):
    """
    刷新玩家盈利榜
    """
    if ftlog.is_debug():
        ftlog.debug("_refreshProfitCoinRankData->", event.userId, event.count)
    rankClass = _getRankingClass(RankType.ProfitCoin, event.userId, CLIENTID_ROBOT)
    rankClass.refreshRankingData(event)


def _refreshSuperbossPointRankData(event):
    """
    刷新超级boss积分排行榜
    """
    if ftlog.is_debug():
        ftlog.debug("_refreshSuperbossPointRankData->", event.userId, event.bigRoomId, event.point)
    for _rankType, _defineIdx in SbossPointRankTypeDefineIndexDict.iteritems():
        if SbossRankDefineIdxBigRoomIdDict.get(_defineIdx) == event.bigRoomId:
            rankClass = _getRankingClass(_rankType, event.userId, CLIENTID_ROBOT)
            rankClass.refreshRankingData(event)
            break


def _refreshCollectItemRankData(event):
    """
    刷新收集xx道具排行榜(兔耳收集榜)
    """
    rewards = event.rewards
    if not rewards:
        return
    for reward in rewards:
        if reward.get("name", 0) == config.getCollectItemConf("consumeItemId"):
            rankClass = _getRankingClass(RankType.CollectItem, event.userId, CLIENTID_ROBOT)
            rankClass.refreshRankingData(event)
        if reward.get("name", 0) == config.getActItemHappyDoubleConfig().get("rankKindId"):
            rankClass = _getRankingClass(RankType.ItemHappyDouble, event.userId, CLIENTID_ROBOT)
            rankClass.refreshRankingData(event)


def _refreshPoseidonWinRankData(event):
    """
    刷新海皇今日赢家榜、七日赢家榜
    """
    rankClass = _getRankingClass(RankType.PoseidonTodayWinner, event.userId, CLIENTID_ROBOT)
    rankClass.refreshRankingData(event)

    rankClass = _getRankingClass(RankType.PoseidonWeekWinner, event.userId, CLIENTID_ROBOT)
    rankClass.refreshRankingData(event)


def refreshCompActTeamPoint(rankType, userId, point):
    """
    刷新竞赛活动team积分
    """
    if ftlog.is_debug():
        ftlog.debug("refreshCompActTeamPoint, userId =", userId, "point =", point, "rankType =", rankType)
    data = [userId, point]
    rankClass = _getRankingClass(rankType, userId, CLIENTID_ROBOT)
    rankClass and rankClass.refreshRankingData(data)

    rankClass = _getRankingClass(RankType.CompActPoint, userId, CLIENTID_ROBOT)
    rankClass and rankClass.refreshRankingData(data)


def onTimer(event):
    """排行榜的定时器"""
    global _prevProcessRankingTime
    timestamp = pktimestamp.getCurrentTimestamp()
    if (not _prevProcessRankingTime or timestamp - _prevProcessRankingTime > _processRankingInterval):
        # # 隔天清理竞赛活动过期数据
        # if _prevProcessRankingTime and util.getDayStartTimestamp(timestamp) != util.getDayStartTimestamp(_prevProcessRankingTime):
        #     from newfish.entity.fishactivity import competition_activity
        #     competition_activity.clearCompActExpireData()
        _prevProcessRankingTime = timestamp
        processRankings()
        addRobotToGrandPrix()


def processRankings():
    """处理排行榜发奖逻辑"""
    timestamp = pktimestamp.getCurrentTimestamp()
    todayDate = date.fromtimestamp(timestamp).strftime("%Y%m%d")
    strfTime = time.strftime("%R", time.localtime(timestamp))               # 18:31

    # rankClassThousandRed = _getRankingClass(RankType.RedReward, config.ROBOT_MAX_USER_ID, CLIENTID_ROBOT)
    # rankClassThousandRed.processRanking(todayDate, strfTime)

    if config.getRankRewardConf(RankType.TodayStarfish).get("visible"):
        rankClass = _getRankingClass(RankType.TodayStarfish, config.ROBOT_MAX_USER_ID, CLIENTID_ROBOT)
        rankClass.processRanking(todayDate, strfTime)

    if config.getRankRewardConf(RankType.WeekLucky).get("visible"):
        rankClass = _getRankingClass(RankType.WeekLucky, config.ROBOT_MAX_USER_ID, CLIENTID_ROBOT)
        rankClass.processRanking(todayDate, strfTime)

    if config.getRankRewardConf(RankType.TodayWinner).get("visible"):
        rankClass = _getRankingClass(RankType.TodayWinner, config.ROBOT_MAX_USER_ID, CLIENTID_ROBOT)
        rankClass.processRanking(todayDate, strfTime)

    if config.getRankRewardConf(RankType.WeekWinner).get("visible"):
        rankClass = _getRankingClass(RankType.WeekWinner, config.ROBOT_MAX_USER_ID, CLIENTID_ROBOT)
        rankClass.processRanking(todayDate, strfTime)

    if config.getRankRewardConf(RankType.SlotMachine).get("visible"):
        rankClass = _getRankingClass(RankType.SlotMachine, config.ROBOT_MAX_USER_ID, CLIENTID_ROBOT)
        rankClass.processRanking(todayDate, strfTime)

    if config.getRankRewardConf(RankType.MoneyTree).get("visible"):
        rankClass = _getRankingClass(RankType.MoneyTree, config.ROBOT_MAX_USER_ID, CLIENTID_ROBOT)
        rankClass.processRanking(todayDate, strfTime)

    if config.getRankRewardConf(RankType.TodayGrandPrix).get("visible"):
        rankClass = _getRankingClass(RankType.TodayGrandPrix, config.ROBOT_MAX_USER_ID, CLIENTID_ROBOT)
        rankClass.processRanking(todayDate, strfTime)

    # if config.getRankRewardConf(RankType.WeekGrandPrix).get("visible"):
    #     rankClass = _getRankingClass(RankType.WeekGrandPrix, config.ROBOT_MAX_USER_ID, CLIENTID_ROBOT)
    #     rankClass.processRanking(todayDate, strfTime)

    if config.getRankRewardConf(RankType.FestivalTurntable).get("visible"):
        rankClass = _getRankingClass(RankType.FestivalTurntable, config.ROBOT_MAX_USER_ID, CLIENTID_ROBOT)
        rankClass.processRanking(todayDate, strfTime)

    if config.getRankRewardConf(RankType.CollectItem).get("visible"):
        rankClass = _getRankingClass(RankType.CollectItem, config.ROBOT_MAX_USER_ID, CLIENTID_ROBOT)
        rankClass.processRanking(todayDate, strfTime)

    if config.getRankRewardConf(RankType.PoseidonTodayWinner).get("visible"):
        rankClass = _getRankingClass(RankType.PoseidonTodayWinner, config.ROBOT_MAX_USER_ID, CLIENTID_ROBOT)
        rankClass.processRanking(todayDate, strfTime)

    if config.getRankRewardConf(RankType.PoseidonWeekWinner).get("visible"):
        rankClass = _getRankingClass(RankType.PoseidonWeekWinner, config.ROBOT_MAX_USER_ID, CLIENTID_ROBOT)
        rankClass.processRanking(todayDate, strfTime)

    # 竞赛活动积分排行榜
    if config.getRankRewardConf(RankType.CompActPoint).get("visible"):
        rankClass = _getRankingClass(RankType.CompActPoint, config.ROBOT_MAX_USER_ID, CLIENTID_ROBOT)
        if rankClass and rankClass.processRanking(todayDate, strfTime):
            # 竞赛活动team排行榜
            from newfish.entity.fishactivity import competition_activity
            # rankType = competition_activity.getLastChampionTeamRankType()
            # if config.getRankRewardConf(rankType).get("visible"):
            #     rankClass = _getRankingClass(rankType, config.ROBOT_MAX_USER_ID, CLIENTID_ROBOT)
            #     rankClass and rankClass.processRanking(todayDate, strfTime)
            rankTypeOrder = json.loads(competition_activity.getRankTypeOrder())
            teamCnt = config.getCompActConf().get("rankRewardsTeamCnt", 1)
            for idx, rankType in enumerate(rankTypeOrder):
                if idx >= teamCnt:
                    break
                if config.getRankRewardConf(rankType).get("visible"):
                    rankClass = _getRankingClass(rankType, config.ROBOT_MAX_USER_ID, CLIENTID_ROBOT)
                    rankClass and rankClass.processRanking(todayDate, strfTime)

    if config.getRankRewardConf(RankType.ItemHappyDouble).get("visible"):
        rankClass = _getRankingClass(RankType.ItemHappyDouble, config.ROBOT_MAX_USER_ID, CLIENTID_ROBOT)
        rankClass.processRanking(todayDate, strfTime)

    # 超级boss排行榜发奖.
    for _rankType in SbossPointRankTypeDefineIndexDict.keys():
        if config.getRankRewardConf(_rankType).get("visible"):
            rankClass = _getRankingClass(_rankType, config.ROBOT_MAX_USER_ID, CLIENTID_ROBOT)
            rankClass.processRanking(todayDate, strfTime)


def addRobotToGrandPrix():
    """
    机器人进入大奖赛排行榜 "robot": [1, 30, [2, 2]]
    """
    global _addRobotToGrandPrixRankTimestamp
    curTime = int(time.time())
    startDay = config.getGrandPrixConf("info").get("startDay")
    if startDay and curTime < util.getTimestampFromStr(startDay):
        return
    if curTime < _addRobotToGrandPrixRankTimestamp:
        return
    robotConf = config.getGrandPrixConf("info").get("robot", [])
    if len(robotConf) < 3 or len(robotConf[2]) < 2:
        _addRobotToGrandPrixRankTimestamp = curTime + 10 * 60                   # 10分钟
        return
    # 不启用机器人
    if robotConf[0] == 0:
        _addRobotToGrandPrixRankTimestamp = curTime + 10 * 60
        return
    startInterval = robotConf[1] * 60
    dayStartTS = util.getDayStartTimestamp(curTime)
    openTimeRange = config.getGrandPrixConf("openTimeRange")
    if util.timeStrToInt(openTimeRange[0]) + startInterval >= (curTime - dayStartTS) or (curTime - dayStartTS) >= util.timeStrToInt(openTimeRange[1]):
        _addRobotToGrandPrixRankTimestamp = curTime
        return
    nextAddInterval = random.randint(robotConf[2][0] * 60, robotConf[2][1] * 60)
    _addRobotToGrandPrixRankTimestamp = curTime + nextAddInterval

    rdKey = redis_keys.MixData.grandPrixRobotData % config.FISH_GAMEID
    robotDatas = config.getGrandPrixConf("robotData")
    maxCount = sum([val["count"] for val in robotDatas])                # {"count": 1, "points": [58001, 60000]},
    dayStartTS = util.getDayStartTimestamp(int(time.time()))
    robotDatas = daobase.executeMixCmd("HGET", rdKey, str(dayStartTS))
    if robotDatas:
        robotDatas = json.loads(robotDatas)
    else:
        robotDatas = {}
    robotDatas.setdefault("uids", [])
    robotDatas.setdefault("ranks", [])
    uidList = robotDatas.get("uids")
    rankList = robotDatas.get("ranks")
    if len(uidList) >= maxCount:
        _addRobotToGrandPrixRankTimestamp = curTime + 10 * 60
        return

    datas = daobase.executeMixCmd("HGETALL", rdKey)
    if datas:
        for ts in datas[0::2]:
            if int(ts) < dayStartTS:
                daobase.executeMixCmd("HDEL", rdKey, ts)

    startRobotUid = 0
    ruid = random.randint(startRobotUid + 1, startRobotUid + maxCount)
    while ruid in uidList:
        ruid = random.randint(startRobotUid + 1, startRobotUid + maxCount)
    rrank = random.randint(1, maxCount)
    while rrank in rankList:
        rrank = random.randint(1, maxCount)
    uidList.append(ruid)
    rankList.append(rrank)
    daobase.executeMixCmd("HSET", rdKey, str(dayStartTS), json.dumps(robotDatas))
    robotDatas = config.getGrandPrixConf("robotData")
    for val in robotDatas:
        if rrank > val["count"]:
            rrank -= val["count"]
        else:
            fishPoint = random.randint(val["points"][0], val["points"][1])
            if userdata.checkUserData(ruid):
                refreshGrandPrixPoint(ruid, fishPoint)
            # else:
            #     ftlog.error("addRobotToGrandPrix, error", "uid =", ruid)
            # if ftlog.is_debug():
            #     ftlog.debug("addRobotToGrandPrix", "uid =", ruid, "rank =", rrank, "point =", fishPoint, maxCount)
            break


def _getRankingClass(rankType, userId, clientId=None, httpRequest=False):
    """获取排行榜的类"""
    rankClass = None
    if rankType == RankType.TodayStarfish:                      # 海星收集榜
        rankClass = TodayStarfishRanking(userId, rankType, RankDefineIndex.Starfish, clientId, httpRequest, MailRewardType.StarRank)
    elif rankType == RankType.LastStarfish:                     # 昨日海星榜
        rankClass = YesterdayStarfishRanking(userId, rankType, RankDefineIndex.Starfish, clientId, httpRequest, MailRewardType.StarRank)
    elif rankType == RankType.Bullet:                           # 招财珠榜
        rankClass = BulletRanking(userId, rankType, RankDefineIndex.Bullet, clientId, httpRequest)
    elif rankType == RankType.TodayLucky:                       # 每日幸运榜
        rankClass = TodayLuckyRanking(userId, rankType, RankDefineIndex.TodayLucky, clientId, httpRequest)
    elif rankType == RankType.WeekLucky:                        # 七日幸运榜
        rankClass = WeekLuckyRanking(userId, rankType, RankDefineIndex.WeekLucky, clientId, httpRequest)
    elif rankType == RankType.TodayWinner:                      # 招财今日赢家榜
        rankClass = TodayRobberyRanking(userId, rankType, RankDefineIndex.RobberyWinner, clientId, httpRequest, MailRewardType.RobberyRank)
    elif rankType == RankType.LastWinner:                       # 招财昨日赢家榜
        rankClass = YestodayRobberyRanking(userId, rankType, RankDefineIndex.RobberyWinner, clientId, httpRequest, MailRewardType.RobberyRank)
    elif rankType == RankType.WeekWinner:                       # 招财七日赢家榜
        rankClass = WeekRobberyRanking(userId, rankType, RankDefineIndex.WeekWinner, clientId, httpRequest)
    # elif rankType == RankType.RedReward:                      # 万元红包发奖（已废弃）
    #     rankClass = RedRewardRank(userId, rankType, RankDefineIndex.ThousandRed, clientId, httpRequest)
    elif rankType == RankType.XiuXianMatch:                     # 休闲回馈赛
        rankClass = MatchRanking(userId, rankType, RankDefineIndex.Match44104, clientId, httpRequest)
    elif rankType == RankType.ChuJiMatch:                       # 初级回馈赛
        rankClass = MatchRanking(userId, rankType, RankDefineIndex.Match44101, clientId, httpRequest)
    elif rankType == RankType.ZhongJiMatch:                     # 中级回馈赛
        rankClass = MatchRanking(userId, rankType, RankDefineIndex.Match44102, clientId, httpRequest)
    elif rankType == RankType.GaoJiMatch:                       # 高级回馈赛
        rankClass = MatchRanking(userId, rankType, RankDefineIndex.Match44103, clientId, httpRequest)
    elif rankType == RankType.SlotMachine:                      # 老虎机活动积分榜
        rankClass = SlotMachineIntegralRanking(userId, rankType, RankDefineIndex.SlotMachine, clientId, httpRequest, MailRewardType.SystemReward)
    elif rankType == RankType.MoneyTree:                        # 摇钱树活动摇动次数榜
        rankClass = MoneyTreeRanking(userId, rankType, RankDefineIndex.MoneyTree, clientId, httpRequest, MailRewardType.SystemReward)
    elif rankType == RankType.TodayGrandPrix:                   # 大奖赛积分榜
        rankClass = TodayGrandPrixRanking(userId, rankType, RankDefineIndex.GrandPrix, clientId, httpRequest, MailRewardType.SystemReward)
    elif rankType == RankType.LastGrandPrix:                    # 大奖赛昨日榜
        rankClass = YestodayGrandPrixRanking(userId, rankType, RankDefineIndex.GrandPrix, clientId, httpRequest)
    # elif rankType == RankType.WeekGrandPrix:                    # 大奖赛积分周榜
    #     rankClass = WeekGrandPrixRanking(userId, rankType, RankDefineIndex.WeekGrandPrix, clientId, httpRequest, MailRewardType.SystemReward)
    elif rankType == RankType.ProfitCoin:                       # 玩家盈利榜
        rankClass = ProfitCoinRanking(userId, rankType, RankDefineIndex.ProfitCoin, clientId, httpRequest)
    elif rankType == RankType.FestivalTurntable:                # 节日转盘抽大奖积分榜
        rankClass = FestivalTurntableIntegralRanking(userId, rankType, RankDefineIndex.FestivalTurntable, clientId, httpRequest, MailRewardType.ActivityReward)
    elif rankType == RankType.MagicCrystal:                     # 魔晶收集榜
        rankClass = TodayRankingBase(userId, rankType, RankDefineIndex.MagicCrystal, clientId, httpRequest)
    elif rankType == RankType.CollectItem:                      # 收集xx道具榜(集兔耳赢奖励)
        rankClass = CollectItemRanking(userId, rankType, RankDefineIndex.CollectItem, clientId, httpRequest, MailRewardType.ActivityReward)
    elif rankType == RankType.PoseidonTodayWinner:              # 海皇今日赢家榜
        rankClass = TodayPoseidonRanking(userId, rankType, RankDefineIndex.PoseidonWinner, clientId, httpRequest, MailRewardType.PoseidonRank)
    elif rankType == RankType.PoseidonLastWinner:               # 海皇昨日赢家榜
        rankClass = YestodayPoseidonRanking(userId, rankType, RankDefineIndex.PoseidonWinner, clientId, httpRequest, MailRewardType.PoseidonRank)
    elif rankType == RankType.PoseidonWeekWinner:               # 海皇七日赢家榜
        rankClass = WeekPoseidonRanking(userId, rankType, RankDefineIndex.PoseidonWeekWinner, clientId, httpRequest)
    elif rankType in CompActRankTypeDefineIndexDict:            # 竞赛活动Team积分榜
        rankClass = CompActTeamRanking(userId, rankType, CompActRankTypeDefineIndexDict[rankType], clientId, httpRequest, MailRewardType.ActivityReward)
    elif rankType == RankType.CompActPoint:                     # 竞赛活动积分排行榜
        rankClass = CompActPointRanking(userId, rankType, RankDefineIndex.CompActPoint, clientId, httpRequest)
    elif rankType == RankType.LastCompActWinner:                # 上期竞赛冠军榜
        from newfish.entity.fishactivity import competition_activity
        lastRankType = competition_activity.getLastChampionTeamRankType()
        if lastRankType in CompActRankTypeDefineIndexDict:
            rankClass = YestordayCompActTeamRanking(userId, rankType, CompActRankTypeDefineIndexDict[lastRankType], clientId, httpRequest, MailRewardType.ActivityReward)
    elif rankType == RankType.ItemHappyDouble:
        rankClass = ItemHappyDoubleRanking(userId, rankType, RankDefineIndex.ItemHappyDouble, clientId, httpRequest, MailRewardType.ActivityReward)
    elif rankType in SbossPointRankTypeDefineIndexDict:         # 超级boss积分排行榜
        rankClass = SuperbossPointRanking(userId, rankType, SbossPointRankTypeDefineIndexDict[rankType], clientId, httpRequest)
    elif rankType in LastSbossPointRankTypeDefineIndexDict:     # 上期超级boss积分排行榜
        rankClass = YestordaySuperbossPointRanking(userId, rankType, LastSbossPointRankTypeDefineIndexDict[rankType], clientId, httpRequest)
    return rankClass


def getUserRankAndRewards(rankType, userId):
    """
    获取玩家排行榜排名和排名奖励
    """
    rankClass = _getRankingClass(rankType, userId, CLIENTID_ROBOT)
    rank = rankClass.getTopNUserRank(userId, rankClass._getOwnRankingTime())
    rankRewards = rankClass._getOneUserReward(userId, rank)
    return rank, rankRewards


_inited = False
_prevProcessRankingTime = None
_processRankingInterval = 30
_addRobotToGrandPrixRankTimestamp = 0


def initialize(isCenter):
    """初始化"""
    ftlog.info("newfish ranking_system initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from poker.entity.events.tyevent import EventUserLogin, EventHeartBeat
        from newfish.game import TGFish
        from newfish.entity.event import StarfishChangeEvent, BulletChangeEvent, \
            SendMailEvent, ReceiveMailEvent, GameTimeLuckyAddEvent, OpenEggsEvent, \
            SlotMachineAddIntegralEvent, MoneyTreeAddCountEvent, NetIncomeChangeEvent, \
            FestivalTurntableAddIntegralEvent, SuperbossPointChangeEvent, ActivityItemChangeEvent, \
            PoseidonProfitAndLossEvent
        TGFish.getEventBus().subscribe(EventUserLogin, _refreshBulletRankData)
        TGFish.getEventBus().subscribe(StarfishChangeEvent, _refreshStarfishRankData)
        TGFish.getEventBus().subscribe(BulletChangeEvent, _refreshBulletRankData)
        TGFish.getEventBus().subscribe(SendMailEvent, _refreshBulletRankData)
        TGFish.getEventBus().subscribe(ReceiveMailEvent, _refreshBulletRankData)
        TGFish.getEventBus().subscribe(GameTimeLuckyAddEvent, _refreshLuckyBonusRankData)
        TGFish.getEventBus().subscribe(OpenEggsEvent, _refreshLuckyBonusRankData)
        TGFish.getEventBus().subscribe(SlotMachineAddIntegralEvent, _refreshSlotMachineRankData)
        TGFish.getEventBus().subscribe(MoneyTreeAddCountEvent, _refreshMoneyTreeRankData)
        TGFish.getEventBus().subscribe(NetIncomeChangeEvent, _refreshProfitCoinRankData)
        TGFish.getEventBus().subscribe(FestivalTurntableAddIntegralEvent, _refreshFestivalTurntableRankData)
        TGFish.getEventBus().subscribe(ActivityItemChangeEvent, _refreshCollectItemRankData)
        TGFish.getEventBus().subscribe(PoseidonProfitAndLossEvent, _refreshPoseidonWinRankData)
        TGFish.getEventBus().subscribe(SuperbossPointChangeEvent, _refreshSuperbossPointRankData)
        if isCenter:
            from poker.entity.events.tyeventbus import globalEventBus
            globalEventBus.subscribe(EventHeartBeat, onTimer)
    ftlog.info("newfish ranking_system initialize end")