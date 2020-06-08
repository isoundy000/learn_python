#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6
'''普通房间类
'''
from poker.entity.game.game import TYGame
from random import choice
from freetime.core.tasklet import FTTasklet
import freetime.util.log as ftlog
from freetime.util.log import getMethodName
from poker.entity.configure import gdata
from poker.entity.game.rooms.room import TYRoom
from poker.entity.dao import daobase
from poker.entity.dao.lua_scripts import room_scripts
from poker.util import strutil



class TYNormalRoom(TYRoom):
    '''普通房间类'''

    def __init__(self, roomDefine):
        super(TYNormalRoom, self).__init__(roomDefine)

        # GT重启创建Room对象时清空牌桌评分历史数据
        daobase.executeTableCmd(self.roomId, 0, "DEL", self.getTableScoresKey(self.roomId))

    def getTableScoresKey(self, shadowRoomId):
        """获取桌子的评分"""
        return "ts:" + str(shadowRoomId)