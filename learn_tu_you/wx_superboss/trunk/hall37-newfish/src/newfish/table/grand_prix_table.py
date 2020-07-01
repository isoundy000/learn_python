#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/29
"""
大奖赛table逻辑
"""

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.entity.dao import userdata
from newfish.entity import config
from newfish.entity.config import FISH_GAMEID
from newfish.entity.msg import GameMsg
from newfish.entity.fishgroup.fish_group_system import FishGroupSystem
from newfish.entity.fishgroup.normal_fish_group import NormalFishGroup
from newfish.table.friend_table import FishFriendTable
from newfish.entity.fishgroup.boss_fish_group import BossFishGroup
from newfish.entity.fishgroup.terror_fish_group import TerrorFishGroup
from newfish.entity.fishgroup.autofill_fish_group import AutofillFishGroup
from newfish.entity.fishgroup.grandprix_fish_group import GrandPrixFishGroup
from newfish.player.grand_prix_player import FishGrandPrixPlayer


class FishGrandPrixTable(FishFriendTable):

    def startFishGroup(self):
        """
        启动鱼阵
        """
        self.fishGroupSystem = FishGroupSystem(self)
        if self.runConfig.allNormalGroupIds:
            self.normalFishGroup = NormalFishGroup(self)
        # Boss鱼初始化
        if self.runConfig.allBossGroupIds:
            self.bossFishGroup = BossFishGroup(self)
        # terror鱼初始化
        if self.runConfig.allTerrorGroupIds:
            self.terrorFishGroup = TerrorFishGroup(self)
        # autofill鱼初始化
        if self.runConfig.allAutofillGroupIds:
            self.autofillFishGroup = AutofillFishGroup(self)
        # grandprix鱼初始化
        if self.runConfig.allGrandPrixGroupIds:
            self.grandPrixFishGroup = GrandPrixFishGroup(self)
        ftlog.debug("FishGrandPrixTable, startFishGroups, ", self.runConfig.allNormalGroupIds, self.runConfig.allGrandPrixGroupIds)

    def createPlayer(self, table, seatIndex, clientId):
        """
        新创建Player对象
        """
        return


    def _startGrandPrix(self, msg, userId, seatId):
        """
        开始大奖赛或是直接进入渔场
        """
        signUp = msg.getParam("signUp", 0)
        player = self.getPlayer(userId)
        if player:
            player.startGrandPrix(signUp)