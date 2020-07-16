# -*- coding=utf-8 -*-
"""
Created by hhx on 18/03/15.
"""
import time
import copy
import math
import json
from datetime import date, datetime, timedelta

import freetime.util.log as ftlog
from poker.util import strutil
import poker.util.timestamp as pktimestamp
from poker.entity.biz import bireport
from poker.entity.dao import userdata, gamedata, daobase
from poker.entity.configure import gdata
from hall.entity.hallconf import HALL_GAMEID
from hall.entity import hallranking, hallconf, hallitem
from newfish.entity import config, util, weakdata
from newfish.entity.config import CLIENTID_ROBOT, FISH_GAMEID, \
    BRONZE_BULLET_KINDID, SILVER_BULLET_KINDID, GOLD_BULLET_KINDID, \
    CHIP_KINDID, COUPON_KINDID, BULLET_KINDIDS
from newfish.entity.redis_keys import GameData, WeakData, UserData
from newfish.entity.event import BulletChangeEvent, RankOverEvent
from newfish.entity import mail_system
from newfish.entity.lotterypool import poseidon_lottery_pool, robbery_lottery_pool
from newfish.entity.fishactivity import fish_activity_system
from newfish.entity.mail_system import MailRewardType


cacheRankings = {}                              # 缓存排行榜
historyCacheRankings = {}                       # 获取历史榜单
processedRankings = []                          # 保存发过奖励的key [110044029_20200714、...、]
SevenRankExpireTime = 7 * 24 * 60 * 60



# 排行榜在9999/ranking/0.json配置下的index
class RankDefineIndex:
    Starfish = 0        # 海星收集榜
    Bullet = 1          # 招财珠榜
    TodayLucky = 2      # 幸运玩家榜
    WeekLucky = 3       # 七日幸运榜
    ThousandRed = 4     # 万元红包
    RobberyWinner = 5   # 招财今日赢家榜昨日赢家榜
    WeekWinner = 6      # 七日赢家榜
    Match44104 = 8      # 休闲假日
    Match44101 = 9      # 水上乐园
    Match44102 = 10     # 欢乐竞技
    Match44103 = 11     # 王者争霸
    SlotMachine = 12    # 老虎机积分榜
    MoneyTree = 13      # 摇钱树排行榜
    GrandPrix = 14      # 大奖赛积分榜
    WeekGrandPrix = 15  # 大奖赛积分周榜
    ProfitCoin = 16     # 玩家盈利榜
    FestivalTurntable = 17  # 节日转盘抽大奖积分排行榜
    MagicCrystal = 18   # 魔晶收集榜
    CollectItem = 19    # 活动中收集xx道具榜
    PoseidonWinner = 20 # 海皇今日赢家榜昨日赢家榜
    PoseidonWeekWinner = 21  # 海皇七日赢家榜
    CompActT1 = 22      # 竞赛Team1积分榜
    CompActT2 = 23      # 竞赛Team2积分榜
    CompActT3 = 24      # 竞赛Team3积分榜
    CompActT4 = 25      # 竞赛Team4积分榜
    CompActT5 = 26      # 竞赛Team5积分榜
    CompActPoint = 27   # 竞赛积分榜
    SBossBox = 28       # 宝箱怪积分金币榜
    SBossOctopus = 29   # 章鱼积分金币榜
    SBossQueen = 30     # 龙女王积分金币榜
    SBossDragon = 31    # 冰龙积分金币榜
    SBossBoxRing = 32       # 宝箱怪积分金环榜
    SBossOctopusRing = 33   # 章鱼积分金环榜
    SBossQueenRing = 34    # 龙女王积分金环榜
    SBossDragonRing = 35    # 冰龙积分金环榜


# 44/rankReward/0.json文件中的key
class RankType:
    TodayStarfish = 1   # 海星收集榜
    LastStarfish = 2    # 上期海星榜
    Bullet = 3          # 招财珠榜
    ChuJiMatch = 4      # 初级回馈赛榜
    ZhongJiMatch = 5    # 中级回馈赛榜
    GaoJiMatch = 6      # 高级回馈赛榜
    XiuXianMatch = 7    # 休闲回馈赛榜
    TodayLucky = 8      # 幸运玩家榜
    WeekLucky = 9       # 七日幸运榜
    TodayWinner = 10    # 招财今日赢家榜
    LastWinner = 11     # 招财昨日赢家榜
    WeekWinner = 12     # 招财七日赢家榜
    RedReward = 13      # 万元红包
    SlotMachine = 14    # 老虎机积分榜
    MoneyTree = 15      # 摇钱树排行榜
    TodayGrandPrix = 16 # 大奖赛今日榜
    LastGrandPrix = 17  # 大奖赛昨日榜
    WeekGrandPrix = 18  # 大奖赛周榜
    ProfitCoin = 19     # 玩家盈利榜
    FestivalTurntable = 20      # 节日转盘抽大奖积分排行榜
    MagicCrystal = 21   # 魔晶收集榜
    CollectItem = 22    # 活动中收集xx道具榜
    PoseidonTodayWinner = 23    # 海皇来袭今日赢家榜
    PoseidonLastWinner = 24     # 海皇来袭昨日赢家榜
    PoseidonWeekWinner = 25     # 海皇来袭七日赢家榜
    CompActT1 = 26      # 竞赛Team1积分榜
    CompActT2 = 27      # 竞赛Team2积分榜
    CompActT3 = 28      # 竞赛Team3积分榜
    CompActT4 = 29      # 竞赛Team4积分榜
    CompActT5 = 30      # 竞赛Team5积分榜
    CompActPoint = 31   # 竞赛积分榜
    LastCompActWinner = 32      # 上期竞赛冠军榜
    SBossBox = 33               # 宝箱怪积分金币榜
    LastSBossBox = 34           # 上期宝箱怪积分金币榜
    SBossOctopus = 35           # 章鱼积分金币榜
    LastSBossOctopus = 36       # 上期章鱼积分金币榜
    SBossQueen = 37             # 龙女王积分金币榜
    LastSBossQueen = 38         # 上期龙女王积分金币榜
    SBossDragon = 39            # 冰龙积分金币榜
    LastSBossDragon = 40        # 上期冰龙积分金币榜
    SBossBoxRing = 41               # 宝箱怪积分金环榜
    LastSBossBoxRing = 42           # 上期宝箱怪积分金环榜
    SBossOctopusRing = 43           # 章鱼积分金环榜
    LastSBossOctopusRing = 44       # 上期章鱼积分金环榜
    SBossQueenRing = 45             # 龙女王积分金环榜
    LastSBossQueenRing = 46         # 上期龙女王积分金环榜
    SBossDragonRing = 47            # 冰龙积分金环榜
    LastSBossDragonRing = 48        # 上期冰龙积分金环榜


# 竞赛相关排行榜对应关系
CompActRankTypeDefineIndexDict = {
    RankType.CompActT1: RankDefineIndex.CompActT1,
    RankType.CompActT2: RankDefineIndex.CompActT2,
    RankType.CompActT3: RankDefineIndex.CompActT3,
    RankType.CompActT4: RankDefineIndex.CompActT4,
    RankType.CompActT5: RankDefineIndex.CompActT5
}

# 超级boss相关积分排行榜对应关系
SbossPointRankTypeDefineIndexDict = {
    RankType.SBossBox: RankDefineIndex.SBossBox,                        # 宝箱怪积分金币榜
    RankType.SBossOctopus: RankDefineIndex.SBossOctopus,                # 章鱼积分金币榜
    RankType.SBossQueen: RankDefineIndex.SBossQueen,
    RankType.SBossDragon: RankDefineIndex.SBossDragon,
    RankType.SBossBoxRing: RankDefineIndex.SBossBoxRing,
    RankType.SBossOctopusRing: RankDefineIndex.SBossOctopusRing,
    RankType.SBossQueenRing: RankDefineIndex.SBossQueenRing,
    RankType.SBossDragonRing: RankDefineIndex.SBossDragonRing
}

# 上期超级boss相关积分排行榜对应关系
LastSbossPointRankTypeDefineIndexDict = {
    RankType.LastSBossBox: RankDefineIndex.SBossBox,
    RankType.LastSBossOctopus: RankDefineIndex.SBossOctopus,
    RankType.LastSBossQueen: RankDefineIndex.SBossQueen,
    RankType.LastSBossDragon: RankDefineIndex.SBossDragon,
    RankType.LastSBossBoxRing: RankDefineIndex.SBossBoxRing,
    RankType.LastSBossOctopusRing: RankDefineIndex.SBossOctopusRing,
    RankType.LastSBossQueenRing: RankDefineIndex.SBossQueenRing,
    RankType.LastSBossDragonRing: RankDefineIndex.SBossDragonRing
}

# 超级bossdefineIdx与bigRoomId对应关系
SbossRankDefineIdxBigRoomIdDict = {
    RankDefineIndex.SBossBox: 44411,
    RankDefineIndex.SBossOctopus: 44412,
    RankDefineIndex.SBossQueen: 44414,
    RankDefineIndex.SBossDragon: 44415,
    RankDefineIndex.SBossBoxRing: 44411,
    RankDefineIndex.SBossOctopusRing: 44412,
    RankDefineIndex.SBossQueenRing: 44414,
    RankDefineIndex.SBossDragonRing: 44415
}

# 超级boss相关积分金环排行榜
SbossPointRankTypeRingList = {
    RankType.LastSBossBoxRing,
    RankType.LastSBossOctopusRing,
    RankType.LastSBossQueenRing,
    RankType.LastSBossDragonRing,
    RankType.SBossBoxRing,
    RankType.SBossOctopusRing,
    RankType.SBossQueenRing,
    RankType.SBossDragonRing
}


# 竞赛活动team排行榜列表
CompActRankList = [RankType.CompActT1, RankType.CompActT2, RankType.CompActT3, RankType.CompActT4, RankType.CompActT5]
# 竞赛队伍数量.
TOTAL_COMP_TEAM_CNT = 5


class RankingBase(object):

    def __init__(self, userId, rankType, defineIndex, clientId=None, httpRequest=False, mailType=MailRewardType.SystemReward):
        self.userId = userId
        self.rankType = rankType
        self.httpRequest = httpRequest
        self.rankDefineIndex = defineIndex                                  # 排行榜在9999/ranking/0.json配置下的index
        self.rankDefine = self._getRankingDefine(defineIndex, clientId)     # 大厅排行榜中配置的数据
        self.rankConf = config.getRankRewardConf(rankType)                  # 排行榜发奖的配置
        self.sendRewardTimeStr = self.rankConf.get("sendRewardTime", "00:00")
        self.sendRewardTimeInt = self.timeStrToInt(self.sendRewardTimeStr)  # 排行榜发奖的时间
        self.updateRankTimeStr = self.rankConf.get("updateRankTime", "00:00")
        self.updateRankTimeInt = self.timeStrToInt(self.updateRankTimeStr)  # 排行榜更新的时间
        self.clearDataTime = self.rankConf.get("clearDataTime", "00:00")    # 排行榜清理时间
        self.mailType = mailType
        self.lang = util.getLanguage(userId)
        self.enableSortRank = True                                          # 排序

    def getRankingInfo(self):
        """
        获取排行榜相关数据
        """
        ftlog.debug("getRankingTabs->getRanking userId=", self.userId, "rankType=", self.rankType, "rankingIds=", self.rankDefine.rankingId)
        ranking = {}
        rankRewardConf = self.rankConf
        ranking["order"] = self.rankType
        ranking["rankType"] = self.rankType
        ranking["rankName"] = config.getMultiLangTextConf(str(rankRewardConf.get("rankName")), lang=self.lang)
        if rankRewardConf.get("rankDesc"):
            ranking["rankDesc"] = config.getMultiLangTextConf(str(rankRewardConf.get("rankDesc")), lang=self.lang)
        cacheRanking = self.getRanking(self._getRankTimestamp())
        cacheRanking = copy.deepcopy(cacheRanking[2])
        ownRanking = self._getOwnRanking(self.userId, cacheRanking["rankData"])                 # 自己的排名信息
        cacheRanking["rankData"].insert(0, ownRanking)                                          # 排名信息在第一位
        ranking["rankData"] = cacheRanking["rankData"]                                          # 排名详细数据
        ranking["lotteryPool"] = cacheRanking["bonusPool"]                                      # 奖池
        ranking["bonusPool"] = cacheRanking["bonusPool"]                                        # 奖池
        ranking["superbossPool"] = cacheRanking["superbossPool"]                                # 超级奖池
        return ranking

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
            if cacheRanking:
                cacheRankings[self.rankDefine.rankingId] = cacheRanking
                ftlog.debug(
                    "getRanking->getRanking userId=", self.userId, "rankingId=", self.rankDefine.rankingId,
                    "rankingIssueNumber=", cacheRanking[0].issueNumber,
                    "rankingCycle=", ("[%s,%s)" % (cacheRanking[0].timeCycle.startTime, cacheRanking[0].timeCycle.endTime)),
                    "timestamp=", datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                    "data=", cacheRanking[2]
                )
            else:
                if self.rankDefine.rankingId in cacheRankings:
                    del cacheRankings[self.rankDefine.rankingId]
                    ftlog.debug("getRanking->getRanking remove userId=", self.userId, "rankingId=", self.rankDefine.rankingId)
        return cacheRanking

    def _getProcessedKey(self, todayDate):
        """
        获取发奖完成标识
        """
        return "%s_%s" % (self.rankDefine.rankingId, todayDate)

    def processRanking(self, todayDate, strfTime):
        """处理排行榜发奖"""
        pass

    def refreshRankingData(self, event):
        """刷新排行榜数据"""
        pass

    def _getRankTimestamp(self):
        """获取排行榜时的时间戳"""
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
        templateName = hallconf.getClientRankTemplateName(rankingKey, clientId) or "default"
        rankingDefines = hallranking.rankingSystem.getRankingDefinesForRankingKey(rankingKey, templateName)
        return rankingDefines[defineIndex]

    def _getHistoryTimeAndUpdate(self, historyCacheRanking, currentTimestamp, yesterday):
        """
        获取历史榜单的时间戳和判断是否需要更新历史榜单 historyCacheRanking (TYRankingList, timestamp, rankingList)
        """
        timestamp = pktimestamp.getDayStartTimestamp(time.mktime(yesterday.timetuple()))
        if historyCacheRanking:
            isUpdate = pktimestamp.getDayStartTimestamp(currentTimestamp) != pktimestamp.getDayStartTimestamp(historyCacheRanking[1])
        else:
            isUpdate = True
        return timestamp, isUpdate

    def _getHistoryRanking(self):
        """
        获取历史榜单
        """
        global historyCacheRankings
        currentTimestamp = pktimestamp.getCurrentTimestamp()
        timestamp = currentTimestamp
        dateArray = datetime.fromtimestamp(timestamp)
        yesterday = dateArray - timedelta(days=1)
        historyCacheRanking = historyCacheRankings.get(self.rankDefine.rankingId)
        timestamp, isUpdate = self._getHistoryTimeAndUpdate(historyCacheRanking, currentTimestamp, yesterday)   # 获取历史榜单的时间戳和判断是否需要更新历史榜单
        if isUpdate:                                                                    # 更新历史榜单
            historyCacheRanking = self._getRanking(timestamp)
            if historyCacheRanking:
                historyCacheRankings[self.rankDefine.rankingId] = historyCacheRanking
                ftlog.debug(
                    "getHistoryRanking userId=", self.userId,                           # 116002
                    "rankingId=", self.rankDefine.rankingId,                            # 110044029
                    "rankingIssueNumber=", historyCacheRanking[0].issueNumber,          # 20200714
                    "rankingCycle=", ("[%s,%s)" % (historyCacheRanking[0].timeCycle.startTime, historyCacheRanking[0].timeCycle.endTime)),  # [1594656000,1594742400)
                    "timestamp=", datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"),  # 2020-07-14 15:32:35
                    "data=", historyCacheRanking[2]                                     # 排行榜数据
                )
            else:
                if self.rankDefine.rankingId in historyCacheRankings:
                    del historyCacheRankings[self.rankDefine.rankingId]
                    ftlog.debug("getHistoryRanking remove userId=", self.userId, "rankingId=", self.rankDefine.rankingId)
        return historyCacheRanking

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
        if self.rankType in [RankType.TodayWinner, RankType.LastWinner]:                    # 招财今日赢家榜、招财昨日赢家榜
            bonusPool = robbery_lottery_pool.getRobberyWealthPool((self.rankType == RankType.LastWinner))
        elif self.rankType in [RankType.PoseidonTodayWinner, RankType.PoseidonLastWinner]:  # 海皇来袭今日赢家榜
            bonusPool = poseidon_lottery_pool.getPoseidonWealthPool(self.rankType == RankType.PoseidonLastWinner)
        bigRoomId = SbossRankDefineIdxBigRoomIdDict.get(self.rankDefineIndex)
        if self.rankType in SbossPointRankTypeDefineIndexDict.keys() and bigRoomId:         # 超级boss相关积分排行榜对应关系
            from newfish.entity.superboss import gameplay
            mode = 1 if self.rankType in SbossPointRankTypeRingList else 0
            superbossPool = gameplay.getSuperbossBonusPool(bigRoomId, mode)
        elif self.rankType in LastSbossPointRankTypeDefineIndexDict.keys() and bigRoomId:   # 上期超级boss相关积分排行榜对应关系
            from newfish.entity.superboss import gameplay
            mode = 1 if self.rankType in SbossPointRankTypeRingList else 0
            superbossPool = gameplay.getSuperbossBonusPool(bigRoomId, timestamp, mode)
        rankData = []
        if ftlog.is_debug():
            ftlog.debug("_getRanking, rankType =", self.rankType, "rankingList =", len(rankingList.rankingUserList))
        for index, user in enumerate(rankingList.rankingUserList):
            if user.userId == 0:
                continue
            name = util.getNickname(user.userId)
            sex, avatar = userdata.getAttrs(user.userId, ["sex", "purl"])
            score = self._getOneUserScore(user.userId, user.score)                                  # 获取排名积分
            rewards = self._getOneUserReward(user.userId, user.rank + 1, bonusPool, user.score)     # 获取排名的奖励
            vipLevel = util.getVipShowLevel(user.userId)
            oneUserRankData = {
                "userId": user.userId,
                "name": name,
                "sex": sex,
                "score": score,
                "rank": user.rank + 1,
                "avatar": avatar,
                "vip": vipLevel,
                "rewards": rewards
            }
            rankData.append(oneUserRankData)

        return (rankingList, int(time.time()), {                # 获取topN玩家列表、时间
            "rankId": self.rankDefine.rankingId,                # 大厅排行榜Id
            "issueNum": rankingList.issueNumber,                #
            "name": rankingList.rankingDefine.name,             # 大厅排行榜名
            "desc": rankingList.rankingDefine.desc,             # 排行榜描述
            "type": rankingList.rankingDefine.rankingType,      # 排行榜类型
            "rankData": rankData,                               # 排行榜数据
            "bonusPool": bonusPool,                             # 奖池
            "superbossPool": superbossPool                      # 超级奖池
        })

    def getTopNRankUsers(self, _timestamp, _rankDefine=None):
        """
        获取topN玩家列表
        """
        rankingList = self._getTopN(_timestamp, _rankDefine)
        for index, user in enumerate(rankingList.rankingUserList):
            user.rank = index                                                           # 玩家排名
        return rankingList

    def getTotalNRankUsers(self, _timestamp, _rankDefine):
        """
        获取totalN玩家列表
        """
        rankingList = self._getTopN(_timestamp, _rankDefine, _rankDefine.totalN)
        for index, user in enumerate(rankingList.rankingUserList):
            user.rank = index
        return rankingList

    def getTopNUserRank(self, userId, _timestamp, _rankDefine=None):
        """
        获取指定玩家排名
        """
        rankingList = self._getTopN(_timestamp, _rankDefine)
        for index, user in enumerate(rankingList.rankingUserList):
            if user.userId == userId:
                return index + 1
        return 0

    def _getTopN(self, _timestamp, _rankDefine=None, cnt=None):
        """获取前n名"""
        _rankDefine = _rankDefine or self.rankDefine
        # rankingList = hallranking.rankingSystem.getTopN(_rankDefine.rankingId, _rankDefine.totalN, _timestamp)
        cnt = cnt or _rankDefine.topN                   # 排行榜大厅中玩家数量
        rankingList = hallranking.rankingSystem.getTopN(_rankDefine.rankingId, cnt, _timestamp)
        if not rankingList:
            return None
        self.dateTime = util.timestampToStr(_timestamp, "%Y-%m-%d")
        if self.enableSortRank:                                                         # 排行榜数据排序
            rankingList.rankingUserList.sort(cmp=self.sortRankUser)
        # rankingList.rankingUserList = rankingList.rankingUserList[:cnt]
        return rankingList

    def saveUserScore(self, rankingId, userId, score, timestamp):
        """
        保存玩家排行榜分数
        """
        hallranking.rankingSystem.setUserScore(rankingId, userId, score, timestamp)
        score = self._getGameData9999RankInfo(userId)
        util.saveRankInfo(userId, score, rankingId, timestamp, expireTime=self.rankConf.get("expireTime"))  # 保存自己身上的排行榜积分和时间

    def sortRankUser(self, a, b):
        """排序 按照玩家的积分"""
        ret = cmp(a.score, b.score)         # 分数相同
        if ret != 0:                        # 分数不同
            return -ret

        return cmp(self._getRankTimeInfo(a.userId), self._getRankTimeInfo(b.userId))

    def _getRankTimeInfo(self, userId):
        """
        获取最后一次保存的时间戳
        """
        # 2019-xx-xx
        self.dateTime = self.dateTime or date.today()
        key_ = UserData.rankingInfo % (self.rankDefine.rankingId, self.dateTime, FISH_GAMEID, userId)
        scoreTime = daobase.executeUserCmd(userId, "GET", key_) or "{}"
        scoreTime = json.loads(scoreTime)
        return scoreTime.get("time", 0)

    def _getOwnRankingTime(self):
        """获取自身排行榜的时间戳"""
        return pktimestamp.getCurrentTimestamp()

    def _getOwnRanking(self, userId, rankDatas):
        """
        获取指定玩家排名相关数据
        :param userId: 玩家自己userId
        :param rankDatas: 排行榜数据
        :return:
        """
        name = util.getNickname(userId)
        sex, avatar = userdata.getAttrs(userId, ["sex", "purl"])
        rank = 0
        score = 0
        rankData = [rankData for rankData in rankDatas if rankData["userId"] == userId]

        if rankData:
            score = rankData[0]["score"]
            rank = rankData[0]["rank"]
        else:
            rankData = hallranking.rankingSystem.getRankingUser(self.rankDefine.rankingId, userId, self._getOwnRankingTime())
            if rankData and rankData.rank is not None:
                score = rankData.score
                rank = self.getTopNUserRank(userId, self._getOwnRankingTime(), self.rankDefine) \
                    if rankData.rank <= self.rankDefine.totalN else rankData.rank + 1               # 50名以外自己去排行榜取数据

        score = self._getOneUserScore(userId, score, True)
        rewards = self._getOneUserReward(userId, rank)
        vipLevel = util.getVipShowLevel(userId)
        ownRankingDataDic = {
            "userId": userId,
            "name": name,
            "sex": sex,
            "score": score,
            "rank": rank,
            "avatar": avatar,
            "vip": vipLevel,
            "rewards": rewards
        }
        return ownRankingDataDic

    def _getOneUserScore(self, userId, score, isOwner=False):
        """获取一个玩家的排行榜积分"""
        if score:
            return score
        else:
            return 0

    def _getOneUserReward(self, userId, rank, poolNum=0, score=0):
        """
        获取排名对应奖励
        """
        rewards = []
        rankRewards = self._getRankRewards(rank)                                    # 获取排名奖励
        if rankRewards and rankRewards["rewards"]:
            rewards = self._buildRewards(rankRewards["rewards"])                    # 处理奖励格式
        return rewards

    def _getRankRewards(self, rank, rankType=None):
        """
        获取排名奖励
        :param rank: 玩家排名
        :return: 奖励
        """
        rankType = rankType or self.rankType
        rankRewardConf = config.getRankRewardConf(rankType)                         # 获取排名奖励配置表
        rankRewardsList = rankRewardConf.get("rankRewards")
        if rankRewardsList:
            for rankRewards in rankRewardsList:
                if rankRewards["ranking"]["start"] <= rank <= rankRewards["ranking"]["end"]:
                    return rankRewards
        return None

    def _buildRewards(self, rewardList):
        """
        处理奖励格式
        """
        rewards = []
        for r in rewardList:
            assetKind = hallitem.itemSystem.findAssetKind(r["itemId"])
            if r["count"] > 0 and assetKind:
                rewards.append({
                    "name": assetKind.displayName,                                  # 奖励道具名
                    "kindId": assetKind.kindId,                                     # 奖励道具Id
                    "num": r["count"],                                              # 数量
                    "unit": assetKind.units,                                        #
                    "desc": assetKind.displayName + "x" + str(r["count"]) + assetKind.units,    # 描述
                    "img": assetKind.pic                                            # 图片
                })
        return rewards

    def _sendRewards(self, rankData, rankType, rankRewards=None):
        """
        发送排行榜奖励
        """
        ftlog.debug("_sendRewards, ", rankType, self.rankType, self.mailType, self.rankDefine.rankingId)
        if rankType != self.rankType:
            ftlog.error("_sendRewards, ", rankType, self.rankType, self.mailType, self.rankDefine.rankingId)
        userId = rankData["userId"]
        rank = rankData["rank"]
        rankRewards = rankRewards or self._getRankRewards(rank)                     # 获取排名奖励
        if rankRewards and rankRewards["rewards"]:
            rewards = self._getProcessedRewards(rankData, rankRewards)              # 获取处理后的最终奖励
            message = self._getProcessedMessage(rankData, rankRewards)
            if ftlog.is_debug():
                ftlog.debug("_sendRewards->", self.rankType, rewards, message)
            mail_system.sendSystemMail(userId, self.mailType, rewards, message)     # 发送奖励邮件
            self._dealSendRewardsAfter(rankData, userId, rank, rewards)             # 处理完排行榜发奖后的逻辑

    def _getProcessedRewards(self, rankData, rankRewards):
        """
        获取处理后的最终奖励
        """
        rewards = []
        if rankRewards and rankRewards["rewards"]:
            rewards = util.convertToFishItems(rankRewards["rewards"])
        return rewards

    def _getProcessedMessage(self, rankData, rankRewards):
        """
        获取处理后的邮件内容
        """
        userId = rankData["userId"]
        rank = rankData["rank"]
        rankRewardConf = config.getRankRewardConf(self.rankType)
        rankNameId = rankRewardConf["rankName"] # 大奖赛积分榜
        messageId = rankRewards["message"]      # ID_CONFIG_RANKING_MAIL_MSG_UNIVERSAL == 恭喜您在上期\\${rankName}中取得第\\${rank}名，附件内容为您获得的奖励，请您查收！
        lang = util.getLanguage(userId)
        message = config.getMultiLangTextConf(str(messageId), lang=lang)
        params = {"rank": rank, "rankName": config.getMultiLangTextConf(str(rankNameId), lang=lang)}
        message = strutil.replaceParams(message, params)
        return message

    def _dealSendRewardsAfter(self, rankData, userId, rank, rewards):
        """
        处理完排行榜发奖后的逻辑
        """
        self._sendAcRewards(userId, rank, rewards)

    def _sendAcRewards(self, userId, rank, rewards):
        """
        发送活动奖励
        """
        pass

    def timeStrToInt(self, strTime):
        """
        "xx:xx"转成对应秒数
        """
        sendTimeArr = strTime.split(":")
        intTime = int(sendTimeArr[0]) * 3600 + int(sendTimeArr[1]) * 60
        return intTime

    def _getGameData9999RankInfo(self, userId, time_=None):
        """
        获取玩家在排行榜中的分数
        当玩家未上榜时，getRankingUser无法获取到玩家实际排名及分数，但可通过此方法获取分数
        """
        try:
            time_ = time_ or time.time()
            strTime = util.timestampToStr(time_, "%Y%m%d")
            field = "ranking.info:%s" % self.rankDefine.rankingId
            d = gamedata.getGameAttrJson(userId, HALL_GAMEID, field)
            if d and d["issueNumber"] == strTime:                       # 期号20200714
                ftlog.debug("_getGameData9999RankInfo", d["score"])
                return d["score"]
        except:
            ftlog.error()
        return 0

    def _reportBIEvent(self, rankData, param01=0, param02=0):
        """
        上报排名等数据
        """
        try:
            bireport.reportGameEvent(
                "BI_NFISH_GE_RANKING", rankData["userId"], FISH_GAMEID, 0,
                int(self.rankDefine.rankingId), int(rankData["rank"]), 0, int(param01), int(param02),
                [], util.getClientId(rankData["userId"])
            )
        except:
            ftlog.error()

    def _sendRankOverEvent(self, rankData, params=None):
        """发送排行榜结算事件"""
        from newfish.game import TGFish
        event = RankOverEvent(rankData["userId"], FISH_GAMEID, self.rankDefine.rankingId, self.rankType, rankData["rank"], params)
        TGFish.getEventBus().publishEvent(event)


class TodayStarfishRanking(RankingBase):
    """
    海星收集榜
    """
    pass


class YesterdayStarfishRanking(RankingBase):
    """
    昨日海星榜
    """


class BulletRanking(RankingBase):
    """
    弹头榜
    """


class TodayLuckyRanking(RankingBase):
    """
    今日幸运榜
    """
    def _getOneUserScore(self, userId, score, isOwner=False):
        """获取一个玩家的排行榜积分"""
        if isOwner and not score:
            score = weakdata.getDayFishData(userId, WeakData.luckyEggsNum, 0)              # 今日幸运榜金币数
        return score

    def refreshRankingData(self, event):
        """刷新排行榜数据"""
        score = event.coinNum
        self.saveUserScore(config.RANK_DAY_LUCKY, event.userId, score, int(time.time()))


class WeekLuckyRanking(RankingBase):
    """
    七日幸运榜
    """


class TodayRobberyRanking(RankingBase):
    """
    招财今日赢家榜
    """


class YestodayRobberyRanking(TodayRobberyRanking):
    """
    招财昨日赢家榜数据
    """


class WeekRobberyRanking(RankingBase):
    """
    招财七日赢家榜数据
    """


def _getSendRedTime():
    """获取新手玩家的时间 09:00 时间秒数"""
    sendRedTimeStr = config.getCommonValueByKey("sendRedTime")
    sendRedTimeArr = sendRedTimeStr.split(":")                      # 09:00
    rankStartTime = int(sendRedTimeArr[0]) * 3600 + int(sendRedTimeArr[1]) * 60
    return sendRedTimeStr, rankStartTime


def getRedPlayersNumKey():
    """获取新手玩家数量的key"""
    timestamp = pktimestamp.getCurrentTimestamp()
    _, rankStartTime = _getSendRedTime()
    timeStr = date.today()
    diffTime = timestamp - pktimestamp.getDayStartTimestamp(timestamp)
    if diffTime >= rankStartTime:                                   # 时间超过09:00点
        timeStr = date.today() + timedelta(days=1)
    return "redPlayersNum:%d:%s" % (FISH_GAMEID, timeStr)


class MatchRanking(RankingBase):
    """
    回馈赛榜
    """


class SlotMachineIntegralRanking(RankingBase):
    """
    老虎机(鸿运当头)活动玩家积分排行榜
    """


class MoneyTreeRanking(RankingBase):
    """
    摇钱树活动玩家摇动次数榜
    """


class TodayGrandPrixRanking(RankingBase):
    """
    大奖赛积分榜
    """
    def _getRanking(self, timestamp):
        """
        获取所有用户排行榜数据
        :param rankingDefine: 数值配置
        :param timestamp: 时间戳
        :return: 排行榜所有数据
        """
        rankingList = self.getTopNRankUsers(timestamp)
        bonusPool = 0
        rankData = []
        rankingListLen = len(rankingList.rankingUserList)
        ftlog.debug("TodayGrandPrixRanking._getRanking, rankType =", self.rankType, "rankingListLen =", rankingListLen, self.rankDefine.topN)
        rankRewardConf = config.getRankRewardConf(self.rankType)
        rankRewardsList = rankRewardConf.get("rankRewards")
        if rankRewardsList:
            for rankRewards in rankRewardsList:
                idx = rankRewards["ranking"]["start"] - 1
                if idx < rankingListLen:
                    user = rankingList.rankingUserList[idx]
                    if rankRewards["ranking"]["start"] == rankRewards["ranking"]["end"]:
                        userId = user.userId
                        name = util.getNickname(userId)
                        sex, avatar = userdata.getAttrs(userId, ["sex", "purl"])
                        vipLevel = util.getVipShowLevel(userId)
                    else:
                        idx = rankRewards["ranking"]["end"] - 1
                        while idx >= rankingListLen:
                            idx -= 1
                        user = rankingList.rankingUserList[idx]                                     # 6-10第十名玩家
                        name = config.getMultiLangTextConf("ID_RANK_INFO_1", lang=self.lang) % (rankRewards["ranking"]["start"], rankRewards["ranking"]["end"])     # %d-%d名
                        userId = sex = vipLevel = 0
                        avatar = ""
                    userRank = user.rank + 1
                    score = self._getOneUserScore(user.userId, user.score)
                else:
                    if rankRewards["ranking"]["start"] == rankRewards["ranking"]["end"]:
                        name = config.getMultiLangTextConf("ID_HAS_NO_DATA", lang=self.lang)        # 暂无数据
                    else:
                        name = config.getMultiLangTextConf("ID_RANK_INFO_1", lang=self.lang) % (rankRewards["ranking"]["start"], rankRewards["ranking"]["end"])
                    userId = sex = vipLevel = score = userRank = 0
                    avatar = ""
                rewards = self._buildRewards(rankRewards["rewards"]) if rankRewards["rewards"] else []
                oneUserRankData = {
                    "userId": userId,
                    "name": name,
                    "sex": sex,
                    "score": score,
                    "rank": userRank,
                    "avatar": avatar,
                    "vip": vipLevel,
                    "rewards": rewards
                }
                rankData.append(oneUserRankData)
            if ftlog.is_debug():
                for idx, user in enumerate(rankingList.rankingUserList):
                    ftlog.debug("TodayGrandPrixRanking, rank =", idx + 1, user.rank + 1, user.userId, user.score)

        return (rankingList, int(time.time()), {
            "rankId": self.rankDefine.rankingId,
            "issueNum": rankingList.issueNumber,
            "name": rankingList.rankingDefine.name,
            "desc": rankingList.rankingDefine.desc,
            "type": rankingList.rankingDefine.rankingType,
            "rankData": rankData,
            "bonusPool": bonusPool,
            "superbossPool": 0
        })

    def _getRankingDetail(self, timestamp):
        """
        获取所有用户排行榜数据
        :param rankingDefine: 数值配置
        :param timestamp: 时间戳
        :return:  排行榜所有数据
        """
        rankingList = self.getTopNRankUsers(timestamp)
        rankData = []
        if ftlog.is_debug():
            ftlog.debug("_getRankingDetail, rankType =", self.rankType, "rankingList =", len(rankingList.rankingUserList))
        for index, user in enumerate(rankingList.rankingUserList):
            if user.userId == 0:
                continue
            name = util.getNickname(user.userId)
            sex, avatar = userdata.getAttrs(user.userId, ["sex", "purl"])
            score = self._getOneUserScore(user.userId, user.score)                                  # 获取排名积分
            rewards = self._getOneUserReward(user.userId, user.rank + 1, 0, user.score)             # 获取排名的奖励
            vipLevel = util.getVipShowLevel(user.userId)
            oneUserRankData = {
                "userId": user.userId,
                "name": name,
                "sex": sex,
                "score": score,
                "rank": user.rank + 1,
                "avatar": avatar,
                "vip": vipLevel,
                "rewards": rewards
            }
            rankData.append(oneUserRankData)

        return (rankingList, int(time.time()), {                # 获取topN玩家列表、时间
            "rankId": self.rankDefine.rankingId,                # 大厅排行榜Id
            "issueNum": rankingList.issueNumber,                #
            "name": rankingList.rankingDefine.name,             # 大厅排行榜名
            "desc": rankingList.rankingDefine.desc,             # 排行榜描述
            "type": rankingList.rankingDefine.rankingType,      # 排行榜类型
            "rankData": rankData,                               # 排行榜数据
        })

    def getRankingDetail(self, timestamp=None, refresh=False):
        """
        @return: (TYRankingList, timestamp, rankingList)
        获取榜单数据
        """
        global cacheRankings
        if not timestamp:
            timestamp = pktimestamp.getCurrentTimestamp()
        cacheRanking = cacheRankings.get(self.rankDefine.rankingId)
        rankRewardConf = self.rankConf
        # 更新排行榜缓存.
        if (refresh or not cacheRanking or (int(time.time()) - cacheRanking[1]) >= rankRewardConf.get("cacheTime", 0) or
            pktimestamp.getDayStartTimestamp(timestamp) != pktimestamp.getDayStartTimestamp(cacheRanking[1])):
            cacheRanking = self._getRankingDetail(timestamp)
            if cacheRanking:
                cacheRankings[self.rankDefine.rankingId] = cacheRanking
            else:
                if self.rankDefine.rankingId in cacheRankings:
                    del cacheRankings[self.rankDefine.rankingId]
        return cacheRanking

    def getRankingInfo2(self):
        """
        获取排行榜相关数据
        """
        ranking = {}
        rankRewardConf = self.rankConf
        ranking["order"] = self.rankType
        ranking["rankType"] = self.rankType
        ranking["rankName"] = config.getMultiLangTextConf(str(rankRewardConf.get("rankName")), lang=self.lang)
        if rankRewardConf.get("rankDesc"):
            ranking["rankDesc"] = config.getMultiLangTextConf(str(rankRewardConf.get("rankDesc")), lang=self.lang)
        cacheRanking = self.getRankingDetail(self._getRankTimestamp())
        cacheRanking = copy.deepcopy(cacheRanking[2])
        ownRanking = self._getOwnRanking(self.userId, cacheRanking["rankData"])                 # 自己的排名信息
        cacheRanking["rankData"].insert(0, ownRanking)                                          # 排名信息在第一位
        ranking["rankData"] = cacheRanking["rankData"]                                          # 排名详细数据
        return ranking

    def _getOneUserScore(self, userId, score, isOwner=False):
        """获取玩家自己的积分"""
        ftlog.debug("TodayGrandPrixRanking._getOneUserScore, userId =", userId, "score =", score, "isOwner =", isOwner)
        if isOwner and not score:
           score = weakdata.getDayFishData(userId, WeakData.grandPrix_point, 0)
        return score

    def refreshRankingData(self, userPointData):
        """
        刷新排行榜数据
        """
        userId = userPointData[0]
        score = userPointData[1]
        timestamp = pktimestamp.getCurrentTimestamp()
        point = weakdata.getDayFishData(self.userId, WeakData.grandPrix_point, 0)       # 大奖赛积分值
        if score > point:
            weakdata.setDayFishData(self.userId, WeakData.grandPrix_point, score)
            bireport.reportGameEvent("BI_NFISH_GRAND_PRIX_POINTS", self.userId, FISH_GAMEID, 0, int(self.rankDefine.rankingId), score, 0, 0, 0, [], util.getClientId(self.userId))
        if score:
            self.saveUserScore(config.RANK_GRAND_PRIX, userId, score, timestamp)        # 保存玩家积分

    def processRanking(self, todayDate, strfTime):
        """
        处理排行榜发奖
        """
        processedKey = self._getProcessedKey(todayDate)
        ftlog.debug("grand_prix->processRanking", strfTime, self.sendRewardTimeStr, processedKey, processedRankings)
        if strfTime == self.sendRewardTimeStr and processedKey not in processedRankings:
            timestamp = pktimestamp.getCurrentTimestamp()
            cacheRanking = super(TodayGrandPrixRanking, self)._getRanking(timestamp)
            cacheRanking = copy.deepcopy(cacheRanking[2]["rankData"])
            processedRankings.append(processedKey)
            ftlog.info("processRankings =", processedKey, self.rankDefine.rankingId, cacheRanking, processedRankings)
            for rankData in cacheRanking:
                userId = rankData["userId"]
                weakdata.setDayFishData(userId, WeakData.grandPrix_point, 0)                        # 大奖赛积分值为0
                if userId >= config.ROBOT_MAX_USER_ID:
                    self._sendRewards(rankData, RankType.TodayGrandPrix)
                self._reportBIEvent(rankData, param01=rankData["score"])

    def _dealSendRewardsAfter(self, rankData, userId, rank, rewards):
        """
        处理完排行榜发奖后的逻辑
        @param rewards: 排名奖励可能还有宝藏加成
        """
        self._sendRankOverEvent(rankData, params={"rewards": rewards})


class YestodayGrandPrixRanking(TodayGrandPrixRanking):
    """
    昨日大奖赛积分榜
    """
    def getRankingInfo(self):
        """获取排行榜相关数据"""
        ranking = super(YestodayGrandPrixRanking, self).getRankingInfo()
        rankRewardConf = self.rankConf
        ranking["rankDesc"] = ""                                        # 替换排行榜描述文本
        if ranking["rankData"] and len(ranking["rankData"]) > 1:
            rankDescId = rankRewardConf.get("rankDesc")
            ranking["rankDesc"] = strutil.replaceParams(config.getMultiLangTextConf(str(rankDescId), lang=self.lang),
                                                        {"userName": ranking["rankData"][1]["name"]})
        return ranking

    def getRanking(self, timestamp=None, refresh=False):
        """获取历史榜单数据"""
        return self._getHistoryRanking()

    def _getOneUserScore(self, userId, score, isOwner=False):
        """获取玩家自身昨日排名的积分"""
        ftlog.debug("YestodayGrandPrixRanking._getOneUserScore, userId =", userId, "score =", score, "isOwner =", isOwner)
        if isOwner:
            timestamp = pktimestamp.getCurrentTimestamp()
            dateArray = datetime.fromtimestamp(timestamp)
            yesterday = dateArray - timedelta(days=1)
            timestamp = pktimestamp.getDayStartTimestamp(time.mktime(yesterday.timetuple()))
            userRankData = hallranking.rankingSystem.getRankingUser(self.rankDefine.rankingId, self.userId, timestamp)
            return userRankData.score or self._getGameData9999RankInfo(userId, timestamp)
        return score

    def _getOneUserReward(self, userId, rank, poolNum=0, score=0):
        """获取排名玩家第N名的奖励"""
        rewards = []
        rankRewards = self._getRankRewards(rank, RankType.TodayGrandPrix)
        if rankRewards and rankRewards["rewards"]:
            rewards = self._buildRewards(rankRewards["rewards"])
        return rewards

    def processRanking(self, todayDate, strfTime):
        """处理排行榜发奖"""
        pass

    def _getOwnRankingTime(self):
        """获取昨天排行榜的时间戳"""
        dateArray = datetime.fromtimestamp(pktimestamp.getCurrentTimestamp())
        yesterday = dateArray - timedelta(days=1)
        timestamp = pktimestamp.getDayStartTimestamp(time.mktime(yesterday.timetuple()))
        return timestamp


class WeekGrandPrixRanking(RankingBase):
    """
    大奖赛积分周榜
    """
    def _getOneUserScore(self, userId, score, isOwner=False):
        """获取玩家一周的排行榜积分"""
        if isOwner and not score:
            weekPointList = json.loads(weakdata.getWeekFishData(userId, WeakData.grandPrix_weekPointList, "[0, 0, 0, 0, 0, 0, 0]"))
            score = sum(sorted(weekPointList)[-3:])                     # 一周最好3次的总积分
        return score

    def processRanking(self, todayDate, strfTime):
        """
        处理排行榜发奖
        """
        todayStartTimestamp = pktimestamp.getCurrentDayStartTimestamp()
        processedKey = self._getProcessedKey(todayDate)
        st = time.localtime(todayStartTimestamp)
        # 周日23:30重置
        if st.tm_wday == config.getRankRewardConf(self.rankType).get("clearWeekDay", 6) \
                and strfTime == self.clearDataTime and processedKey not in processedRankings:
            timestamp = pktimestamp.getCurrentTimestamp()
            cacheRanking = self.getRanking(timestamp, True)
            cacheRanking = copy.deepcopy(cacheRanking[2]["rankData"])
            processedRankings.append(processedKey)
            ftlog.info("processRankings =", processedKey, self.rankDefine.rankingId, cacheRanking, processedRankings)
            for rankData in cacheRanking:
                userId = rankData["userId"]
                weakdata.setWeekFishData(userId, WeakData.grandPrix_weekPointList, "[0, 0, 0, 0, 0, 0, 0]")
                if userId >= config.ROBOT_MAX_USER_ID:
                    self._sendRewards(rankData, RankType.WeekGrandPrix)
                self._reportBIEvent(rankData, param01=rankData["score"])
                # 删除一周前数据
                hallranking.rankingSystem.removeUser(self.rankDefine.rankingId, userId)

    def refreshRankingData(self, userPointData):
        """
        刷新周榜数据
        """
        userId = userPointData[0]
        point = userPointData[1]
        timestamp = pktimestamp.getCurrentTimestamp()
        st = time.localtime(timestamp)
        weekPointList = json.loads(weakdata.getWeekFishData(userId, WeakData.grandPrix_weekPointList, "[0, 0, 0, 0, 0, 0, 0]"))
        oldScore = sum(sorted(weekPointList)[-3:])
        if point > weekPointList[st.tm_wday]:           # [0、1、2、3、4、5、6]
            weekPointList[st.tm_wday] = point
            weakdata.setWeekFishData(userId, WeakData.grandPrix_weekPointList, json.dumps(weekPointList))
        score = sum(sorted(weekPointList)[-3:])
        if score >= oldScore:
            self.saveUserScore(config.RANK_GRAND_PRIX_WEEK, userId, score, timestamp)

class ProfitCoinRanking(RankingBase):
    """
    玩家盈利榜
    """


class FestivalTurntableIntegralRanking(RankingBase):
    """
    节日转盘抽大奖活动玩家积分排行榜
    """


class TodayRankingBase(RankingBase):
    """
    今日榜
    """


class CollectItemRanking(RankingBase):
    """
    活动中收集xx道具排行榜(赢永久魅影皮肤活动)
    """


class TodayPoseidonRanking(RankingBase):
    """
    海皇今日赢家榜
    """


class YestodayPoseidonRanking(TodayPoseidonRanking):
    """
    海皇昨日赢家榜
    """


class WeekPoseidonRanking(RankingBase):
    """
    海皇七日赢家榜
    """


class CompActTeamRanking(TodayRankingBase):
    """
    竞赛活动team积分榜
    """


class YestordayCompActTeamRanking(CompActTeamRanking):
    """
    上期竞赛team积分榜
    """


class CompActPointRanking(TodayRankingBase):
    """
    竞赛活动积分榜
    """


class SuperbossPointRanking(TodayRankingBase):
    """
    超级boss积分榜
    """


class YestordaySuperbossPointRanking(SuperbossPointRanking):
    """
    上期超级boss积分榜
    """