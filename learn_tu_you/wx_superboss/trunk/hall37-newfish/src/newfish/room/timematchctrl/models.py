#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/10

import random

from newfish.room.timematchctrl.const import SeatQueuingType, ScoreCalcType
from newfish.room.timematchctrl.utils import Logger
from newfish.entity.match_record import MatchRecord
from newfish.entity import config
from newfish.entity.config import FISH_GAMEID


class Signer(object):
    def __init__(self, userId, instId, matchId):
        # 用户ID
        self.userId = userId
        # 比赛实例ID
        self.instId = instId
        # 用户名
        self.userName = ""
        # 报名费
        self.fee = None
        # 报名时间
        self.signinTime = None
        # clientId
        self.clientId = ""
        # 游戏客户端版本
        self.gameClientVersion = 0
        # 是否在报名界面
        self.isEnter = False
        # 是否锁定了Location
        self.isLocked = False
        # 比赛实例
        self.inst = None
        record = MatchRecord.loadRecord(FISH_GAMEID, self.userId, matchId)
        # 幸运值
        self.luckyValue = record.luckyValue
        # 累计参赛次数
        self.playCount = record.playCount
        # 平均排名
        self.averageRank = sum(record.recentRank) / max((len(record.recentRank), 1))


class Player(object):
    ST_SIGNIN = 1
    ST_WAIT = 2
    ST_PLAYING = 3
    ST_WINLOSE = 4
    ST_RISE = 5
    ST_OVER = 6

    def __init__(self, userId):
        # 用户ID
        self.userId = userId
        # 实例ID
        self.instId = None
        # 用户名
        self.userName = ""
        # 报名费
        self.fee = None
        # 报名时间
        self.signinTime = None
        # clientId
        self.clientId = ""
        # 游戏客户端版本
        self.gameClientVersion = 0
        # 当前积分
        self.score = 0
        # 当前排名
        self.rank = 0
        # 当前桌子排名
        self.tableRank = 0
        # 等待时间
        self.waitTimes = 0
        # 状态
        self._state = Player.ST_SIGNIN
        # 座位
        self._seat = None
        # 当前所在分组
        self._group = None
        # 胜了哪些人
        self.beatDownUserName = None
        # 牌手编号
        self.playerNo = None
        # 用户是否退出
        self.isQuit = 0
        # 幸运值
        self.luckyValue = 0
        # 累计参赛次数
        self.playCount = 0
        # 平均排名
        self.averageRank = 0

    @property
    def state(self):
        return self._state

    @property
    def group(self):
        return self._group

    @property
    def stage(self):
        return self._group.stage

    @property
    def seat(self):
        return self._seat

    @property
    def seatId(self):
        return self._seat.seatId

    @property
    def table(self):
        return self._seat.table if self._seat else None


class Seat(object):
    def __init__(self, table, seatId):
        self._table = table
        self._seatId = seatId
        self._location = "%s.%s.%s.%s" % (table.gameId, table.roomId, table.tableId, seatId)
        self._player = None

    @property
    def gameId(self):
        return self.table.gameId

    @property
    def table(self):
        return self._table

    @property
    def seatId(self):
        return self._seatId

    @property
    def roomId(self):
        return self.table.roomId

    @property
    def tableId(self):
        return self.table.tableId

    @property
    def location(self):
        return self._location

    @property
    def player(self):
        return self._player


class Table(object):
    def __init__(self, gameId, roomId, tableId, seatCount):
        # 游戏ID
        self._gameId = gameId
        # 房间ID
        self._roomId = roomId
        # 座位ID
        self._tableId = tableId
        # 所有座位
        self._seats = self._makeSeats(seatCount)
        # 空闲座位
        self._idleSeats = self._seats[:]
        # 使用该桌子的比赛
        self._group = None
        # 当前牌局开始时间
        self._playTime = None
        # 桌子Location
        self._location = "%s.%s.%s" % (self.gameId, self.roomId, self.tableId)
        # 桌子排名比例
        self._tableRankRatio = 0

    @property
    def gameId(self):
        return self._gameId

    @property
    def roomId(self):
        return self._roomId

    @property
    def tableId(self):
        return self._tableId

    @property
    def seats(self):
        return self._seats

    @property
    def group(self):
        return self._group

    @property
    def location(self):
        return self._location

    @property
    def seatCount(self):
        return len(self._seats)

    @property
    def playTime(self):
        return self._playTime

    @property
    def tableRankRatio(self):
        return self._tableRankRatio

    @property
    def idleSeatCount(self):
        """
        空闲座位的数量
        """
        return len(self._idleSeats)

    def getPlayingPlayerCount(self):
        """
        获取PLAYING状态的玩家数量
        """
        count = 0
        for seat in self._seats:
            if seat.player and seat.player.state == Player.ST_PLAYING:
                count += 1
        return count

    def getPlayingPlayerList(self):
        playerList = []
        for seat in self._seats:
            if seat.player and seat.player.state == Player.ST_PLAYING:
                playerList.append(seat.player)
        return playerList

    def getPlayerList(self):
        """
        获取本桌的所有player
        """
        return [seat.player for seat in self.seats if seat.player]

    def getUserIdList(self):
        """
        获取本桌所有userId
        """
        ret = []
        for seat in self.seats:
            ret.append(seat.player.userId if seat.player else 0)
        return ret

    def sitdown(self, player):
        """
        玩家坐下
        """
        assert (player._seat is None)
        assert (len(self._idleSeats) > 0)
        seat = self._idleSeats[-1]
        del self._idleSeats[-1]
        seat._player = player
        player._table = self
        player._seat = seat

    def standup(self, player):
        """
        玩家离开桌子
        """
        assert (player._seat is not None
                and player._seat.table == self)
        self._clearSeat(player._seat)

    def clear(self):
        """
        清理桌子上的所有玩家
        """
        for seat in self._seats:
            if seat._player:
                self.standup(seat._player)

    def _clearSeat(self, seat):
        seat._player._seat = None
        seat._player = None
        self._idleSeats.append(seat)

    def _makeSeats(self, count):
        assert (count > 0)
        seats = []
        for i in xrange(count):
            seats.append(Seat(self, 2 * i + 1))
        return seats


class PlayerSort(object):
    @classmethod
    def cmpByScore(cls, p1, p2):
        if p1.score == p2.score:
            return cls.cmpBySigninTime(p1, p2)
        if p1.score < p2.score:
            return 1
        return -1

    @classmethod
    def cmpBySigninTime(cls, p1, p2):
        return cmp(p1.signinTime, p2.signinTime)

    @classmethod
    def cmpByLucky(cls, p1, p2):
        if p1.userId <= config.ROBOT_MAX_USER_ID:
            return 1
        if p2.userId <= config.ROBOT_MAX_USER_ID:
            return -1
        if p1.playCount >= 5:
            if p2.playCount >= 5:
                if cls.getLuckyValue(p1) >= cls.getLuckyValue(p2):
                    return 1
                else:
                    return -1
            else:
                return 1
        else:
            if p2.playCount >= 5:
                return -1
            else:
                if p1.luckyValue >= p2.luckyValue:
                    return 1
                else:
                    return -1

    @classmethod
    def getLuckyValue(cls, player):
        return player.averageRank + player.luckyValue / random.randint(500, 1000) + random.randint(-2, 5)

    @classmethod
    def cmpByTableRanking(cls, p1, p2):
        if p1.tableRank <= 0 and p2.tableRank <= 0:
            return cls.cmpByScore(p1, p2)
        if (p1.tableRank == p2.tableRank):
            return cls.cmpByScore(p1, p2)
        if p1.tableRank <= 0:
            return 1
        if p2.tableRank <= 0:
            return -1
        if p1.tableRank > p2.tableRank:
            return 1
        return -1


class PlayerQueuingImpl(object):
    def sort(self, players):
        """排序players，并返回排序后的列表"""
        raise NotImplementedError


class PlayerQueuingRandom(PlayerQueuingImpl):
    def sort(self, players):
        random.shuffle(players)
        return players


class PlayerQueuingSnake(PlayerQueuingImpl):
    def sort(self, players):
        return players


class PlayerQueuingScore(PlayerQueuingImpl):
    def sort(self, matchUserList):
        matchUserList.sort(PlayerSort.cmpByScore)
        return matchUserList


class PlayerQueuingSigninTime(PlayerQueuingImpl):
    def sort(self, matchUserList):
        matchUserList.sort(PlayerSort.cmpBySigninTime)
        return matchUserList


class PlayerQueuingLucky(PlayerQueuingImpl):
    def sort(self, matchUserList):
        matchUserList.sort(PlayerSort.cmpByLucky)
        return matchUserList


class PlayerQueuing(object):
    _defaultQueuing = PlayerQueuingRandom()
    _queuingMap = {
        SeatQueuingType.RANDOM: _defaultQueuing,
        SeatQueuingType.SNAKE: PlayerQueuingSnake(),
        SeatQueuingType.SEED: PlayerQueuingScore(),
        SeatQueuingType.SIGNIN_TIME: PlayerQueuingSigninTime(),
        SeatQueuingType.LUCKY: PlayerQueuingLucky()
    }

    @classmethod
    def sort(cls, queuingType, players):
        if queuingType in cls._queuingMap:
            return cls._queuingMap[queuingType].sort(players)
        return cls._defaultQueuing.sort(players)


class PlayerScoreCalcImpl(object):
    def calc(self, score):
        raise NotImplementedError


class PlayerScoreCalcFixed(PlayerScoreCalcImpl):
    def __init__(self, value):
        self._value = value

    def calc(self, score):
        if self._value == 0:
            return score
        return int(self._value)


class PlayerScoreCalcPingFangGen(PlayerScoreCalcImpl):
    def calc(self, score):
        return int(score ** 0.5)


class PlayerScoreCalcBaiFenBi(PlayerScoreCalcImpl):
    def __init__(self, rate):
        self._rate = rate

    def calc(self, score):
        return int(score * self._rate)


class PlayerScoreCalcKaiFangFangDa(PlayerScoreCalcImpl):
    def __init__(self, base, middle):
        self._base = base
        self._middle = max(middle, 1)
        self._rate = self._base / self._middle ** 0.5

    def calc(self, score):
        if score < 0:
            score = 0
        return int((score ** 0.5) * self._rate)


class PlayerScoreCalc:
    _pingFangGenInstance = PlayerScoreCalcPingFangGen()

    @classmethod
    def makeCalc(cls, stageConf, playerList):
        calcType = stageConf.chipUser
        if calcType == ScoreCalcType.PING_FANG_GEN:
            return cls._pingFangGenInstance
        elif calcType == ScoreCalcType.BAI_FEN_BI:
            rate = float(stageConf.chipUserRate)
            return PlayerScoreCalcBaiFenBi(rate)
        elif calcType == ScoreCalcType.KAI_FANG_FANG_DA:
            base = float(stageConf.chipUserBase)
            middle = len(playerList) / 2
            return PlayerScoreCalcKaiFangFangDa(base, playerList[middle].score)
        return PlayerScoreCalcFixed(calcType)


class PlayerGrouping(object):
    @classmethod
    def groupingByGroupCount(cls, playerList, groupCount, tableSeatCount):
        # 计算按userCount分成groupCount组最合适的人数
        countPerGroup = len(playerList) / groupCount
        # 分组人数是tableSeatCount的倍数，选最接近的数
        countPerGroup += cls.calcFixCount(countPerGroup, tableSeatCount)
        ret = []
        pos = 0
        for _ in xrange(groupCount):
            nextPos = pos + countPerGroup
            ret.append(playerList[pos:nextPos])
            pos = nextPos

        rem = len(playerList) - pos
        if rem > 0:
            for i in xrange(groupCount):
                if pos >= len(playerList):
                    break
                ret[i].extend(playerList[pos:pos + tableSeatCount])
                pos += tableSeatCount
        return ret

    @classmethod
    def calcFixCount(cls, userCount, tableSeatCount):
        mod = userCount % tableSeatCount
        if mod == 0:
            return 0
        if mod != 0:
            add = tableSeatCount - mod
            if add < mod or (userCount - mod) < tableSeatCount:
                return add
            return -mod
        return 0

    @classmethod
    def groupingByMaxUserCountPerGroup(cls, playerList, userCount, tableSeatCount):
        groupCount = (len(playerList) + userCount - 1) / userCount
        # 计算按userCount分成groupCount组最合适的人数
        countPerGroup = len(playerList) / groupCount
        # 分组人数是tableSeatCount的倍数，选最接近的数
        countPerGroup += cls.calcFixCount(countPerGroup, tableSeatCount)
        countPerGroup = min(countPerGroup, userCount)
        ret = []
        pos = 0
        for _ in xrange(groupCount):
            nextPos = pos + countPerGroup
            ret.append(playerList[pos:nextPos])
            pos = nextPos

        rem = len(playerList) - pos
        if rem > 0:
            for i in xrange(groupCount):
                if pos >= len(playerList):
                    break
                addCount = min(tableSeatCount, userCount - len(ret[i]))
                ret[i].extend(playerList[pos:pos + addCount])
                pos += addCount
        return ret

    @classmethod
    def groupingByFixedUserCountPerGroup(cls, playerList, userCount):
        pos = 0
        ret = []
        while (pos < len(playerList)):
            nextPos = pos + userCount
            ret.append(playerList[pos:nextPos])
            pos = nextPos
        return ret


class GroupNameGenerator(object):
    GROUP_NAME_PREFIX = [chr(i) for i in range(ord("A"), ord("Z") + 1)]

    @classmethod
    def generateGroupName(cls, groupCount, i):
        assert (0 <= i < groupCount)
        groupName = GroupNameGenerator.GROUP_NAME_PREFIX[i % len(GroupNameGenerator.GROUP_NAME_PREFIX)]
        if groupCount > len(GroupNameGenerator.GROUP_NAME_PREFIX):
            number = i + 1
            if number % len(GroupNameGenerator.GROUP_NAME_PREFIX) != 0:
                groupName += "%s" % (number / len(GroupNameGenerator.GROUP_NAME_PREFIX) + 1)
            else:
                groupName += "%s" % (number / len(GroupNameGenerator.GROUP_NAME_PREFIX))
        return groupName + "组"


class TableManager(object):
    """桌子管理者"""
    def __init__(self, room, tableSeatCount):
        self._room = room
        self._tableSeatCount = tableSeatCount       # 桌子座位数
        self._idleTables = []
        self._allTableMap = {}
        self._roomIds = set()
        self._logger = Logger()
        self._logger.add("roomId", self._room.roomId)

    @property
    def tableSeatCount(self):
        return self._tableSeatCount

    @property
    def roomCount(self):
        return len(self._roomIds)

    @property
    def gameId(self):
        return self._room.gameId

    @property
    def allTableCount(self):
        """所有的桌子数"""
        return len(self._allTableMap)

    @property
    def idleTableCount(self):
        """空闲的桌子数"""
        return len(self._idleTables)

    @property
    def busyTableCount(self):
        """繁忙的桌子数"""
        return max(0, self.allTableCount - self.idleTableCount)

    def getTableCountPerRoom(self):
        return len(self._allTableMap) / max(1, self.roomCount)

    def addTable(self, table):
        assert (not table.tableId in self._allTableMap)
        assert (table.seatCount == self.tableSeatCount)
        self._idleTables.append(table)
        self._allTableMap[table.tableId] = table

    def addTables(self, roomId, baseId, count):
        if count > 0:
            self._roomIds.add(roomId)
        for i in xrange(count):
            tableId = baseId + i + 1  # 新框架里tableId 从 1开始计数， 0表示队列。
            table = Table(self.gameId, roomId, tableId, self._tableSeatCount)
            self._idleTables.append(table)
            self._allTableMap[tableId] = table

    def borrowTables(self, count):
        """
        从空闲的table中获取可用table
        """
        assert (self.idleTableCount >= count)
        ret = self._idleTables[0:count]
        self._idleTables = self._idleTables[count:]
        self._logger.info("TableManager.borrowTables",
                          "count=", count,
                          "idleTableCount=", self.idleTableCount,
                          "allTableCount=", self.allTableCount)
        return ret

    def returnTables(self, tables):
        """
        释放table到空闲状态
        """
        for table in tables:
            assert (self._allTableMap.get(table.tableId, None) == table)
            assert (not table.getPlayerList())
            self._idleTables.append(table)
        self._logger.info("TableManager.returnTables",
                          "count=", len(tables),
                          "idleTableCount=", self.idleTableCount,
                          "allTableCount=", self.allTableCount)

    def findTable(self, roomId, tableId):
        return self._allTableMap.get(tableId, None)
