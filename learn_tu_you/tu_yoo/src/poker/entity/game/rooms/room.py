#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6
"""
房间基类
"""
from freetime.entity.msg import MsgPack
from freetime.util.log import getMethodName, catchedmethod
import freetime.util.log as ftlog


from poker.entity.configure import gdata, pokerconf
from poker.entity.dao import sessiondata, onlinedata, userchip
from poker.entity.game import game
from poker.entity.game.plugin import TYPluginCenter, TYPluginUtils
from poker.entity.game.tables.table_player import TYPlayer
from poker.protocol import router


class TYRoom(object):
    '''游戏房间基类

    Attributes:
        roomDefine： 房间配置信息
        maptable:    房间牌字典
    '''
    ENTER_ROOM_REASON_INNER_ERROR = 2           # 服务器内部错误
    ROOM_STATUS_RUN = game.GAME_STATUS_RUN      # 房间初始化后，处于正常服务状态

    def __init__(self, roomDefine):
        '''
        Args:
            roomDefine:
                RoomDefine.bigRoomId     int 当前房间的大房间ID, 即为game/<gameId>/room/0.json中的键
                RoomDefine.parentId      int 父级房间ID, 当前为管理房间时, 必定为0 (管理房间, 可以理解为玩家队列控制器)
                RoomDefine.roomId        int 当前房间ID
                RoomDefine.gameId        int 游戏ID
                RoomDefine.configId      int 配置分类ID
                RoomDefine.controlId     int 房间控制ID
                RoomDefine.shadowId      int 影子ID
                RoomDefine.tableCount    int 房间中桌子的数量
                RoomDefine.shadowRoomIds tuple 当房间为管理房间时, 下属的桌子实例房间的ID列表
                RoomDefine.configure     dict 房间的配置内容, 即为game/<gameId>/room/0.json中的值
        '''
        if ftlog.is_debug():
            ftlog.debug("<<", "|roomDefine", str(roomDefine), caller=self)
        self.__define = roomDefine
        self.maptable = {}
        self.runStatus = TYRoom.ROOM_STATUS_RUN

    @property  # read only attributes
    def roomDefine(self):
        return self.__define

    @property
    def bigRoomId(self):
        return self.__define.bigRoomId

    @property
    def ctrlRoomId(self):
        if self.__define.parentId == 0:
            return self.__define.roomId
        else:
            return self.__define.parentId

    @property
    def roomId(self):
        return self.__define.roomId

    @property
    def gameId(self):
        return self.__define.gameId

    @property
    def tableConf(self):
        return self.__define.configure['tableConf']

    @property
    def roomConf(self):
        return self.__define.configure

    @property
    def matchConf(self):
        return self.__define.configure['matchConf']

    @property
    def hasRobot(self):
        return self.__define.configure['hasrobot', 0]

    @property
    def shelterShadowRoomIds(self):
        return self.__define.configure.get('shelterShadowRoomIds', [])      # 保护的房间

    @property
    def openShadowRoomIds(self):
        openIds = []
        for rId in self.roomDefine.shadowRoomIds:
            if rId not in self.shelterShadowRoomIds:
                openIds.append(rId)
        return openIds