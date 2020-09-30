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
    ItemHappyDouble = 28    # 道具翻番乐排行榜
    SBossBox = 29       # 宝箱怪积分金币榜
    SBossOctopus = 30   # 章鱼积分金币榜
    SBossQueen = 31     # 龙女王积分金币榜
    SBossDragon = 32    # 冰龙积分金币榜
    SBossBoxRing = 33       # 宝箱怪积分金环榜
    SBossOctopusRing = 34   # 章鱼积分金环榜
    SBossQueenRing = 35    # 龙女王积分金环榜
    SBossDragonRing = 36    # 冰龙积分金环榜


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
    FestivalTurntable = 20  # 节日转盘抽大奖积分排行榜
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
    LastCompActWinner = 32# 上期竞赛冠军榜
    ItemHappyDouble = 33 # 道具翻番乐收集排行
    SBossBox = 34               # 宝箱怪积分金币榜
    LastSBossBox = 35           # 上期宝箱怪积分金币榜
    SBossOctopus = 36           # 章鱼积分金币榜
    LastSBossOctopus = 37       # 上期章鱼积分金币榜
    SBossQueen = 38             # 龙女王积分金币榜
    LastSBossQueen = 39         # 上期龙女王积分金币榜
    SBossDragon = 40            # 冰龙积分金币榜
    LastSBossDragon = 41        # 上期冰龙积分金币榜
    SBossBoxRing = 42               # 宝箱怪积分金环榜
    LastSBossBoxRing = 43           # 上期宝箱怪积分金环榜
    SBossOctopusRing = 44           # 章鱼积分金环榜
    LastSBossOctopusRing = 45       # 上期章鱼积分金环榜
    SBossQueenRing = 46             # 龙女王积分金环榜
    LastSBossQueenRing = 47         # 上期龙女王积分金环榜
    SBossDragonRing = 48            # 冰龙积分金环榜
    LastSBossDragonRing = 49        # 上期冰龙积分金环榜


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
        if ftlog.is_debug():
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
            if ftlog.is_debug():
                ftlog.debug("cacheRanking rankingDefine cacheTimes:", cacheRanking[0].rankingDefine.cacheTimes)
        # 更新排行榜缓存.
        if (refresh or not cacheRanking or (int(time.time()) - cacheRanking[1]) >= rankRewardConf.get("cacheTime", 0) or
            pktimestamp.getDayStartTimestamp(timestamp) != pktimestamp.getDayStartTimestamp(cacheRanking[1])):
            cacheRanking = self._getRanking(timestamp)
            if cacheRanking:
                cacheRankings[self.rankDefine.rankingId] = cacheRanking
                if ftlog.is_debug():
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
                    if ftlog.is_debug():
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
                if ftlog.is_debug():
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
                    if ftlog.is_debug():
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
            "issueNum": rankingList.issueNumber,                # 期号
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
        if ftlog.is_debug():
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
                if ftlog.is_debug():
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
    def _getRankTimestamp(self):
        """
        获取排行榜时的时间戳
        """
        # 过22点（发奖时间）用第二天的时间戳
        timestamp = pktimestamp.getCurrentTimestamp()
        if timestamp - pktimestamp.getDayStartTimestamp(timestamp) >= self.sendRewardTimeInt:
            dateArray = datetime.fromtimestamp(timestamp)
            tomorrow = dateArray + timedelta(days=1)
            timestamp = time.mktime(tomorrow.timetuple())
        return timestamp

    def _getOwnRankingTime(self):
        return self._getRankTimestamp()

    def _getOneUserScore(self, userId, score, isOwner=False):
        if isOwner:
            timestamp = pktimestamp.getCurrentTimestamp()
            if timestamp - pktimestamp.getDayStartTimestamp(timestamp) >= self.sendRewardTimeInt:
                dateArray = datetime.fromtimestamp(timestamp)
                tomorrow = dateArray + timedelta(days=1)
                timestamp = pktimestamp.getDayStartTimestamp(time.mktime(tomorrow.timetuple()))

            userRankData = hallranking.rankingSystem.getRankingUser(self.rankDefine.rankingId,
                                                                    self.userId, timestamp)

            return userRankData.score or self._getGameData9999RankInfo(userId, timestamp)

        else:
            return score

    def refreshRankingData(self, event):
        """
        刷新排行榜数据
        """
        userId = event.userId
        count = event.count
        timestamp = pktimestamp.getCurrentTimestamp()
        weakdata.incrDayFishData(userId, WeakData.starfish, count)
        if timestamp - pktimestamp.getDayStartTimestamp(timestamp) < self.sendRewardTimeInt:
            self.saveUserScore(config.RANK_STAR, userId, count, timestamp)
        else:
            dateArray = datetime.fromtimestamp(timestamp)
            tomorrow = dateArray + timedelta(days=1)
            timestamp = pktimestamp.getDayStartTimestamp(time.mktime(tomorrow.timetuple()))
            self.saveUserScore(config.RANK_STAR, userId, count, timestamp)

    def processRanking(self, todayDate, strfTime):
        """
        处理排行榜发奖
        """
        processedKey = self._getProcessedKey(todayDate)
        timestamp = pktimestamp.getCurrentTimestamp()
        if ftlog.is_debug():
            ftlog.debug("starfish->processRanking", strfTime, self.sendRewardTimeStr, todayDate, processedRankings)
        if strfTime == self.sendRewardTimeStr and processedKey not in processedRankings:  # 海星榜发奖
            cacheRanking = self.getRanking(timestamp, True)
            cacheRanking = copy.deepcopy(cacheRanking[2]["rankData"])
            processedRankings.append(processedKey)
            ftlog.info("processRankings =", processedKey, self.rankDefine.rankingId, cacheRanking, processedRankings)
            for rankData in cacheRanking:
                self._sendRewards(rankData, RankType.TodayStarfish)
                self._sendRankOverEvent(rankData)
                self._reportBIEvent(rankData, param01=rankData["score"])

    def _sendAcRewards(self, userId, rank, rewards):
        """
        发送榜上有名活动奖励
        """
        acTime = fish_activity_system.getRealAcTime(userId, "activity_star_rank_bet")
        if not acTime:
            return
        isAcBetOpen = util.isTimeEffective(acTime)
        activityBet = self.rankConf.get("activityBet", 1)
        if not isAcBetOpen or not rewards:
            return
        tmpRewards = []
        for reward in rewards:
            tmpRewards.append({"name": reward["name"], "count": int(math.ceil(reward["count"] * activityBet))})
        lang = util.getLanguage(userId)
        message = strutil.replaceParams(config.getMultiLangTextConf(self.rankConf.get("activityMailDesc"), lang=lang),
                                        {"rank": rank, "rankName": config.getMultiLangTextConf(str(self.rankConf["rankName"]), lang=lang)})
        mail_system.sendSystemMail(userId, mail_system.MailRewardType.ActivityReward, tmpRewards, message)


class YesterdayStarfishRanking(RankingBase):
    """
    昨日海星榜
    """
    def getRankingInfo(self):
        if ftlog.is_debug():
            ftlog.debug("getRankingTabs->getRanking userId=", self.userId,
                        "rankType=", self.rankType,
                        "rankingIds=", self.rankDefine.rankingId)
        ranking = super(YesterdayStarfishRanking, self).getRankingInfo()
        rankRewardConf = self.rankConf
        ranking["rankDesc"] = ""
        if ranking["rankData"] and len(ranking["rankData"]) > 1:
            rankDescId = rankRewardConf.get("rankDesc")
            ranking["rankDesc"] = strutil.replaceParams(config.getMultiLangTextConf(str(rankDescId), lang=self.lang),
                                                        {"userName": ranking["rankData"][1]["name"]})
        return ranking

    def getRanking(self, timestamp=None, refresh=False):
        return self._getHistoryRanking()

    def _getHistoryTimeAndUpdate(self, historyCacheRanking, currentTimestamp, yesterday):
        """
        @return: (TYRankingList, timestamp, rankingList)
        """
        timestamp = currentTimestamp
        if currentTimestamp - pktimestamp.getDayStartTimestamp(currentTimestamp) < self.sendRewardTimeInt:
            timestamp = pktimestamp.getDayStartTimestamp(time.mktime(yesterday.timetuple()))
        if historyCacheRanking:
            isUpdate = currentTimestamp - pktimestamp.getDayStartTimestamp(
                historyCacheRanking[1]) >= self.sendRewardTimeInt
        else:
            isUpdate = True
        return timestamp, isUpdate

    def _getOneUserScore(self, userId, score, isOwner=False):
        if isOwner:
            timestamp = pktimestamp.getCurrentTimestamp()
            if timestamp - pktimestamp.getDayStartTimestamp(timestamp) < self.sendRewardTimeInt:
                dateArray = datetime.fromtimestamp(timestamp)
                yesterday = dateArray - timedelta(days=1)
                timestamp = pktimestamp.getDayStartTimestamp(time.mktime(yesterday.timetuple()))

            userRankData = hallranking.rankingSystem.getRankingUser(self.rankDefine.rankingId,
                                                                    self.userId, timestamp)
            return userRankData.score or self._getGameData9999RankInfo(userId, timestamp)
        return score

    def _getOwnRankingTime(self):
        timestamp = pktimestamp.getCurrentTimestamp()
        if timestamp - pktimestamp.getDayStartTimestamp(timestamp) < self.sendRewardTimeInt:
            dateArray = datetime.fromtimestamp(timestamp)
            yesterday = dateArray - timedelta(days=1)
            timestamp = pktimestamp.getDayStartTimestamp(time.mktime(yesterday.timetuple()))
        return timestamp

    def _getOneUserReward(self, userId, rank, poolNum=0, score=0):
        rewards = []
        rankRewards = self._getRankRewards(rank, RankType.TodayStarfish)
        if rankRewards and rankRewards["rewards"]:
            rewards = self._buildRewards(rankRewards["rewards"])
        return rewards


class BulletRanking(RankingBase):
    """
    弹头榜
    """
    def getRankingInfo(self):
        event = BulletChangeEvent(self.userId, FISH_GAMEID)
        self.refreshRankingData(event)
        return super(BulletRanking, self).getRankingInfo()

    def refreshRankingData(self, event):
        userBag = hallitem.itemSystem.loadUserAssets(event.userId).getUserBag()
        score = 0
        bulletCountDict = {}
        for kindId in BULLET_KINDIDS:
            bulletItemKind = hallitem.itemSystem.findItemKind(kindId)
            bulletCount = userBag.calcTotalUnitsCount(bulletItemKind)
            score += BULLET_KINDIDS[kindId] * bulletCount
            bulletCountDict[kindId] = bulletCount
        if score >= BULLET_KINDIDS[GOLD_BULLET_KINDID] * 1000:
            if gdata.mode() == gdata.RUN_MODE_ONLINE:
                ftlog.info("[WARNING]hold bullet too many", event.userId, bulletCountDict)
        self.saveUserScore(config.RANK_BULLET, event.userId, score, int(time.time()))

    def _getOneUserScore(self, userId, score, isOwner=False):
        if isOwner or self.rankConf.get("encryptScore", 0) == 0 or self.httpRequest:
            userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
            bronzeBulletItemKind = hallitem.itemSystem.findItemKind(BRONZE_BULLET_KINDID)
            silverBulletItemKind = hallitem.itemSystem.findItemKind(SILVER_BULLET_KINDID)
            goldBulletItemKind = hallitem.itemSystem.findItemKind(GOLD_BULLET_KINDID)
            bronzeBulletCount = userBag.calcTotalUnitsCount(bronzeBulletItemKind)
            silverBulletCount = userBag.calcTotalUnitsCount(silverBulletItemKind)
            goldBulletCount = userBag.calcTotalUnitsCount(goldBulletItemKind)
            score = [bronzeBulletCount, silverBulletCount, goldBulletCount]
        else:
            score = ["?", "?", "?"]
        return score


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
    def _getOneUserScore(self, userId, score, isOwner=False):
        if isOwner and not score:
            score = weakdata.getDayFishData(userId, WeakData.luckyEggsNum, 0)
        return score

    def processRanking(self, todayDate, strfTime):
        timestamp = pktimestamp.getCurrentTimestamp()
        todayStartTimestamp = util.getDayStartTimestamp(timestamp)
        processedKey = self._getProcessedKey(todayDate)
        if strfTime == self.clearDataTime and processedKey not in processedRankings:  # 删除七天前数据
            rankingDefine = self.rankDefine
            luck7Rank = self.getTopNRankUsers(timestamp, rankingDefine)
            processedRankings.append(processedKey)
            for userRankInfo in luck7Rank.rankingUserList:
                _time = gamedata.getGameAttrInt(userRankInfo.userId, FISH_GAMEID, GameData.luckyEggs7RkTime)
                ftlog.info("processRankings =", processedKey, rankingDefine.rankingId, userRankInfo.userId, _time, processedRankings)
                if todayStartTimestamp - util.getDayStartTimestamp(_time) >= SevenRankExpireTime:
                    hallranking.rankingSystem.removeUser(rankingDefine.rankingId, userRankInfo.userId)

    def refreshRankingData(self, event):
        todayRankDefine = self._getRankingDefine(RankDefineIndex.TodayLucky, CLIENTID_ROBOT)
        todayRankInfo = hallranking.rankingSystem.getRankingUser(todayRankDefine.rankingId, self.userId)
        sevenRankInfo = hallranking.rankingSystem.getRankingUser(self.rankDefine.rankingId, self.userId)
        if todayRankInfo and sevenRankInfo:
            todayScore = int(todayRankInfo.score) if todayRankInfo.score else weakdata.getDayFishData(self.userId,
                                                                                                      WeakData.luckyEggsNum,
                                                                                                      0)
            sevenScore = int(sevenRankInfo.score) if sevenRankInfo.score else 0
            _time = int(time.time())
            if ftlog.is_debug():
                ftlog.debug("_update7LuckyRank->", sevenRankInfo.score, _time, todayRankInfo.score)
            if sevenScore == 0 or todayScore >= sevenScore:
                gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.luckyEggs7RkTime, _time)
                self.saveUserScore(config.RANK_SEVEN_LUCKY, self.userId, todayScore, _time)


class TodayRobberyRanking(RankingBase):
    """
    招财今日赢家榜
    """
    def _getOneUserScore(self, userId, score, isOwner=False):
        score = robbery_lottery_pool.getRobberyWinMostData(userId)
        return score

    def _getOneUserReward(self, userId, rank, poolNum=0, score=0):
        rewards = []
        if poolNum == 0 or not poolNum:
            poolNum = robbery_lottery_pool.getRobberyWealthPool(False)
        rankRewards, _ = self._getRobberyReward(rank, poolNum)
        if rankRewards and rankRewards["rewards"]:
            rewards = self._buildRewards(rankRewards["rewards"])
        return rewards

    def _getRobberyReward(self, rank, poolNum, isMerge=False):
        rankRewards = self._getRankRewards(rank, RankType.TodayWinner)
        if not rankRewards or not rankRewards["rewardPercent"]:
            return None, 0
        tempRankRewards = {}
        tempRankRewards["message"] = rankRewards["message"]
        tempRankRewards["desc"] = rankRewards["desc"]
        tempRankRewards["ranking"] = rankRewards["ranking"]
        precentNum = rankRewards["rewardPercent"][rank % len(rankRewards["rewardPercent"]) - 1]
        todayProportion = config.getRobberyConf()["wealthAwardTodayProportion"]
        # 原始铜珠数量
        originCount = math.ceil(poolNum * precentNum * todayProportion)
        itemCount = originCount
        rewards = []
        if isMerge:
            if int(itemCount / 50) > 0: # 转换为金珠
                count_ = int(itemCount / 50)
                itemId_ = "item:%d" % GOLD_BULLET_KINDID
                rewards.append({"itemId": itemId_, "count": int(count_)})
                itemCount -= count_ * 50
            if int(itemCount / 10) > 0: # 转换为银珠
                count_ = int(itemCount / 10)
                itemId_ = "item:%d" % SILVER_BULLET_KINDID
                rewards.append({"itemId": itemId_, "count": int(count_)})
                itemCount -= count_ * 10
        # 转换为金、银珠后，剩余的铜珠
        if itemCount > 0:
            itemId = "item:%d" % BRONZE_BULLET_KINDID
            rewards.append({"itemId": itemId, "count": int(itemCount)})
        tempRankRewards["rewards"] = rewards
        return tempRankRewards, originCount

    def processRanking(self, todayDate, strfTime):
        processedKey = self._getProcessedKey(todayDate)
        if strfTime == self.sendRewardTimeStr and processedKey not in processedRankings:  # 发今日赢家榜奖励
            yesterday = date.today() - timedelta(days=1)
            yesterdayTimestamp = int(time.mktime(yesterday.timetuple()))  # 昨天开始时间
            cacheRanking = self._getRanking(yesterdayTimestamp)
            cacheRanking = copy.deepcopy(cacheRanking[2]["rankData"])
            processedRankings.append(processedKey)
            totalPoolNum = robbery_lottery_pool.getRobberyWealthPool(True)
            bireport.reportGameEvent("BI_NFISH_GE_ROBBERY_LOTTERY", config.ROBOT_MAX_USER_ID, FISH_GAMEID, 0,
                                     0, 0, int(totalPoolNum), 0, 0, [], config.CLIENTID_ROBOT)
            ftlog.info("processRankings =", processedKey, self.rankDefine.rankingId,
                       cacheRanking, processedRankings, totalPoolNum)

            for rankData in cacheRanking:
                randRewards, originCount = self._getRobberyReward(rankData["rank"], totalPoolNum, isMerge=True)
                if ftlog.is_debug():
                    ftlog.debug("processRankings", rankData, randRewards)
                self._sendRewards(rankData, RankType.TodayWinner, randRewards)
                self._sendRankOverEvent(rankData, params={"originCount": originCount})
                self._reportBIEvent(rankData, param01=originCount)

    def _getProcessedMessage(self, rankData, rankRewards):
        """
        获取处理后的邮件内容
        """
        message = super(TodayRobberyRanking, self)._getProcessedMessage(rankData, rankRewards)
        if (len(rankRewards["rewards"]) == 1 and
            str(BRONZE_BULLET_KINDID) in rankRewards["rewards"][0]["itemId"]):
            # 招财奖励邮件去除"(自动向上转换)"
            message = message.split("(")[0]
        return message

    def _sendAcRewards(self, userId, rank, rewards):
        acTime = fish_activity_system.getRealAcTime(userId, "activity_robbery_rank")
        if not acTime:
            return
        isActivityOpen = util.isTimeEffective(acTime)
        if not isActivityOpen:
            return

        rankRewardsList = self.rankConf.get("activityRewards")
        tmpRewards = []
        if rankRewardsList:
            for rankRewards in rankRewardsList:
                if rankRewards["ranking"]["start"] <= rank <= rankRewards["ranking"]["end"]:
                    tmpRewards = rankRewards
                    break
        lang = util.getLanguage(userId)
        message = strutil.replaceParams(config.getMultiLangTextConf(tmpRewards.get("message"), lang=lang),
                                        {"rank": rank})
        mail_system.sendSystemMail(userId, mail_system.MailRewardType.ActivityReward, tmpRewards.get("rewards"), message)


class YestodayRobberyRanking(TodayRobberyRanking):
    """
    招财昨日赢家榜数据
    """
    def getRankingInfo(self):
        if ftlog.is_debug():
            ftlog.debug("getRankingTabs->getRanking userId=", self.userId,
                        "rankType=", self.rankType,
                        "rankingIds=", self.rankDefine.rankingId)
        ranking = super(TodayRobberyRanking, self).getRankingInfo()
        rankRewardConf = self.rankConf
        ranking["rankDesc"] = ""
        if ranking["rankData"] and len(ranking["rankData"]) > 1:
            rankDescId = rankRewardConf.get("rankDesc")
            ranking["rankDesc"] = strutil.replaceParams(config.getMultiLangTextConf(str(rankDescId), lang=self.lang),
                                                        {"userName": ranking["rankData"][1]["name"]})
        return ranking

    def getRanking(self, timestamp=None, refresh=False):
        return self._getHistoryRanking()

    def _getOneUserScore(self, userId, score, isOwner=False):
        dateTime = date.today() - timedelta(days=1)
        score = robbery_lottery_pool.getRobberyWinMostData(userId, dateTime)
        return score

    def _getOneUserReward(self, userId, rank, poolNum=0, score=0):
        rewards = []
        if poolNum == 0 or not poolNum:
            poolNum = robbery_lottery_pool.getRobberyWealthPool(True)
        rankRewards, _ = self._getRobberyReward(rank, poolNum)
        if rankRewards and rankRewards["rewards"]:
            rewards = self._buildRewards(rankRewards["rewards"])
        return rewards

    def processRanking(self, todayDate, strfTime):
        pass

    def _getOwnRankingTime(self):
        dateArray = datetime.fromtimestamp(pktimestamp.getCurrentTimestamp())
        yesterday = dateArray - timedelta(days=1)
        timestamp = pktimestamp.getDayStartTimestamp(time.mktime(yesterday.timetuple()))
        return timestamp


class WeekRobberyRanking(RankingBase):
    """
    招财七日赢家榜数据
    """
    def _getOneUserScore(self, userId, score, isOwner=False):
        score = robbery_lottery_pool.getRobbery7WinBulletNum(userId)
        return score

    def processRanking(self, todayDate, strfTime):
        """处理发奖之后的数据"""
        processedKey = self._getProcessedKey(todayDate)
        timestamp = pktimestamp.getCurrentTimestamp()
        todayStartTimestamp = pktimestamp.getDayStartTimestamp()
        if strfTime == self.clearDataTime and processedKey not in processedRankings:  # 删除七天前数据
            rankingDefine = self.rankDefine
            robbery7Rank = self.getTopNRankUsers(timestamp, rankingDefine)
            processedRankings.append(processedKey)
            for userRankInfo in robbery7Rank.rankingUserList:
                robbery7Score = robbery_lottery_pool.getRobbery7WinMostData(userRankInfo.userId)
                if robbery7Score and len(robbery7Score) >= 2:
                    _time = robbery7Score[1]
                    ftlog.info("processRankings =", processedKey, rankingDefine.rankingId, userRankInfo.userId, _time, processedRankings)
                    if todayStartTimestamp - util.getDayStartTimestamp(_time) >= SevenRankExpireTime:
                        robbery_lottery_pool.delRobbery7WinMostData(userRankInfo.userId)
                        hallranking.rankingSystem.removeUser(rankingDefine.rankingId, userRankInfo.userId)


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
    def _getRankRewards(self, rank, rankType=None):
        """
        获取排名奖励
        :param rank: 玩家排名
        :return: 奖励
        """
        roomId = 44104
        if self.rankDefineIndex == RankDefineIndex.Match44101:
            roomId = 44101
        elif self.rankDefineIndex == RankDefineIndex.Match44102:
            roomId = 44102
        elif self.rankDefineIndex == RankDefineIndex.Match44103:
            roomId = 44103
        elif self.rankDefineIndex == RankDefineIndex.Match44104:
            roomId = 44104
        roomConf = gdata.getRoomConfigure(roomId)
        if not roomConf:
            return None
        matchConf = roomConf.get("matchConf")
        rankRewardsList = matchConf.get("rank.rewards")
        if rankRewardsList:
            for rankRewards in rankRewardsList:
                if rankRewards["ranking"]["start"] <= rank <= rankRewards["ranking"]["end"]:
                    return rankRewards
        return None

    def refreshRankingData(self, userScores):
        """
        刷新排行榜分数
        """
        curTime = pktimestamp.getCurrentTimestamp()
        rankKey = u"ranking.list:%s:19700101" % str(self.rankDefine.rankingId)
        daobase.executeRankCmd("DEL", rankKey)
        for userInfo in userScores:
            hallranking.rankingSystem.setUserScore(self.rankDefine.rankingId, userInfo["userId"], userInfo["score"], curTime)
            util.saveRankInfo(userInfo["userId"], userInfo["score"],
                              self.rankDefine.rankingId, userInfo.get("signinTime", 0),
                              expireTime=self.rankConf.get("expireTime"), updateTime=userInfo.get("signinTime", 0))


class SlotMachineIntegralRanking(RankingBase):
    """
    老虎机(鸿运当头)活动玩家积分排行榜
    """
    def _getOneUserScore(self, userId, score, isOwner=False):
        if isOwner and not score:
           score = weakdata.getDayFishData(userId, WeakData.slotMachineIntegral, 0)
        return score

    def refreshRankingData(self, event):
        """
        刷新排行榜数据
        """
        userId = event.userId
        count = event.integral
        timestamp = pktimestamp.getCurrentTimestamp()
        self.saveUserScore(config.RANK_SLOT_MACHINE, userId, count, timestamp)

    def processRanking(self, todayDate, strfTime):
        """
        处理排行榜发奖
        """
        processedKey = self._getProcessedKey(todayDate)
        if ftlog.is_debug():
            ftlog.debug("slot_machine---processRanking", strfTime, self.sendRewardTimeStr, processedKey, processedRankings)
        if strfTime == self.sendRewardTimeStr and processedKey not in processedRankings:
            yesterday = date.today() - timedelta(days=1)
            yesterdayTimestamp = int(time.mktime(yesterday.timetuple()))  # 昨天开始时间
            cacheRanking = self._getRanking(yesterdayTimestamp)
            cacheRanking = copy.deepcopy(cacheRanking[2]["rankData"])
            processedRankings.append(processedKey)
            ftlog.info("processRankings =", processedKey, self.rankDefine.rankingId,
                       cacheRanking, processedRankings)
            for rankData in cacheRanking:
                self._sendRewards(rankData, RankType.SlotMachine)
                self._reportBIEvent(rankData, param01=rankData["score"])


class MoneyTreeRanking(RankingBase):
    """
    摇钱树活动玩家摇动次数榜
    """
    def _getOneUserScore(self, userId, score, isOwner=False):
        if isOwner and not score:
           score = weakdata.getDayFishData(userId, WeakData.moneyTreeCount, 0)
        return score

    def refreshRankingData(self, event):
        """
        刷新排行榜数据
        """
        userId = event.userId
        count = event.count
        timestamp = pktimestamp.getCurrentTimestamp()
        weakdata.incrDayFishData(userId, WeakData.moneyTreeCount, count)
        self.saveUserScore(config.RANK_MONEY_TREE, userId, count, timestamp)

    def processRanking(self, todayDate, strfTime):
        """
        处理排行榜发奖
        """
        processedKey = self._getProcessedKey(todayDate)
        if ftlog.is_debug():
            ftlog.debug("money_tree->processRanking", strfTime, self.sendRewardTimeStr, processedKey, processedRankings)
        if strfTime == self.sendRewardTimeStr and processedKey not in processedRankings:
            yesterday = date.today() - timedelta(days=1)
            yesterdayTimestamp = int(time.mktime(yesterday.timetuple()))  # 昨天开始时间
            cacheRanking = self._getRanking(yesterdayTimestamp)
            cacheRanking = copy.deepcopy(cacheRanking[2]["rankData"])
            processedRankings.append(processedKey)
            ftlog.info("processRankings =", processedKey, self.rankDefine.rankingId, cacheRanking, processedRankings)
            for rankData in cacheRanking:
                self._sendRewards(rankData, RankType.MoneyTree)
                self._reportBIEvent(rankData, param01=rankData["score"])


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
        if ftlog.is_debug():
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
        if ftlog.is_debug():
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
        if ftlog.is_debug():
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
        if ftlog.is_debug():
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
        todayStartTimestamp = util.getDayStartTimestamp()
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
    def _getOneUserScore(self, userId, score, isOwner=False):
        if isOwner and not score:
           score = self._getGameData9999RankInfo(userId)
        return score

    def processRanking(self, todayDate, strfTime):
        """
        处理排行榜发奖
        """
        processedKey = self._getProcessedKey(todayDate)
        if ftlog.is_debug():
            ftlog.debug("ProfitCoinRanking->processRanking", strfTime, self.clearDataTime, processedKey, processedRankings)
        if strfTime == self.clearDataTime and processedKey not in processedRankings:
            yesterday = date.today() - timedelta(days=1)
            yesterdayTimestamp = int(time.mktime(yesterday.timetuple()))  # 昨天开始时间
            cacheRanking = self._getRanking(yesterdayTimestamp)
            cacheRanking = copy.deepcopy(cacheRanking[2]["rankData"])
            processedRankings.append(processedKey)
            ftlog.info("processRankings =", processedKey, self.rankDefine.rankingId, cacheRanking, processedRankings)
            for rankData in cacheRanking:
                self._reportBIEvent(rankData, param01=rankData["score"])

    def refreshRankingData(self, event):
        """
        刷新玩家盈利数据
        """
        userId = event.userId
        count = event.count
        timestamp = pktimestamp.getCurrentTimestamp()
        self.saveUserScore(config.RANK_PROFIT_COIN, userId, count, timestamp)
        dailyNetIncome = self._getGameData9999RankInfo(userId)
        if gdata.mode() == gdata.RUN_MODE_ONLINE:
            if dailyNetIncome >= self.rankConf.get("alertThreshold", 100000000):
                ftlog.error("[WARNING]profit coin too many", userId, dailyNetIncome)


class FestivalTurntableIntegralRanking(RankingBase):
    """
    节日转盘抽大奖活动玩家积分排行榜
    """
    def _getOneUserScore(self, userId, score, isOwner=False):
        if isOwner and not score:
           score = weakdata.getDayFishData(userId, WeakData.festivalTurntableIntegral, 0)
        return score

    def refreshRankingData(self, event):
        """
        刷新排行榜数据
        """
        userId = event.userId
        count = event.integral
        timestamp = pktimestamp.getCurrentTimestamp()
        self.saveUserScore(config.RANK_FESTIVAL_TURNTABLE, userId, count, timestamp)

    def processRanking(self, todayDate, strfTime):
        """
        处理排行榜发奖
        """
        processedKey = self._getProcessedKey(todayDate)
        if ftlog.is_debug():
            ftlog.debug("festival_Turntable---processRanking", strfTime, self.sendRewardTimeStr, processedKey, processedRankings)
        if strfTime == self.sendRewardTimeStr and processedKey not in processedRankings:
            yesterday = date.today() - timedelta(days=1)
            yesterdayTimestamp = int(time.mktime(yesterday.timetuple()))  # 昨天开始时间
            cacheRanking = self._getRanking(yesterdayTimestamp)
            cacheRanking = copy.deepcopy(cacheRanking[2]["rankData"])
            processedRankings.append(processedKey)
            ftlog.info("processRankings =", processedKey, self.rankDefine.rankingId,
                       cacheRanking, processedRankings)
            for rankData in cacheRanking:
                self._sendRewards(rankData, RankType.FestivalTurntable)
                self._reportBIEvent(rankData, param01=rankData["score"])


class TodayRankingBase(RankingBase):
    """
    今日榜
    """
    def _getRankTimestamp(self):
        """
        获取排行榜时的时间戳
        """
        timestamp = pktimestamp.getCurrentTimestamp()
        # 发奖时间不是0点需要特殊处理.
        if timestamp - pktimestamp.getDayStartTimestamp(timestamp) >= self.updateRankTimeInt > 0:
            dateArray = datetime.fromtimestamp(timestamp)
            tomorrow = dateArray + timedelta(days=1)
            timestamp = time.mktime(tomorrow.timetuple())
        return timestamp

    def _getOwnRankingTime(self):
        return self._getRankTimestamp()

    def _getOneUserScore(self, userId, score, isOwner=False):
        if isOwner:
            timestamp = pktimestamp.getCurrentTimestamp()
            # 发奖时间不是0点需要特殊处理.
            if timestamp - pktimestamp.getDayStartTimestamp(timestamp) >= self.updateRankTimeInt > 0:
                dateArray = datetime.fromtimestamp(timestamp)
                tomorrow = dateArray + timedelta(days=1)
                timestamp = pktimestamp.getDayStartTimestamp(time.mktime(tomorrow.timetuple()))
            userRankData = hallranking.rankingSystem.getRankingUser(self.rankDefine.rankingId, self.userId, timestamp)
            return userRankData.score or self._getGameData9999RankInfo(userId, timestamp)
        else:
            return score

    def refreshRankingData(self, event):
        """
        刷新排行榜数据
        """
        userId = event.userId
        count = event.count
        timestamp = pktimestamp.getCurrentTimestamp()
        # 发奖时间不是0点需要特殊处理.
        if timestamp - pktimestamp.getDayStartTimestamp(timestamp) >= self.updateRankTimeInt > 0:
            dateArray = datetime.fromtimestamp(timestamp)
            tomorrow = dateArray + timedelta(days=1)
            timestamp = pktimestamp.getDayStartTimestamp(time.mktime(tomorrow.timetuple()))
        self.saveUserScore(str(self.rankDefine.rankingId), userId, count, timestamp)

    def processRanking(self, todayDate, strfTime):
        """
        处理排行榜发奖
        """
        processedKey = self._getProcessedKey(todayDate)
        timestamp = pktimestamp.getCurrentTimestamp()
        if ftlog.is_debug():
            ftlog.debug("TodayRanking->processRanking, rank =", processedKey,
                        strfTime, self.sendRewardTimeStr, processedRankings)
        # 今日榜发奖
        if strfTime == self.sendRewardTimeStr and processedKey not in processedRankings:
            processedRankings.append(processedKey)
            rankRewardConf = config.getRankRewardConf(self.rankType)
            rankRewardsList = rankRewardConf.get("rankRewards")
            if not rankRewardsList:
                ftlog.info("no rewards, processRankings =", processedKey, self.rankDefine.rankingId, processedRankings)
                return
            cacheRanking = self.getRanking(timestamp, True)
            cacheRanking = copy.deepcopy(cacheRanking[2]["rankData"])
            ftlog.info("processRankings =", processedKey, self.rankDefine.rankingId, cacheRanking, processedRankings)
            for rankData in cacheRanking:
                self._sendRewards(rankData, self.rankType)
                self._sendRankOverEvent(rankData)
                self._reportBIEvent(rankData, param01=rankData["score"])


class CollectItemRanking(RankingBase):
    """
    活动中收集xx道具排行榜（兑换皮肤炮皮肤活动）
    """
    def _getOneUserScore(self, userId, score, isOwner=False):
        if isOwner and not score:
           score = weakdata.getDayFishData(userId, WeakData.collectActivityItemCount, 0)
        return score

    def refreshRankingData(self, event):
        """
        刷新排行榜数据
        """
        userId = event.userId
        rewards = event.rewards
        timestamp = pktimestamp.getCurrentTimestamp()
        for reward in rewards:
            if reward["name"] == config.getCollectItemConf("consumeItemId"):
                count = reward.get("count", 0)
                self.saveUserScore(config.RANK_COLLECT_ITEM, userId, count, timestamp)

    def processRanking(self, todayDate, strfTime):
        """
        处理排行榜发奖
        """
        processedKey = self._getProcessedKey(todayDate)
        if ftlog.is_debug():
            ftlog.debug("collectItem->processRanking", strfTime, self.sendRewardTimeStr, processedKey, processedRankings)
        if strfTime == self.sendRewardTimeStr and processedKey not in processedRankings:
            yesterday = date.today() - timedelta(days=1)
            yesterdayTimestamp = int(time.mktime(yesterday.timetuple()))
            cacheRanking = self._getRanking(yesterdayTimestamp)
            cacheRanking = copy.deepcopy(cacheRanking[2]["rankData"])
            processedRankings.append(processedKey)
            ftlog.info("processRankings =", processedKey, self.rankDefine.rankingId,
                       cacheRanking, processedRankings)
            for rankData in cacheRanking:
                self._sendRewards(rankData, RankType.CollectItem)
                self._reportBIEvent(rankData, param01=rankData["score"])


class TodayPoseidonRanking(RankingBase):
    """
    海皇今日赢家榜
    """
    def _getOneUserScore(self, userId, score, isOwner=False):
        """
        获取玩家排名分数
        """
        if isOwner and not score:
            score = self._getGameData9999RankInfo(userId)
        return score

    def _getOneUserReward(self, userId, rank, poolNum=0, score=0):
        """
        获取玩家排名奖励
        """
        rewards = []
        if poolNum == 0 or not poolNum:
            poolNum = poseidon_lottery_pool.getPoseidonWealthPool(False)
        rankRewards = self._getPoseidonReward(rank, poolNum)
        if rankRewards and rankRewards["rewards"]:
            rewards = self._buildRewards(rankRewards["rewards"])
        return rewards

    def _getPoseidonReward(self, rank, poolNum):
        """
        获取海皇今日赢家榜奖励
        """
        rankRewards = self._getRankRewards(rank, RankType.PoseidonTodayWinner)
        if not rankRewards or not rankRewards["rewardPercent"]:
            return None
        tempRankRewards = {}
        tempRankRewards["message"] = rankRewards["message"]
        tempRankRewards["desc"] = rankRewards["desc"]
        tempRankRewards["ranking"] = rankRewards["ranking"]
        precentNum = rankRewards["rewardPercent"][rank % len(rankRewards["rewardPercent"]) - 1]
        todayProportion = config.getPoseidonConf("wealthAwardTodayProportion")
        itemCount = int(math.ceil(poolNum * precentNum * todayProportion)) // 1000 * 1000
        rewards = []
        if itemCount > 0:
            rewards.append({"itemId": "user:chip", "count": itemCount})
        tempRankRewards["rewards"] = rewards
        return tempRankRewards

    def refreshRankingData(self, event):
        """
        刷新排行榜数据
        """
        userId = event.userId
        coin = event.coin
        lastCoin = poseidon_lottery_pool.getPoseidonWinMostData(userId)
        if coin > lastCoin:
            poseidon_lottery_pool.setPoseidonWinMostData(userId, coin)
            timestamp = pktimestamp.getCurrentTimestamp()
            self.saveUserScore(config.RANK_POSEIDON_DAY_WIN, userId, coin, timestamp)

    def processRanking(self, todayDate, strfTime):
        processedKey = self._getProcessedKey(todayDate)
        if strfTime == self.sendRewardTimeStr and processedKey not in processedRankings:  # 发今日赢家榜奖励
            yesterday = date.today() - timedelta(days=1)
            yesterdayTimestamp = int(time.mktime(yesterday.timetuple()))  # 昨天开始时间
            cacheRanking = self._getRanking(yesterdayTimestamp)
            cacheRanking = copy.deepcopy(cacheRanking[2]["rankData"])
            processedRankings.append(processedKey)
            totalPoolNum = poseidon_lottery_pool.getPoseidonWealthPool(True)
            bireport.reportGameEvent("BI_NFISH_GE_POSEIDON_LOTTERY", config.ROBOT_MAX_USER_ID, FISH_GAMEID, 0,
                                     0, 0, int(totalPoolNum), 0, 0, [], config.CLIENTID_ROBOT)
            ftlog.info("processRankings =", processedKey, self.rankDefine.rankingId,
                       cacheRanking, processedRankings, totalPoolNum)

            for rankData in cacheRanking:
                randRewards = self._getPoseidonReward(rankData["rank"], totalPoolNum)
                if ftlog.is_debug():
                    ftlog.debug("processRankings", rankData, randRewards)
                self._sendRewards(rankData, RankType.PoseidonTodayWinner, randRewards)
                self._sendRankOverEvent(rankData)
                self._reportBIEvent(rankData)


class YestodayPoseidonRanking(TodayPoseidonRanking):
    """
    海皇昨日赢家榜
    """
    def getRankingInfo(self):
        ranking = super(TodayPoseidonRanking, self).getRankingInfo()
        rankRewardConf = self.rankConf
        ranking["rankDesc"] = ""
        if ranking["rankData"] and len(ranking["rankData"]) > 1:
            rankDescId = rankRewardConf.get("rankDesc")
            ranking["rankDesc"] = strutil.replaceParams(config.getMultiLangTextConf(str(rankDescId), lang=self.lang),
                                                        {"userName": ranking["rankData"][1]["name"]})
        return ranking

    def getRanking(self, timestamp=None, refresh=False):
        return self._getHistoryRanking()

    def _getOneUserScore(self, userId, score, isOwner=False):
        dateTime = date.today() - timedelta(days=1)
        score = poseidon_lottery_pool.getPoseidonWinMostData(userId, dateTime)
        return score

    def _getOneUserReward(self, userId, rank, poolNum=0, score=0):
        rewards = []
        if poolNum == 0 or not poolNum:
            poolNum = poseidon_lottery_pool.getPoseidonWealthPool(True)
        rankRewards = self._getPoseidonReward(rank, poolNum)
        if ftlog.is_debug():
            ftlog.debug("YestodayPoseidonRanking", rankRewards, poolNum)
        if rankRewards and rankRewards["rewards"]:
            rewards = self._buildRewards(rankRewards["rewards"])
        return rewards

    def _getOwnRankingTime(self):
        dateArray = datetime.fromtimestamp(pktimestamp.getCurrentTimestamp())
        yesterday = dateArray - timedelta(days=1)
        timestamp = pktimestamp.getDayStartTimestamp(time.mktime(yesterday.timetuple()))
        return timestamp


class WeekPoseidonRanking(RankingBase):
    """
    海皇七日赢家榜
    """
    def _getOneUserScore(self, userId, score, isOwner=False):
        return poseidon_lottery_pool.getPoseidon7WinMostData(userId)

    def refreshRankingData(self, event):
        """
        刷新排行榜数据
        """
        userId = event.userId
        coin = event.coin
        lastCoin = poseidon_lottery_pool.getPoseidon7WinMostData(userId)
        if coin > lastCoin:
            timestamp = pktimestamp.getCurrentTimestamp()
            weekMostData = [coin, timestamp]
            poseidon_lottery_pool.setPoseidon7WinMostData(userId, weekMostData)
            self.saveUserScore(config.RANK_POSEIDON_SEVEN_WIN, userId, coin, timestamp)

    def processRanking(self, todayDate, strfTime):
        processedKey = self._getProcessedKey(todayDate)
        timestamp = pktimestamp.getCurrentTimestamp()
        if strfTime == self.clearDataTime and processedKey not in processedRankings:  # 删除七天前数据
            rankingDefine = self.rankDefine
            poseidon7Rank = self.getTopNRankUsers(timestamp, rankingDefine)
            processedRankings.append(processedKey)
            for userRankInfo in poseidon7Rank.rankingUserList:
                poseidon7Score = poseidon_lottery_pool.getPoseidon7WinMostData(userRankInfo.userId)
                if poseidon7Score == 0:
                    poseidon_lottery_pool.delPoseidon7WinMostData(userRankInfo.userId)
                    hallranking.rankingSystem.removeUser(rankingDefine.rankingId, userRankInfo.userId)


class CompActTeamRanking(TodayRankingBase):
    """
    竞赛活动team积分榜
    """
    def __init__(self, userId, rankType, defineIndex, clientId=None, httpRequest=False, mailType=MailRewardType.SystemReward):
        super(CompActTeamRanking, self).__init__(userId, rankType, defineIndex, clientId, httpRequest, mailType)
        self.enableSortRank = False
        self.teamId = -1
        for rt, idx in CompActRankTypeDefineIndexDict.iteritems():
            if idx == defineIndex:
                self.teamId = CompActRankList.index(rt)
                break
        from newfish.entity.fishactivity import competition_activity
        self.teamPoint = competition_activity._getCompTeamPointShow(self.teamId)
        self.bonusPool = competition_activity._getCompBonusPool(int(time.time()))
        self.isChampionTeam = competition_activity.isChampionTeam(self.rankType)
        self.rankExtraRewards = config.getCompActConf(clientId).get("rankRewards", [])
        self.championRankExtraRewards = config.getCompActConf(clientId).get("winnerRankRewards", [])

    def refreshRankingData(self, data):
        """
        刷新排行榜数据
        """
        userId = data[0]
        count = data[1]
        timestamp = pktimestamp.getCurrentTimestamp()
        self.saveUserScore(str(self.rankDefine.rankingId), userId, count, timestamp)

    def getTotalNRanking(self, timestamp=None):
        timestamp = timestamp or pktimestamp.getCurrentTimestamp()
        rankingList = self.getTotalNRankUsers(timestamp, self.rankDefine)
        rankData = []
        if ftlog.is_debug():
            ftlog.debug("_getRanking, rankType =", self.rankType, "rankingList =", len(rankingList.rankingUserList))
        for index, user in enumerate(rankingList.rankingUserList):
            if user.userId == 0:
                continue
            score = self._getOneUserScore(user.userId, user.score)
            oneUserRankData = {
                "userId": user.userId,
                "score": score,
                "rank": user.rank + 1
            }
            rankData.append(oneUserRankData)
        return (rankingList, int(time.time()), {
            "rankId": self.rankDefine.rankingId,
            "issueNum": rankingList.issueNumber,
            "name": rankingList.rankingDefine.name,
            "desc": rankingList.rankingDefine.desc,
            "type": rankingList.rankingDefine.rankingType,
            "rankData": rankData
        })

    def processRanking(self, todayDate, strfTime):
        """
        处理排行榜发奖
        """
        from newfish.entity.fishactivity import competition_activity
        if not competition_activity.isActEnable():
            return
        processedKey = self._getProcessedKey(todayDate)
        timestamp = pktimestamp.getCurrentTimestamp()
        if ftlog.is_debug():
            ftlog.debug("CompActTeamRanking->processRanking, rank =", processedKey,
                        strfTime, self.sendRewardTimeStr, processedRankings)
        # 今日榜发奖
        if strfTime == self.sendRewardTimeStr and processedKey not in processedRankings:
            processedRankings.append(processedKey)
            self.isChampionTeam = competition_activity.isChampionTeam(self.rankType)
            # # 判断自己team是否为获胜team，只有第一名的team才发奖
            # if not self.isChampionTeam:
            #     return
            ftlog.info("CompActTeamRanking, champion! processRankings =", processedKey, self.rankDefine.rankingId, self.rankType)
            rankRewardConf = config.getRankRewardConf(self.rankType)
            rankRewardsList = rankRewardConf.get("rankRewards")
            if not rankRewardsList:
                ftlog.info("CompActTeamRanking, no rewards, processRankings =", processedKey, self.rankDefine.rankingId, processedRankings)
                return
            cacheRanking = self.getTotalNRanking(timestamp)
            cacheRanking = copy.deepcopy(cacheRanking[2]["rankData"])
            ftlog.info("CompActTeamRanking, ", processedKey, self.rankDefine.rankingId, len(cacheRanking))
            _begin = time.time()
            for rankData in cacheRanking:
                if not self.isChampionTeam and rankData["rank"] > len(self.rankExtraRewards):
                    break
                self._sendRewards(rankData, self.rankType)
                self._reportBIEvent(rankData, param01=rankData["score"])
            ftlog.info("CompActTeamRanking, rankingId =", self.rankDefine.rankingId,
                       "rankLen =", len(cacheRanking), "costTime =", time.time() - _begin, "s")

    def _getProcessedRewards(self, rankData, rankRewards):
        """
        获取处理后的最终奖励
        """
        userId = rankData["userId"]
        rank = rankData["rank"]
        score = rankData["score"]
        rewards = []
        for reward in rankRewards["rewards"]:
            name = reward["itemId"]
            if name == "user:chip":
                name = CHIP_KINDID
            elif name == "user:coupon":
                name = COUPON_KINDID
            else:
                name = int(name.split(":")[1])
            _cnt = self._getRewardCount(userId, score, rank, self.isChampionTeam)
            if _cnt > 0:
                rewards.append({"name": name, "count": _cnt})
        return rewards

    def _getProcessedMessage(self, rankData, rankRewards):
        """
        获取处理后的邮件内容
        """
        userId = rankData["userId"]
        rank = rankData["rank"]
        rankRewardConf = config.getRankRewardConf(self.rankType)
        rankNameId = rankRewardConf["rankName"]
        if self.isChampionTeam:
            if 0 < rank <= len(self.championRankExtraRewards):
                messageId = rankRewards["message"]
            else:
                messageId = rankRewards["message1"]
        else:
            messageId = rankRewards["message2"]
        lang = util.getLanguage(userId)
        message = config.getMultiLangTextConf(str(messageId), lang=lang)
        params = {"rank": rank, "rankName": config.getMultiLangTextConf(str(rankNameId), lang=lang)}
        message = strutil.replaceParams(message, params)
        return message

    def _getRewardCount(self, userId, score, rank, hasScoreRewards=True):
        from newfish.entity.fishactivity import competition_activity
        if hasScoreRewards:
            _count = competition_activity.calculateUserRankRewardCount(userId, CompActRankList.index(self.rankType), score,
                                                                 teamPoint=self.teamPoint, bonusPool=self.bonusPool)
            if 0 < rank <= len(self.championRankExtraRewards):
                _count += self.championRankExtraRewards[rank - 1]["count"]
        else:
            _count = 0
        if 0 < rank <= len(self.rankExtraRewards):
            _count += self.rankExtraRewards[rank - 1]["count"]
        return _count

    def _getOneUserReward(self, userId, rank, poolNum=0, score=0):
        """
        获取排名对应奖励
        """
        rewards = []
        rankRewards = self._getRankRewards(rank)
        if rankRewards and rankRewards["rewards"]:
            count = self._getRewardCount(userId, score, rank)
            if count:
                rewards = self._buildRewards(rankRewards["rewards"])
                if rewards:
                    rewards[0]["num"] = count
        return rewards


class YestordayCompActTeamRanking(CompActTeamRanking):
    """
    上期竞赛team积分榜
    """
    def __init__(self, userId, rankType, defineIndex, clientId=None, httpRequest=False, mailType=MailRewardType.SystemReward):
        super(YestordayCompActTeamRanking, self).__init__(userId, rankType, defineIndex, clientId, httpRequest, mailType)
        from newfish.entity.fishactivity import competition_activity
        ts = self._getOwnRankingTime()
        self.teamPoint = competition_activity._getCompTeamPointShow(self.teamId, ts)
        self.bonusPool = competition_activity._getCompBonusPool(ts)

    def getRankingInfo(self):
        ranking = super(YestordayCompActTeamRanking, self).getRankingInfo()
        rankRewardConf = self.rankConf
        # 替换排行榜描述文本
        ranking["rankDesc"] = ""
        if ranking["rankData"] and len(ranking["rankData"]) > 1:
            rankDescId = rankRewardConf.get("rankDesc")
            if rankDescId:
                ranking["rankDesc"] = strutil.replaceParams(config.getMultiLangTextConf(str(rankDescId), lang=self.lang),
                                                        {"userName": ranking["rankData"][1]["name"]})
            else:
                ranking["rankDesc"] = ""
        return ranking

    def getRanking(self, timestamp=None, refresh=False):
        return self._getHistoryRanking()

    def _getHistoryTimeAndUpdate(self, historyCacheRanking, currentTimestamp, yesterday):
        """
        获取历史榜单的时间戳和判断是否需要更新历史榜单
        """
        timestamp = currentTimestamp
        if currentTimestamp - pktimestamp.getDayStartTimestamp(currentTimestamp) < self.sendRewardTimeInt:
            timestamp = pktimestamp.getDayStartTimestamp(time.mktime(yesterday.timetuple()))
        if historyCacheRanking:
            isUpdate = currentTimestamp - pktimestamp.getDayStartTimestamp(
                historyCacheRanking[1]) >= self.sendRewardTimeInt
        else:
            isUpdate = True
        return timestamp, isUpdate

    def _getOneUserScore(self, userId, score, isOwner=False):
        if isOwner:
            timestamp = pktimestamp.getCurrentTimestamp()
            if timestamp - pktimestamp.getDayStartTimestamp(timestamp) < self.sendRewardTimeInt:
                dateArray = datetime.fromtimestamp(timestamp)
                yesterday = dateArray - timedelta(days=1)
                timestamp = pktimestamp.getDayStartTimestamp(time.mktime(yesterday.timetuple()))

            userRankData = hallranking.rankingSystem.getRankingUser(self.rankDefine.rankingId,
                                                                    self.userId, timestamp)
            return userRankData.score or self._getGameData9999RankInfo(userId, timestamp)
        return score

    def _getOwnRankingTime(self):
        timestamp = pktimestamp.getCurrentTimestamp()
        if timestamp - pktimestamp.getDayStartTimestamp(timestamp) < self.sendRewardTimeInt:
            dateArray = datetime.fromtimestamp(timestamp)
            yesterday = dateArray - timedelta(days=1)
            timestamp = pktimestamp.getDayStartTimestamp(time.mktime(yesterday.timetuple()))
        return timestamp

    def _getRewardCount(self, userId, score, rank, ignoreScoreRewards=False):
        from newfish.entity.fishactivity import competition_activity
        _count = competition_activity.calculateUserRankRewardCount(userId, self.teamId, score,
                                                                 teamPoint=self.teamPoint, bonusPool=self.bonusPool)
        if 0 < rank <= len(self.rankExtraRewards):
            _count += self.rankExtraRewards[rank - 1]["count"]
        if 0 < rank <= len(self.championRankExtraRewards):
            _count += self.championRankExtraRewards[rank - 1]["count"]
        return _count

    def _getOwnRanking(self, userId, rankDatas):
        """
        获取指定玩家排名相关数据
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
                    if rankData.rank <= self.rankDefine.totalN else rankData.rank + 1

        score = self._getOneUserScore(userId, score, True)
        rewards = self._getOneUserReward(userId, rank, score=score)
        vipLevel = util.getVipShowLevel(userId)
        ownRankingDataDic = {
                                "userId": userId,
                                "name": name,
                                "sex": sex,
                                "score": score,
                                "rank": rank,
                                "avatar": avatar,
                                "vip": vipLevel,
                                "rewards": rewards}
        return ownRankingDataDic


class CompActPointRanking(TodayRankingBase):
    """
    竞赛活动积分榜
    """
    def __init__(self, userId, rankType, defineIndex, clientId=None, httpRequest=False, mailType=MailRewardType.SystemReward):
        super(CompActPointRanking, self).__init__(userId, rankType, defineIndex, clientId, httpRequest, mailType)
        self.enableSortRank = False

    def refreshRankingData(self, data):
        """
        刷新排行榜数据
        """
        userId = data[0]
        count = data[1]
        timestamp = pktimestamp.getCurrentTimestamp()
        # 发奖时间不是0点需要特殊处理.
        if timestamp - pktimestamp.getDayStartTimestamp(timestamp) >= self.updateRankTimeInt > 0:
            dateArray = datetime.fromtimestamp(timestamp)
            tomorrow = dateArray + timedelta(days=1)
            timestamp = pktimestamp.getDayStartTimestamp(time.mktime(tomorrow.timetuple()))
        self.saveUserScore(str(self.rankDefine.rankingId), userId, count, timestamp)

    def processRanking(self, todayDate, strfTime):
        """
        处理排行榜发奖
        """
        from newfish.entity.fishactivity import competition_activity
        if not competition_activity.isActEnable():
            return False
        processedKey = self._getProcessedKey(todayDate)
        timestamp = pktimestamp.getCurrentTimestamp()
        if ftlog.is_debug():
            ftlog.debug("CompActPointRanking->processRanking, rank =", processedKey,
                        strfTime, self.sendRewardTimeStr, processedRankings)
        # 在发榜的时候存储玩家的排名数据用于第二天分队使用.
        if strfTime == self.sendRewardTimeStr and processedKey not in processedRankings:
            processedRankings.append(processedKey)
            # 没有冠军team证明活动已经结束,不用处理以下逻辑.
            rankType = competition_activity.findChampionTeamRankType(int(time.time()) - 600)
            ftlog.info("CompActPointRanking->processRanking, champion team rankType =", rankType)
            if rankType == 0:
                return False
            cacheRanking = self.getRanking(timestamp, True)
            cacheRanking = copy.deepcopy(cacheRanking[2]["rankData"])
            ftlog.info("CompActPointRanking, ", processedKey, self.rankDefine.rankingId, cacheRanking,
                       processedRankings)
            lastTS = str(util.getDayStartTimestamp(int(time.time()) - 600))
            for rankData in cacheRanking:
                userId = rankData["userId"]
                rank = rankData["rank"]
                gamedata.setGameAttr(userId, FISH_GAMEID, GameData.lastCompActRank, json.dumps([lastTS, rank]))
            return True
        else:
            # 发榜前清理上期榜记录，以免玩家在发奖时间临界点访问到错误榜单.
            if strfTime == self.clearDataTime:
                competition_activity.clearLastChampionTeamRankType()
            return False


class ItemHappyDoubleRanking(RankingBase):
    """
    翻番乐活动收集道具排行榜
    """
    def _getOneUserScore(self, userId, score, isOwner=False):
        if isOwner and not score:
           score = weakdata.getDayFishData(userId, WeakData.itemHappyDoubleCount, 0)
        return score

    def refreshRankingData(self, event):
        """
        刷新排行榜数据
        """
        userId = event.userId
        rewards = event.rewards
        timestamp = pktimestamp.getCurrentTimestamp()
        for reward in rewards:
            if reward["name"] == config.getActItemHappyDoubleConfig().get("kindId"):
                count = reward.get("count", 0)
                self.saveUserScore(config.RANK_ITEM_HAPPY_DOUBLE, userId, count, timestamp)

    def processRanking(self, todayDate, strfTime):
        """
        处理排行榜发奖
        """
        processedKey = self._getProcessedKey(todayDate)
        if ftlog.is_debug():
            ftlog.debug("ItemHappyDoubleRanking.processRanking", strfTime, self.sendRewardTimeStr, processedKey, processedRankings)
        if strfTime == self.sendRewardTimeStr and processedKey not in processedRankings:
            yesterday = date.today() - timedelta(days=1)
            yesterdayTimestamp = int(time.mktime(yesterday.timetuple()))
            cacheRanking = self._getRanking(yesterdayTimestamp)
            cacheRanking = copy.deepcopy(cacheRanking[2]["rankData"])
            processedRankings.append(processedKey)
            ftlog.info("processRankings =", processedKey, self.rankDefine.rankingId,
                       cacheRanking, processedRankings)
            for rankData in cacheRanking:
                self._sendRewards(rankData, RankType.ItemHappyDouble)
                self._reportBIEvent(rankData, param01=rankData["score"])


class SuperbossPointRanking(TodayRankingBase):
    """
    超级boss积分榜
    """
    def __init__(self, userId, rankType, defineIndex, clientId=None, httpRequest=False, mailType=MailRewardType.SystemReward):
        super(SuperbossPointRanking, self).__init__(userId, rankType, defineIndex, clientId, httpRequest, mailType)
        self.bigRoomId = SbossRankDefineIdxBigRoomIdDict.get(self.rankDefineIndex)
        from newfish.entity.superboss import gameplay
        mode = 1 if self.rankType in SbossPointRankTypeRingList else 0
        self.bonusPool = gameplay.getSuperbossBonusPool(self.bigRoomId, mode)

    def refreshRankingData(self, data):
        """
        刷新排行榜数据
        """
        userId = data.userId
        count = data.point
        timestamp = pktimestamp.getCurrentTimestamp()
        self.saveUserScore(str(self.rankDefine.rankingId), userId, count, timestamp)

    def getTotalNRanking(self, timestamp=None):
        timestamp = timestamp or pktimestamp.getCurrentTimestamp()
        rankingList = self.getTotalNRankUsers(timestamp, self.rankDefine)
        rankData = []
        if ftlog.is_debug():
            ftlog.debug("_getRanking, rankType =", self.rankType, "rankingList =", len(rankingList.rankingUserList))
        for index, user in enumerate(rankingList.rankingUserList):
            if user.userId == 0:
                continue
            score = self._getOneUserScore(user.userId, user.score)
            oneUserRankData = {
                "userId": user.userId,
                "score": score,
                "rank": user.rank + 1
            }
            rankData.append(oneUserRankData)
        return (rankingList, int(time.time()), {
            "rankId": self.rankDefine.rankingId,
            "issueNum": rankingList.issueNumber,
            "name": rankingList.rankingDefine.name,
            "desc": rankingList.rankingDefine.desc,
            "type": rankingList.rankingDefine.rankingType,
            "rankData": rankData
        })

    def processRanking(self, todayDate, strfTime):
        """
        处理排行榜发奖
        """
        processedKey = self._getProcessedKey(todayDate)
        if ftlog.is_debug():
            ftlog.debug("SuperbossPointRanking, processRanking, rank =", processedKey,
                        strfTime, self.sendRewardTimeStr, processedRankings)
        # 今日榜发奖
        if strfTime == self.sendRewardTimeStr and processedKey not in processedRankings:
            processedRankings.append(processedKey)
            yesterday = date.today() - timedelta(days=1)
            yesterdayTimestamp = int(time.mktime(yesterday.timetuple()))  # 昨天开始时间
            cacheRanking = self.getTotalNRanking(yesterdayTimestamp)
            cacheRanking = copy.deepcopy(cacheRanking[2]["rankData"])
            ftlog.info("SuperbossPointRanking, ", processedKey, self.rankDefine.rankingId, self.rankType, len(cacheRanking))
            for rankData in cacheRanking:
                self._sendRewards(rankData, self.rankType)
                self._reportBIEvent(rankData, param01=rankData["score"])
            # 发榜后清理过期的存档数据.
            from newfish.entity.superboss import gameplay
            gameplay.removeExpiredData(self.bigRoomId)

    def _getProcessedRewards(self, rankData, rankRewards):
        """
        获取处理后的最终奖励
        """
        userId = rankData["userId"]
        rank = rankData["rank"]
        score = rankData["score"]
        rewards = []
        for reward in rankRewards["rewards"]:
            name = reward["itemId"]
            if name == "user:chip":
                name = CHIP_KINDID
            elif name == "user:coupon":
                name = COUPON_KINDID
            else:
                name = int(name.split(":")[1])
            _cnt = self._getRewardCount(userId, score, rank, rankRewards)
            if _cnt > 0:
                rewards.append({"name": name, "count": _cnt})
        return rewards

    def _dealSendRewardsAfter(self, rankData, userId, rank, rewards):
        """
        处理完排行榜发奖后的逻辑
        @param rewards: 排名奖励可能还有宝藏加成
        """
        self._sendRankOverEvent(rankData, params={"rewards": rewards})

    def _getRewardCount(self, userId, score, rank, rankRewards):
        _count = int(self.bonusPool * rankRewards["rewardPercent"][rank % len(rankRewards["rewardPercent"]) - 1])
        return _count

    def _getOneUserReward(self, userId, rank, poolNum=0, score=0):
        """
        获取排名对应奖励
        """
        rewards = []
        rankRewards = self._getRankRewards(rank)
        if rankRewards and rankRewards["rewards"]:
            count = self._getRewardCount(userId, score, rank, rankRewards)
            if count:
                rewards = self._buildRewards(rankRewards["rewards"])
                if rewards:
                    rewards[0]["num"] = count
        return rewards


class YestordaySuperbossPointRanking(SuperbossPointRanking):
    """
    上期超级boss积分榜
    """
    def __init__(self, userId, rankType, defineIndex, clientId=None, httpRequest=False, mailType=MailRewardType.SystemReward):
        super(YestordaySuperbossPointRanking, self).__init__(userId, rankType, defineIndex, clientId, httpRequest, mailType)
        from newfish.entity.superboss import gameplay
        ts = self._getOwnRankingTime()
        mode = 1 if self.rankType in SbossPointRankTypeRingList else 0
        self.bonusPool = gameplay.getSuperbossBonusPool(self.bigRoomId, ts, mode)

    def getRankingInfo(self):
        ranking = super(YestordaySuperbossPointRanking, self).getRankingInfo()
        rankRewardConf = self.rankConf
        # 替换排行榜描述文本
        ranking["rankDesc"] = ""
        if ranking["rankData"] and len(ranking["rankData"]) > 1:
            rankDescId = rankRewardConf.get("rankDesc")
            if rankDescId:
                ranking["rankDesc"] = strutil.replaceParams(config.getMultiLangTextConf(str(rankDescId), lang=self.lang),
                                                        {"userName": ranking["rankData"][1]["name"]})
            else:
                ranking["rankDesc"] = ""
        return ranking

    def getRanking(self, timestamp=None, refresh=False):
        return self._getHistoryRanking()

    def _getHistoryTimeAndUpdate(self, historyCacheRanking, currentTimestamp, yesterday):
        """
        获取历史榜单的时间戳和判断是否需要更新历史榜单
        """
        timestamp = currentTimestamp
        if currentTimestamp - pktimestamp.getDayStartTimestamp(currentTimestamp) < self.sendRewardTimeInt:
            timestamp = pktimestamp.getDayStartTimestamp(time.mktime(yesterday.timetuple()))
        if historyCacheRanking:
            isUpdate = currentTimestamp - pktimestamp.getDayStartTimestamp(
                historyCacheRanking[1]) >= self.sendRewardTimeInt
        else:
            isUpdate = True
        return timestamp, isUpdate

    def _getOneUserScore(self, userId, score, isOwner=False):
        if isOwner:
            timestamp = pktimestamp.getCurrentTimestamp()
            if timestamp - pktimestamp.getDayStartTimestamp(timestamp) < self.sendRewardTimeInt:
                dateArray = datetime.fromtimestamp(timestamp)
                yesterday = dateArray - timedelta(days=1)
                timestamp = pktimestamp.getDayStartTimestamp(time.mktime(yesterday.timetuple()))

            userRankData = hallranking.rankingSystem.getRankingUser(self.rankDefine.rankingId,
                                                                    self.userId, timestamp)
            return userRankData.score or self._getGameData9999RankInfo(userId, timestamp)
        return score

    def _getOwnRankingTime(self):
        timestamp = pktimestamp.getCurrentTimestamp()
        if timestamp - pktimestamp.getDayStartTimestamp(timestamp) < self.sendRewardTimeInt:
            dateArray = datetime.fromtimestamp(timestamp)
            yesterday = dateArray - timedelta(days=1)
            timestamp = pktimestamp.getDayStartTimestamp(time.mktime(yesterday.timetuple()))
        if ftlog.is_debug():
            ftlog.debug("_getOwnRankingTime, rankType =", self.rankType, "timestamp =", timestamp, self.sendRewardTimeInt)
        return timestamp

    def _getRewardCount(self, userId, score, rank, rankRewards):
        _count = int(self.bonusPool * rankRewards["rewardPercent"][rank % len(rankRewards["rewardPercent"]) - 1])
        return _count

    def _getOwnRanking(self, userId, rankDatas):
        """
        获取指定玩家排名相关数据
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
                    if rankData.rank <= self.rankDefine.totalN else rankData.rank + 1

        score = self._getOneUserScore(userId, score, True)
        rewards = self._getOneUserReward(userId, rank, score=score)
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