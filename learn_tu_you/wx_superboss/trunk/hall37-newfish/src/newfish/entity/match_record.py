# -*- coding=utf-8 -*-
"""
Created by lichen on 2017/6/23.
"""


import json
import time

import freetime.util.log as ftlog
from newfish.entity import config
from poker.entity.dao import gamedata
from hall.entity import hallvip
from newfish.entity.event import MatchWinloseEvent


class MatchRecord(object):
    class Record(object):
        def __init__(self, bestRank, bestRankDate, isGroup, crownCount, playCount, luckyValue, recentRank):
            assert (isinstance(bestRank, (int, float)) and bestRank >= 0)
            assert (isinstance(bestRankDate, int) and bestRankDate >= 0)
            assert (isinstance(isGroup, int) and isGroup >= 0)
            assert (isinstance(crownCount, int) and crownCount >= 0)
            assert (isinstance(playCount, int) and playCount >= 0)
            assert (isinstance(luckyValue, int))
            assert (isinstance(recentRank, list))
            self.bestRank = int(bestRank)
            self.bestRankDate = bestRankDate
            self.isGroup = isGroup
            self.crownCount = crownCount
            self.playCount = playCount
            self.luckyValue = luckyValue
            self.recentRank = recentRank

        def update(self, rank, isGroup, luckyValue):
            if isGroup == 0 and self.isGroup == 1:
                self.bestRank = int(rank)
                self.bestRankDate = int(time.time())
                self.isGroup = 0
            elif isGroup == self.isGroup:
                if self.bestRank <= 0 or rank < self.bestRank:
                    self.bestRank = int(rank)
                    self.bestRankDate = int(time.time())
            if rank == 1 and self.isGroup == 0:
                self.crownCount += 1
            self.recentRank.append(rank)
            self.recentRank = self.recentRank[-5:]
            self.playCount += 1
            self.luckyValue = int(luckyValue)
            self.luckyValue = max(self.luckyValue, 0)
            self.luckyValue = min(self.luckyValue, 10000)

        @classmethod
        def fromDict(cls, d):
            bestRank = d.get("bestRank", 0)
            bestRankDate = d.get("bestRankDate", 0)
            isGroup = d.get("isGroup", 0)
            crownCount = d.get("crownCount", 0)
            playCount = d.get("playCount", 0)
            luckyValue = d.get("luckyValue", 10000)
            recentRank = d.get("recentRank", [])
            return MatchRecord.Record(int(bestRank), bestRankDate, isGroup, crownCount, playCount, luckyValue, recentRank)

        def toDict(self):
            return {"bestRank":int(self.bestRank),
                    "bestRankDate": self.bestRankDate,
                    "isGroup": self.isGroup,
                    "crownCount": self.crownCount,
                    "playCount": self.playCount,
                    "luckyValue": self.luckyValue,
                    "recentRank": self.recentRank
                    }

    @classmethod
    def initialize(cls, eventBus):
        eventBus.subscribe(MatchWinloseEvent, cls.onMatchWinlose)

    @classmethod
    def onMatchWinlose(cls, event):
        if event.userId <= config.ROBOT_MAX_USER_ID: # robot
            return
        record = cls.loadRecord(event.gameId, event.userId, event.matchId)
        record.update(event.rank, event.isGroup, event.luckyValue)
        cls.saveRecord(event.gameId, event.userId, event.matchId, record)

    @classmethod
    def updateAndSaveRecord(cls, event):
        if event["userId"] <= config.ROBOT_MAX_USER_ID:  # robot
            return
        record = cls.loadRecord(event["gameId"], event["userId"], event["matchId"])
        record.update(event["rank"], event["isGroup"], event["luckyValue"])
        cls.saveRecord(event["gameId"], event["userId"], event["matchId"], record)

    @classmethod
    def loadRecord(cls, gameId, userId, matchId):
        try:
            jstr = gamedata.getGameAttr(userId, gameId, cls.__buildField(matchId))

            if ftlog.is_debug():
                ftlog.debug("MatchRecord.loadRecord gameId=", gameId,
                                      "userId=", userId,
                                      "matchId=", matchId,
                                      "data=", jstr,
                                      caller=cls)
            if jstr:
                return MatchRecord.Record.fromDict(json.loads(jstr))
        except:
            ftlog.exception()
        vip = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
        key = "initLuckyValue:%d" % int(matchId)
        initVal = config.getVipConf(vip).get(key, 10000)
        if ftlog.is_debug():
            ftlog.debug("loadRecord, default value !", "userId =", userId, "key =", key, "vip =", vip, "initVal", initVal)
        return MatchRecord.Record(0, 0, 0, 0, 0, initVal, [])

    @classmethod
    def saveRecord(cls, gameId, userId, matchId, record):
        if ftlog.is_debug():
            ftlog.debug("MatchRecord.saveRecord gameId=", gameId,
                                  "userId=", userId,
                                  "matchId=", matchId,
                                  "record=", json.dumps(record.toDict()),
                                  caller=cls)
        gamedata.setGameAttr(userId, gameId, cls.__buildField(matchId), json.dumps(record.toDict()))

    @classmethod
    def __buildField(cls, matchId):
        return "m.%s" % matchId

