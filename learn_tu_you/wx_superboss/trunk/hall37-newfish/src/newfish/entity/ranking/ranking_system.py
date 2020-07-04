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
from newfish.entity.ranking.ranking_base import RankType


from newfish.entity.mail_system import MailRewardType



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
    if rankType == RankType.TodayStarfish:      # 海星收集榜
        rankClass = TodayStarfishRanking(userId, rankType, RankDefineIndex.Starfish, clientId, httpRequest, MailRewardType.StarRank)
    elif rankType == RankType.TodayGrandPrix:
        rankClass = TodayGrandPrixRanking(userId, rankType, RankDefineIndex.GrandPrix, clientId, httpRequest, MailRewardType.SystemReward)
    elif rankType == RankType.LastGrandPrix:    # 大奖赛昨日榜
        rankClass = YestodayGrandPrixRanking(userId, rankType, RankDefineIndex.GrandPrix, clientId, httpRequest)
    elif rankType == RankType.WeekGrandPrix:    # 大奖赛积分周榜
        rankClass = WeekGrandPrixRanking(userId, rankType, RankDefineIndex.WeekGrandPrix, clientId, httpRequest, MailRewardType.SystemReward)

    return rankClass


def getUserRankAndRewards(rankType, userId):
    """
    获取玩家排行榜排名和排名奖励
    """
    rankClass = _getRankingClass(rankType, userId, CLIENTID_ROBOT)
    rank = rankClass.getTopNUserRank(userId, rankClass._getOwnRankingTime())
    rankRewards = rankClass._getOneUserReward(userId, rank)
    return rank, rankRewards