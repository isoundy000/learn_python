#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/8


import random
import time

from copy import deepcopy
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from newfish.entity import config
from newfish.entity.config import FISH_GAMEID
from newfish.entity.fishgroup.fish_group import FishGroup
from newfish.entity.msg import GameMsg


class FishGroupSystem:
    """
    渔场鱼群管理系统
    """
    def __init__(self, table):
        self.table = table
        self._clear()

    def _clear(self):
        """
        重置鱼群数据
        """
        self._globalFishId = 10000      # 累计生成的鱼数量
        self._globalGroupId = 0         # 累计生成的鱼群数量


    def clear(self):
        """
        删除全部鱼群
        """
        self._clear()
        
    def deleteFishGroup(self, group):
        """
        删除单个鱼群
        """
        if ftlog.is_debug():
            ftlog.debug("deleteFishGroup:", group.desc(), self.table.tableId)
        pass
        
    def insertFishGroup(self, groupName, position=None, HP=None, buffer=None, userId=None, score=None,
                        sendUserId=None, gameResolution=None):
        """
        召唤鱼群（与普通鱼群同级，根据特殊规则，单独召唤出现的鱼群）
        :param groupName: 鱼阵文件名称
        :param position: 出现位置
        :param HP: 鱼群中鱼的血量
        :param buffer: 鱼群中鱼的buffer
        :param userId: 归属玩家
        :param score: 指定鱼群中鱼的分数
        :param sendUserId: 指定该鱼群的可见玩家
        :param gameResolution: 召唤该鱼群的玩家的游戏分辨率
        """
        pass
    
    def addNormalFishGroups(self, groupIds):
        """
        普通鱼群，一次生成多个鱼群，一起发给客户端
        """
        pass