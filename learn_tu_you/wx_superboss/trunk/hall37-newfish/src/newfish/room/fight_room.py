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
        except Exception, e:
            if isCollectFee:
                self._returnFee(userId, ftId, ftConf)



    def _initGR(self):
        """初始化房间"""
        # 获取所有的bigRoomId
        self._ftMap = OrderedDict()
        self._tableCtrl = TableController()

    def _genFTId(self):
        """"""
        for _ in xrange(10):
            ftId = genFTId()
            if not self.findFT(ftId):               # 找不到重复的房间号就是新房间
                return ftId
        return None


def ftExists(ftId):
    pass


def ftFind(ftId):
    pass


def ftBindRoomId(ftId, roomId):
    pass


def genFTId():
    """生成房间Id"""
    for _ in xrange(10):
        ftId = hall_friend_table.createFriendTable(FISH_GAMEID)
        if ftId:
            return ftId
    return None


def releaseFTId(ftId):
    pass


def collectCtrlRoomIds():
    pass


def roomIdForFTId(ftId):
    pass


def createFT(userId, fee):
    pass


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



class TableManager(object):

    def __init__(self, room):
        self._room = room
        self._idleTables = []
        self._allTableMap = {}

    pass



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