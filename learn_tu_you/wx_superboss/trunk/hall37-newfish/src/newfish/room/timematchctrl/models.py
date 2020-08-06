#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/10

import random

from newfish.room.timematchctrl.const import SeatQueuingType, ScoreCalcType
from newfish.room.timematchctrl.utils import Logger



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
