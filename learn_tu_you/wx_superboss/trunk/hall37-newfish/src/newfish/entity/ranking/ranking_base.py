#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/30

import time
import copy
import math
import random
import json
from datetime import date, datetime, timedelta

import freetime.util.log as ftlog
from poker.util import strutil
import poker.util.timestamp as pktimestamp
from poker.entity.biz import bireport
from poker.entity.dao import userdata, gamedata, daobase
from poker.entity.configure import gdata
from hall.entity.hallconf import HALL_GAMEID
from hall.entity import hallranking, hallconf, hallvip, hallitem
from newfish.entity import config, util, weakdata
from newfish.entity.config import CLIENTID_ROBOT, FISH_GAMEID, \
    BRONZE_BULLET_KINDID, SILVER_BULLET_KINDID, GOLD_BULLET_KINDID, \
    CHIP_KINDID, COUPON_KINDID, BULLET_KINDIDS, BULLET_VALUE
from newfish.entity.redis_keys import GameData, WeakData, UserData
from newfish.entity.event import BulletChangeEvent, RankOverEvent
from newfish.entity import mail_system, robbery_lottery_pool, poseidon_lottery_pool
from newfish.entity.honor import honor_system
from newfish.entity.fishactivity import fish_activity_system
from newfish.entity.mail_system import MailRewardType


cacheRankings = {}
historyCacheRankings = {}
processedRankings = []
SevenRankExpireTime = 7 * 24 * 60 * 60



# 排行榜在9999/ranking/0.json配置下的index
class RankDefineIndex:
    GrandPrix = 14          # 大奖赛积分榜


# 44/rankReward/0.json文件中的key
class RankType:
    TodayStarfish = 1       # 海星收集榜
    TodayGrandPrix = 16     # 大奖赛今日榜
    LastGrandPrix = 17      # 大奖赛昨日榜
    WeekGrandPrix = 18      # 大奖赛周榜


class RankingBase(object):

    def __init__(self, userId, rankType, defineIndex, clientId=None, httpRequest=False, mailType=MailRewardType.SystemReward):
        self.userId = userId
        self.rankType = rankType
        self.httpRequest = httpRequest
        self.rankDefineIndex = defineIndex                                  # 排行榜在9999/ranking/0.json配置下的index
        self.rankDefine = self._getRankingDefine(defineIndex, clientId)     # 大厅排行榜中配置的数据
        self.rankConf = config.getRankRewardConf(rankType)                  # 排行榜发奖的配置
        # 排行榜发奖的时间
        self.sendRewardTimeStr = self.rankConf.get("sendRewardTime", "00:00")
        self.sendRewardTimeInt = self.timeStrToInt(self.sendRewardTimeStr)
        # 排行榜更新的时间
        self.updateRankTimeStr = self.rankConf.get("updateRankTime", "00:00")
        self.updateRankTimeInt = self.timeStrToInt(self.updateRankTimeStr)
        self.clearDataTime = self.rankConf.get("clearDataTime", "00:00")
        self.mailType = mailType
        self.lang = util.getLanguage(userId)
        self.enableSortRank = True

    def _getRankingInfo(self):
        """
        获取排行榜相关数据
        """
        ftlog.debug("getRankingTabs->getRanking userId=", self.userId, "rankType=", self.rankType, "rankingIds=", self.rankDefine.rankingId)
        ranking = {}
        rankRewardConf = self.rankConf
        ranking["order"] = self.rankType
        ranking["rankType"] = self.rankType
        rankingNameId = rankRewardConf.get("rankName")
        ranking["rankName"] = config.getMultiLangTextConf(str(rankingNameId), lang=self.lang)
        rankingDescId = rankRewardConf.get("rankDesc")
        if rankingDescId:
            ranking["rankDesc"] = config.getMultiLangTextConf(str(rankingDescId), lang=self.lang)
        cacheRanking = self.getRanking(self._getRankTimestamp())

    def getRanking(self, timestamp=None, refresh=False):
        """
        @return: (TYRankingList, timestamp, rankingList)
        获取榜单数据
        """
        global cacheRankings
        if not timestamp:
            timestamp = pktimestamp.getCurrentTimestamp()
        cacheRanking = cacheRankings.get(self.rankDefine.rankingId)
        rankRewardConf = self.rankConf
        if cacheRanking:
            ftlog.debug("cacheRanking rankingDefine cacheTimes:", cacheRanking[0].rankingDefine.cacheTimes)
        # 更新排行榜缓存.
        if (refresh or not cacheRanking or (int(time.time()) - cacheRanking[1]) >= rankRewardConf.get("cacheTime", 0) or
                pktimestamp.getDayStartTimestamp(timestamp) != pktimestamp.getDayStartTimestamp(cacheRanking[1])):
            cacheRanking = self._getRanking(timestamp)
            pass








    def timeStrToInt(self, strTime):
        """
        "xx:xx"转成对应秒数
        """
        sendTimeArr = strTime.split(":")
        intTime = int(sendTimeArr[0]) * 3600 + int(sendTimeArr[1]) * 60
        return intTime

    # 获取排行榜时的时间戳
    def _getRankTimestamp(self):
        return None

    def _getRankingDefine(self, defineIndex, clientId):
        """
        获取9999/ranking数值信息
        :param defineIndex: 排行榜在9999/ranking配置下的index
        :param clientId:
        :return: 9999/ranking的数值配置
        """
        clientId = clientId or CLIENTID_ROBOT
        rankingKey = "fish_44"
        templateName = hallconf.getClientRankTemplateName(rankingKey, clientId) or 'default'
        rankingDefines = hallranking.rankingSystem.getRankingDefinesForRankingKey(rankingKey, templateName)
        return rankingDefines[defineIndex]







    def _getRanking(self, timestamp):
        """
        获取所有用户排行榜数据
        :param rankingDefine: 数值配置
        :param timestamp: 时间戳
        :return:  排行榜所有数据
        """
        rankingList = self.getTopNRankUsers(timestamp)
        bonusPool = 0
        superbossPool = 0

    def getTopNRankUsers(self, _timestamp, _rankDefine=None):
        """
        获取topN玩家列表
        """
        rankingList = self._getTopN(_timestamp, _rankDefine)
        pass

    def _getTopN(self, _timestamp, _rankDefine=None, cnt=None):
        pass



class TodayGrandPrixRanking(RankingBase):
    """
    大奖赛积分榜
    """
    pass


