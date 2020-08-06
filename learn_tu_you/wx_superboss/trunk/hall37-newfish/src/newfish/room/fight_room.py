# -*- coding:utf-8 -*-
"""
Created on 2017年12月26日

@author: haohongxian
"""

import random
from collections import OrderedDict

import freetime.util.log as ftlog
from poker.entity.biz.exceptions import TYBizException
from poker.entity.configure import gdata
from poker.entity.game.rooms.room import TYRoom
from poker.entity.dao import daobase
from poker.util import strutil
import poker.util.timestamp as pktimestamp
from hall.entity import hallitem
from hall.entity import hall_friend_table
from newfish.entity import config, util
from newfish.entity.config import FISH_GAMEID
from newfish.servers.table.rpc import table_remote


class FishFightRoom(TYRoom):
    """
    捕鱼渔友竞技房间
    """
    def __init__(self, roomdefine):
        super(FishFightRoom, self).__init__(roomdefine)
        if gdata.serverType() == gdata.SRV_TYPE_ROOM:       # 服务类型: 游戏的房间服务
            self._initGR()

    def newTable(self, tableId):
        """
        在GT中创建TYTable的实例
        """
        from newfish.table.fight_table import FishFightTable
        table = FishFightTable(self, tableId)
        return table

    def initializedGT(self, shadowRoomId, tableCount):
        pass

    def findFT(self, ftId):
        """查找房间"""
        if isinstance(ftId, int):
            ftId = str(ftId)
        ftlog.debug("findFT-----", self._ftMap, self._ftMap.get(ftId), ftId)
        return self._ftMap.get(ftId)

    def createFT(self, userId, ftConf):
        """创建房间"""
        ftId = self._genFTId()
        isCollectFee = False
        lang = util.getLanguage(userId)
        try:
            if self.runStatus != self.ROOM_STATUS_RUN:
                # raise TYBizException(8, u"游戏维护中，请稍后再试!")
                raise TYBizException(8, config.getMultiLangTextConf("ID_GAME_MAINTAIN_MSG", lang=lang))
            isIn, roomId, tableId, seatId = util.isInFishTable(userId)
            if isIn:
                # raise TYBizException(6, u"您在其他房间中!")
                raise TYBizException(6, config.getMultiLangTextConf("ID_CREAT_FT_IN_OTHER_ROOM", lang=lang))
            if not ftId:
                # raise TYBizException(2, u"渔场太火爆了，请稍后再试!")
                raise TYBizException(2, config.getMultiLangTextConf("ID_ENTER_ROOM_REASON", lang=lang))
            if self._tableManager.idleTableCount < 1:
                # raise TYBizException(2, u"渔场太火爆了，请稍后再试!")
                raise TYBizException(2, config.getMultiLangTextConf("ID_ENTER_ROOM_REASON", lang=lang))
            from newfish.entity.fishactivity import fish_activity_system
            code = fish_activity_system.isCanCreatRoom(userId, ftConf.fee)
            if code != 0:
                # raise TYBizException(code, u"次数不足或道具不够!")
                raise TYBizException(code, config.getMultiLangTextConf("ID_CREAT_FT_ITEM_NOT_ENOUGH", lang=lang))

            self._collectFee(userId, ftId, ftConf)
            isCollectFee = True
            ftBindRoomId(ftId, self.roomId)
            table = self._tableManager.borrowTable()
            ftTable = FTTable(userId, ftId, ftConf, pktimestamp.getCurrentTimestamp(), table)
            self._ftMap[ftId] = ftTable
            table._ftTable = ftTable
            # 通知桌子绑定了朋友桌
            self._tableCtrl.bindTable(ftTable.table)
            self.enterFT(userId, ftId)
            ftlog.info("FTRoom.createFT Success", "roomId=", self.roomId, "userId=", userId, "ftId=", ftId, "fee=", ftConf.fee)
            return 0
        except Exception, e:
            if isCollectFee:
                self._returnFee(userId, ftId, ftConf)
            releaseFTId(ftId)
            if not isinstance(e, TYBizException):
                ftlog.error("createFT", e, userId, ftConf)
                # raise TYBizException(7, u"创建房间失败，请稍后再试！")
                raise TYBizException(7, config.getMultiLangTextConf("ID_CREAT_FT_FAIL_MSG", lang=lang))
            raise e

    def disbindFT(self, ftId, isReturnFee):
        """释放自建桌子"""
        ftlog.debug("FriendRoom disbindFT", ftId)
        ftTable = self.findFT(ftId)
        if not ftTable:
            # raise TYBizException(-1,  u"没有找到该房间! ")
            lang = util.getLanguage(ftTable.userId)
            raise TYBizException(-1, config.getMultiLangTextConf("ID_NOT_FIND_ROOM", lang=lang))

        del self._ftMap[ftId]
        ftTable.table.clear()
        self._tableManager.returnTable(ftTable.table)
        releaseFTId(ftId)

        ftlog.info("FTRoom.disbindFT Succ", "roomId=", self.roomId, "userId=", ftTable.userId, "ftId=", ftTable.ftId, "fee=", ftTable.ftConf.fee)

    def enterFT(self, userId, ftId):
        """进入桌子"""
        ftlog.info("FTRoom.enterFT enterFT", "userId =", userId, "ftId =", ftId, "ftMap =", self._ftMap)
        lang = util.getLanguage(userId)
        try:
            if self.runStatus != self.ROOM_STATUS_RUN:
                # raise TYBizException(8, u"游戏维护中，请稍后再试！")
                raise TYBizException(8, config.getMultiLangTextConf("ID_GAME_MAINTAIN_MSG", lang=lang))
            if isinstance(ftId, int):
                ftId = str(ftId)
            ftTable = self.findFT(ftId)
            if not ftTable or not ftTable.table:
                # raise TYBizException(1, u"您输入的房间号不存在，请重新输入！")
                raise TYBizException(1, config.getMultiLangTextConf("ID_INPUT_ROOMID_ERROR_INFO", lang=lang))
            if ftTable.table.getUserNum() >= self.matchConf["table.seat.count"]:
                # raise TYBizException(3, u"当前房间人数已满！")
                raise TYBizException(3, config.getMultiLangTextConf("ID_ROOM_HAS_FULL", lang=lang))
            if not ftTable.table.getPlayer(userId):
                player = Player(userId)
                ftTable.table.sitdown(player)
                code = self._tableCtrl.tableEnter(ftTable.table, userId, player.seat.seatId)
            else:
                # raise TYBizException(4, u"当前房间人数已满！")
                raise TYBizException(4, config.getMultiLangTextConf("ID_HAS_IN_ROOM", lang=lang))
            return code
        except Exception, e:
            if not isinstance(e, TYBizException):
                ftlog.error("enterFT", e, userId, ftId)
                # raise TYBizException(7, u"加入房间失败，请稍后再试！")
                raise TYBizException(7, config.getMultiLangTextConf("ID_ENTER_ROOM_FAIL", lang=lang))
            raise e

    def userStandUp(self, ftId, userId):
        """用户离开桌子"""
        ftlog.debug("room userStandUp->", userId, ftId, self._ftMap)
        ftTable = self.findFT(ftId)
        if ftTable and ftTable.table:
            player = ftTable.table.getPlayer(userId)
            if player:
                ftTable.table.standup(player)
            ftlog.debug("room userStandUp->", userId, ftTable.table.getUserNum())

    def _returnFee(self, userId, ftId, ftConf):
        """返还门票"""
        if not ftConf.fee:
            return
        try:
            from newfish.entity import util
            code = util.addRewards(userId, ftConf.fee, "ROOM_GAME_FEE", int(ftId))
            ftlog.info("FTRoom._returnFee", "roomId=", self.roomId, "userId=", userId, "ftId=", ftId, "fee=", ftConf.fee, "final=", code)
        except:
            ftlog.error("FTRoom._returnFee", "roomId=", self.roomId, "userId=", userId, "ftId=", ftId, "fee=", ftConf.fee)

    def _collectFee(self, userId, ftId, ftConf):
        """收取门票"""
        ftlog.info("FTRoom._collectFee", "roomId=", self.roomId, "userId=", userId, "fee=", ftConf.fee)
        if ftConf.fee:
            userAssets = hallitem.itemSystem.loadUserAssets(userId)
            lang = util.getLanguage(userId)
            rewards = []
            for reward in ftConf.fee:
                surplusCount = userAssets.balance(FISH_GAMEID, "item:" + str(reward["name"]),
                                                  pktimestamp.getCurrentTimestamp())
                rewards.append({"name": reward["name"], "count": -abs(reward["count"])})
                if surplusCount < reward["count"]:
                    code = 5
                else:
                    code = util.addRewards(userId, rewards, "ROOM_GAME_FEE", int(ftId))
                if code:
                    raise TYBizException(5, config.getMultiLangTextConf("ID_ITEM_COUNT_NOT_ENOUGH", lang=lang))

    def _initGR(self):
        """初始化房间的桌子变量"""
        # 获取所有的bigRoomId
        self._ftMap = OrderedDict()                 # 桌子Id: 桌子对象
        self._tableCtrl = TableController()
        self._tableManager = self._buildTableManager()
        ftlog.info("FTRoom._initGR Succ", "roomId=", self.roomId, "tableCount=", self._tableManager.allTableCount)

    def _buildTableManager(self):
        """构建桌子管理者"""
        shadowRoomIds = self.roomDefine.shadowRoomIds
        seatCount = self.matchConf.get("table.seat.count")
        ftlog.info("FTRoom._buildTableManager", "roomId=", self.roomId, "shadowRoomIds=", list(shadowRoomIds), "seatCount=", seatCount)

        tableManager = TableManager(self)
        for roomId in self.roomDefine.shadowRoomIds:
            count = self.roomDefine.configure["gameTableCount"]
            baseId = roomId * 10000 + 1
            ftlog.info("FTRoom._buildTableManager addTables", "roomId=", self.roomId, "shadowRoomId=", roomId, "baseId=", baseId, "tableCount=", count)
            for i in xrange(count):
                table = Table(FISH_GAMEID, roomId, baseId + i, seatCount)
                tableManager.addTable(table)

        ftlog.info("FTRoom._buildTableManager Succ",
                   "roomId=", self.roomId,
                   "shadowRoomIds=", list(shadowRoomIds),
                   "seatCount=", seatCount,
                   "tableCount=", tableManager.allTableCount)
        return tableManager

    def _genFTId(self):
        """生成一个桌子Id"""
        for _ in xrange(10):
            ftId = genFTId()
            if not self.findFT(ftId):               # 找不到重复的房间号就是新房间
                return ftId
        return None


def ftExists(ftId):
    """是否存在此桌子"""
    ret = False
    try:
        ftBind = ftFind(ftId)
        if ftBind:
            from newfish.servers.room.rpc import room_remote
            ret = room_remote.ftExists(ftBind.get("roomId"), ftId)
    except:
        # 异常，有可能在用
        ret = True
        ftlog.error("ft_service.ftExists ftId=", ftId)

    ftlog.debug("ft_service.ftExists ftId=", ftId,
                "ret=", ret)
    return ret


def ftFind(ftId):
    """查找桌子"""
    jstr = None
    try:
        jstr = daobase.executeMixCmd("get", "ft:%s:%s" % (FISH_GAMEID, ftId))
        ftlog.debug("ft_service.ftFind ftId=", ftId,
                    "jstr=", jstr)
        if not jstr:
            return None
        return strutil.loads(jstr)
    except:
        ftlog.error("ft_service.ftFind ftId=", ftId,
                    "jstr=", jstr)
        return None


def ftBindRoomId(ftId, roomId):
    """桌子绑定房间"""
    daobase.executeMixCmd("set", "ft:%s:%s" % (FISH_GAMEID, ftId), strutil.dumps({"roomId": roomId}))


def genFTId():
    """生成房间Id"""
    for _ in xrange(10):
        ftId = hall_friend_table.createFriendTable(FISH_GAMEID)
        if ftId:
            return ftId
    return None


def releaseFTId(ftId):
    """释放桌子id"""
    try:
        daobase.executeMixCmd("del", "ft:%s:%s" % (FISH_GAMEID, ftId))
        hall_friend_table.releaseFriendTable(FISH_GAMEID, ftId)
    except:
        ftlog.error("ft_service.releaseFTId", "ftId=", ftId)


def collectCtrlRoomIds():
    """查询所有的控制房间"""
    bigRoomIds = gdata.gameIdBigRoomidsMap().get(FISH_GAMEID)
    ctrlRoomIds = []
    for bigRoomId in bigRoomIds:
        roomConf = gdata.getRoomConfigure(bigRoomId)
        if roomConf.get("typeName") == config.FISH_FIGHT:
            ctrlRoomIds.extend(gdata.bigRoomidsMap().get(bigRoomId, []))
    ctrlRoomIds.sort()
    return ctrlRoomIds


def roomIdForFTId(ftId):
    """根据桌子Id查找房间Id"""
    try:
        ftBind = ftFind(ftId)
        if ftBind:
            return ftBind.get("roomId", 0)
    except:
        ftlog.warn("ft_server.roomIdForFTId", "ftId=", ftId)
    return 0


def createFT(userId, fee):
    """
    创建自建桌
    @param userId: 谁创建
    @param fee: 服务费
    """
    ctrlRoomIds = collectCtrlRoomIds()
    lang = util.getLanguage(userId)
    if not ctrlRoomIds:
        ftlog.error("ft_service.createFT userId=", userId, "fee=", fee)
        raise TYBizException(7, config.getMultiLangTextConf("ID_CREAT_FT_FAIL_MSG", lang=lang))
    ctrlRoomId = random.choice(ctrlRoomIds)
    ftlog.debug("ft_service.createFT userId=", userId, "fee=", fee, "ctrlRoomId", ctrlRoomId)
    from newfish.servers.room.rpc import room_remote
    rewards = []
    for reward in fee:
        if reward and reward["count"] > 0:
            rewards.append(reward)
    code = room_remote.createFT(userId, ctrlRoomId, rewards)
    if isinstance(code, dict):
        raise TYBizException(code["errorCode"], code["message"])
    elif isinstance(code, Exception):
        ftlog.error("createFT", code, userId)
        raise TYBizException(7, config.getMultiLangTextConf("ID_CREAT_FT_FAIL_MSG", lang=lang))
    return code


class Player(object):
    """
    比赛中的用户
    """

    def __init__(self, userId):
        super(Player, self).__init__()
        # 用户ID
        self.userId = userId
        # 玩家坐的座位
        self._seat = None
        # 玩家状态
        self._state = None

    @property
    def state(self):
        return self._state

    @property
    def table(self):
        return self._seat.table if self._seat else None

    @property
    def seat(self):
        return self._seat

    @property
    def ftId(self):
        return self.table.ftId if self.table else None


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
        # 当前牌局开始时间
        self.playTime = None
        # 桌子Location
        self._location = "%s.%s.%s" % (self.gameId, self.roomId, self.tableId)
        # 本桌相关的ftTable
        self._ftTable = None

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
    def location(self):
        return self._location

    @property
    def seatCount(self):
        return len(self._seats)

    @property
    def idleSeatCount(self):
        """
        空闲座位的数量
        """
        return len(self._idleSeats)

    @property
    def ftTable(self):
        return self._ftTable

    @property
    def ftId(self):
        """桌子Id"""
        return self._ftTable.ftId if self._ftTable else None

    def getPlayer(self, userId):
        """获取玩家"""
        for seat in self.seats:
            if seat.player and seat.player.userId == userId:
                return seat.player
        return None

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

    def getUserNum(self):
        """
        获取本桌所有userId
        """
        num = 0
        for seat in self.seats:
            if seat.player and seat.player.userId:
                num += 1
        return num

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
        assert (player._seat is not None and player._seat.table == self)
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


class TableManager(object):

    def __init__(self, room):
        self._room = room
        self._idleTables = []
        self._allTableMap = {}

    @property
    def allTableCount(self):
        """桌子数量"""
        return len(self._allTableMap)

    @property
    def idleTableCount(self):
        """空闲的桌子数量"""
        return len(self._idleTables)

    @property
    def busyTableCount(self):
        """繁忙的桌子数"""
        return max(0, self.allTableCount - self.idleTableCount)

    def addTable(self, table):
        """添加桌子"""
        assert (not table.tableId in self._allTableMap)
        self._idleTables.append(table)
        self._allTableMap[table.tableId] = table

    def borrowTable(self):
        """提取|出借一个桌子"""
        assert (self.idleTableCount > 0)
        table = self._idleTables.pop(0)
        ftlog.info("TableManager.borrowTable", "roomId=", self._room.roomId, "idleTableCount=", self.idleTableCount, "allTableCount=", self.allTableCount, "tableId=", table.tableId)
        return table

    def returnTable(self, table):
        """释放一个桌子"""
        assert (self._allTableMap.get(table.tableId, None) == table)
        assert (not table.getPlayerList())
        self._idleTables.append(table)
        ftlog.info("TableManager.returnTable", "roomId=", self._room.roomId, "idleTableCount=", self.idleTableCount, "allTableCount=", self.allTableCount, "tableId=", table.tableId)

    def findTable(self, roomId, tableId):
        """获取一个桌子实例"""
        return self._allTableMap.get(tableId, None)


class FTConf(object):

    def __init__(self, fee=None, gameTime=120):
        self.fee = fee or []
        self.gameTime = gameTime


class FTTable(object):

    def __init__(self, userId, ftId, ftConf, createTime, table=None):
        # 谁创建的
        self.userId = userId
        # 自建桌ID
        self.ftId = ftId
        # 配置
        self.ftConf = ftConf
        # 绑定的桌子
        self.table = table
        # 是否开始了
        self.started = False
        # 最后的结算信息
        self.results = []
        # 创建时间
        self.createTime = createTime
        # 开始时间
        self.startTime = None
        # 牌桌奖励
        self.fee = ftConf.fee


class TableController(object):

    @classmethod
    def buildFTTableDetails(cls, ftTable):
        """构建桌子的详细信息"""
        ret = {
            "ftId": ftTable.ftId,
            "userId": ftTable.userId,
            "fee": ftTable.fee
        }
        return ret

    def bindTable(self, table):
        """绑定桌子"""
        try:
            code = table_remote.ftBind(table.roomId, table.tableId, self.buildFTTableDetails(table.ftTable))
            if isinstance(code, dict):
                raise TYBizException(code["errorCode"], code["message"])
            return code
        except TYBizException, e:
            raise TYBizException(e.errorCode, e.message)

    def tableEnter(self, table, userId, seatId):
        """
        进入桌子
        """
        try:
            code = table_remote.ftEnter(table.roomId, table.tableId, userId, table.ftTable.ftId, seatId)
            if isinstance(code, dict):
                raise TYBizException(code["errorCode"], code["message"])
            return code
        except TYBizException, e:
            raise TYBizException(e.errorCode, e.message)