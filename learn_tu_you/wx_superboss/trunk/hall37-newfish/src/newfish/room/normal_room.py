#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/5
import traceback
from random import choice

from freetime.core.tasklet import FTTasklet
from freetime.core.timer import FTLoopTimer
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.entity.dao import gamedata
from poker.util.keylock import KeyLock
from poker.entity.game.rooms.normal_room import TYNormalRoom
from newfish.entity import util
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData
from newfish.entity.quick_start import FishQuickStart
from newfish.servers.table.rpc import table_remote
from newfish.servers.room.rpc import room_remote



class FishNormalRoom(TYNormalRoom):

    def __init__(self, roomDefine):
        super(FishNormalRoom, self).__init__(roomDefine)
        self._keyLock = KeyLock()
        if gdata.serverType() == gdata.SRV_TYPE_ROOM:       # 当前进程的类型   'GR' # 服务类型: 游戏的房间服务
            self.shadowRoomIdOccupyList = [[shadowRoomId, 0] for shadowRoomId in self.roomDefine.shadowRoomIds]
            self.shadowRoomIdOccupyList.sort(key=lambda x: x[0])
        if gdata.serverType() == gdata.SRV_TYPE_TABLE:  # GT进程
            self._allTableDict = {}
            self._allPlayerDict = {}
            self._usableTableList = []
            FTLoopTimer(self.roomConf.get("occupyIntervalSeconds", 3), -1, self._reportRoomUserOccupy).start()
            from newfish.game import TGFish
            from newfish.entity.event import EnterTableEvent, LeaveTableEvent
            TGFish.getEventBus().subscribe(EnterTableEvent, self._triggerEnterTableEvent)
            TGFish.getEventBus().subscribe(LeaveTableEvent, self._triggerLeaveTableEvent)


    def _reportRoomUserOccupy(self):
        """
        向GR汇报当前GT容量 occupy空间、面积
        """
        if not self.roomConf.get("occupySwitch", 1) or self.runStatus != self.ROOM_STATUS_RUN:
            return
        playerCount = len(self._allPlayerDict)
        tableCount = len(self._allTableDict)
        tableSeatCount = self.tableConf["maxSeatN"]
        totalCount = tableSeatCount * tableCount
        
        
    def _triggerEnterTableEvent(self, event):
        """
        触发进入房间事件
        """
        tableId = event.tableId
        userId = event.userId


    def _triggerLeaveTableEvent(self, event):
        tableId = event.tableId
        userId = event.userId
