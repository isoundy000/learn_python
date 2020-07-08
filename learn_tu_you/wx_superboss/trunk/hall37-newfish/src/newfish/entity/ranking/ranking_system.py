#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/30

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
    YestordayCompActTeamRanking, CompActRankTypeDefineIndexDict, SuperbossPointRanking, YestordaySuperbossPointRanking, \
    SbossPointRankTypeDefineIndexDict, LastSbossPointRankTypeDefineIndexDict, SbossRankDefineIdxBigRoomIdDict
from newfish.entity.mail_system import MailRewardType


def getAllTabs(userId):
    """
    获取所有可以显示的排行榜
    """
    confs = []
    isVerLimit = util.isVersionLimit(userId)


def getRankingInfoByType(userId, clientId, rankType, httpRequest=False):
    """通过排行榜类型获取排行榜信息"""
    rankClass = _getRankingClass(rankType, userId, clientId, httpRequest)
    return rankClass.getRankingInfo() if rankClass else {}


def getRankingTabs(userId, clientId, rankType, httpRequest=False):
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






def refreshGrandPrixPoint(userId, userPoint):
    """
    刷新大奖赛日榜和周榜
    """
    rankClass = _getRankingClass(RankType.TodayGrandPrix, userId, CLIENTID_ROBOT)
    userPointData = [userId, userPoint]
    rankClass.refreshRankingData(userPointData)

    rankClass = _getRankingClass(RankType.WeekGrandPrix, userId, CLIENTID_ROBOT)
    rankClass.refreshRankingData(userPointData)


def _getRankingClass(rankType, userId, clientId=None, httpRequest=False):
    """获取排行榜的类"""
    rankClass = None
    if rankType == RankType.TodayStarfish:  # 海星收集榜
        rankClass = TodayStarfishRanking(userId, rankType, RankDefineIndex.Starfish, clientId, httpRequest,
                                         MailRewardType.StarRank)
    elif rankType == RankType.LastStarfish:  # 昨日海星榜
        rankClass = YesterdayStarfishRanking(userId, rankType, RankDefineIndex.Starfish, clientId, httpRequest,
                                             MailRewardType.StarRank)
    elif rankType == RankType.Bullet:  # 招财珠榜
        rankClass = BulletRanking(userId, rankType, RankDefineIndex.Bullet, clientId, httpRequest)
    elif rankType == RankType.TodayLucky:  # 每日幸运榜
        rankClass = TodayLuckyRanking(userId, rankType, RankDefineIndex.TodayLucky, clientId, httpRequest)
    elif rankType == RankType.WeekLucky:  # 7日幸运榜
        rankClass = WeekLuckyRanking(userId, rankType, RankDefineIndex.WeekLucky, clientId, httpRequest)
    elif rankType == RankType.TodayWinner:  # 招财今日赢家榜
        rankClass = TodayRobberyRanking(userId, rankType, RankDefineIndex.RobberyWinner, clientId, httpRequest,
                                        MailRewardType.RobberyRank)
    elif rankType == RankType.LastWinner:  # 招财昨日赢家榜
        rankClass = YestodayRobberyRanking(userId, rankType, RankDefineIndex.RobberyWinner, clientId, httpRequest,
                                           MailRewardType.RobberyRank)
    elif rankType == RankType.WeekWinner:  # 招财七日赢家榜
        rankClass = WeekRobberyRanking(userId, rankType, RankDefineIndex.WeekWinner, clientId, httpRequest)
    # elif rankType == RankType.RedReward:   # 万元红包发奖（已废弃）
    #     rankClass = RedRewardRank(userId, rankType, RankDefineIndex.ThousandRed, clientId, httpRequest)
    elif rankType == RankType.XiuXianMatch:  # 休闲回馈赛
        rankClass = MatchRanking(userId, rankType, RankDefineIndex.Match44104, clientId, httpRequest)
    elif rankType == RankType.ChuJiMatch:  # 初级回馈赛
        rankClass = MatchRanking(userId, rankType, RankDefineIndex.Match44101, clientId, httpRequest)
    elif rankType == RankType.ZhongJiMatch:  # 中级回馈赛
        rankClass = MatchRanking(userId, rankType, RankDefineIndex.Match44102, clientId, httpRequest)
    elif rankType == RankType.GaoJiMatch:  # 高级回馈赛
        rankClass = MatchRanking(userId, rankType, RankDefineIndex.Match44103, clientId, httpRequest)
    elif rankType == RankType.SlotMachine:  # 老虎机活动积分榜
        rankClass = SlotMachineIntegralRanking(userId, rankType, RankDefineIndex.SlotMachine, clientId, httpRequest,
                                               MailRewardType.SystemReward)
    elif rankType == RankType.MoneyTree:  # 摇钱树活动摇动次数榜
        rankClass = MoneyTreeRanking(userId, rankType, RankDefineIndex.MoneyTree, clientId, httpRequest,
                                     MailRewardType.SystemReward)
    elif rankType == RankType.TodayGrandPrix:  # 大奖赛积分榜
        rankClass = TodayGrandPrixRanking(userId, rankType, RankDefineIndex.GrandPrix, clientId, httpRequest,
                                          MailRewardType.SystemReward)
    elif rankType == RankType.LastGrandPrix:  # 大奖赛昨日榜
        rankClass = YestodayGrandPrixRanking(userId, rankType, RankDefineIndex.GrandPrix, clientId, httpRequest)
    elif rankType == RankType.WeekGrandPrix:  # 大奖赛积分周榜
        rankClass = WeekGrandPrixRanking(userId, rankType, RankDefineIndex.WeekGrandPrix, clientId, httpRequest,
                                         MailRewardType.SystemReward)
    elif rankType == RankType.ProfitCoin:  # 玩家盈利榜
        rankClass = ProfitCoinRanking(userId, rankType, RankDefineIndex.ProfitCoin, clientId, httpRequest)
    elif rankType == RankType.FestivalTurntable:  # 节日转盘抽大奖积分榜
        rankClass = FestivalTurntableIntegralRanking(userId, rankType, RankDefineIndex.FestivalTurntable, clientId,
                                                     httpRequest, MailRewardType.ActivityReward)
    elif rankType == RankType.MagicCrystal:  # 魔晶收集榜
        rankClass = TodayRankingBase(userId, rankType, RankDefineIndex.MagicCrystal, clientId, httpRequest)
    elif rankType == RankType.CollectItem:  # 收集xx道具榜(集兔耳赢奖励)
        rankClass = CollectItemRanking(userId, rankType, RankDefineIndex.CollectItem, clientId, httpRequest,
                                       MailRewardType.ActivityReward)
    elif rankType == RankType.PoseidonTodayWinner:  # 海皇今日赢家榜
        rankClass = TodayPoseidonRanking(userId, rankType, RankDefineIndex.PoseidonWinner, clientId, httpRequest,
                                         MailRewardType.PoseidonRank)
    elif rankType == RankType.PoseidonLastWinner:  # 海皇昨日赢家榜
        rankClass = YestodayPoseidonRanking(userId, rankType, RankDefineIndex.PoseidonWinner, clientId, httpRequest,
                                            MailRewardType.PoseidonRank)
    elif rankType == RankType.PoseidonWeekWinner:  # 海皇七日赢家榜
        rankClass = WeekPoseidonRanking(userId, rankType, RankDefineIndex.PoseidonWeekWinner, clientId, httpRequest)
    elif rankType in CompActRankTypeDefineIndexDict:  # 竞赛活动Team积分榜
        rankClass = CompActTeamRanking(userId, rankType, CompActRankTypeDefineIndexDict[rankType], clientId,
                                       httpRequest, MailRewardType.ActivityReward)
    elif rankType == RankType.CompActPoint:  # 竞赛活动积分排行榜
        rankClass = CompActPointRanking(userId, rankType, RankDefineIndex.CompActPoint, clientId, httpRequest)
    elif rankType == RankType.LastCompActWinner:  # 上期竞赛冠军榜
        from newfish.entity.fishactivity import competition_activity
        lastRankType = competition_activity.getLastChampionTeamRankType()
        if lastRankType in CompActRankTypeDefineIndexDict:
            rankClass = YestordayCompActTeamRanking(userId, rankType, CompActRankTypeDefineIndexDict[lastRankType],
                                                    clientId, httpRequest, MailRewardType.ActivityReward)
    elif rankType in SbossPointRankTypeDefineIndexDict:  # 超级boss积分排行榜
        rankClass = SuperbossPointRanking(userId, rankType, SbossPointRankTypeDefineIndexDict[rankType], clientId,
                                          httpRequest)
    elif rankType in LastSbossPointRankTypeDefineIndexDict:  # 上期超级boss积分排行榜
        rankClass = YestordaySuperbossPointRanking(userId, rankType, LastSbossPointRankTypeDefineIndexDict[rankType],
                                                   clientId, httpRequest)
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
    pass