# -*- coding=utf-8 -*-
"""
Created by lichen on 2020/3/27.
"""

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.entity.dao import userdata
from newfish.entity import config
from newfish.entity.config import FISH_GAMEID
from newfish.entity.msg import GameMsg
from newfish.table.normal_table import FishNormalTable                      # 普通桌子
from newfish.table.friend_table import FishFriendTable
from newfish.entity.fishgroup.fish_group_system import FishGroupSystem
from newfish.entity.fishgroup.boss_fish_group import BossFishGroup
from newfish.entity.fishgroup.coupon_fish_group import CouponFishGroup
from newfish.entity.fishgroup.chest_fish_group import ChestFishGroup
from newfish.entity.fishgroup.activity_fish_group import ActivityFishGroup
from newfish.entity.fishgroup.share_fish_group import ShareFishGroup
from newfish.entity.fishgroup.rainbow_fish_group import RainbowFishGroup
from newfish.entity.fishgroup.terror_fish_group import TerrorFishGroup
from newfish.entity.fishgroup.autofill_fish_group_m import AutofillFishGroup
from newfish.entity.fishgroup.tt_autofill_fish_group import TTAutofillFishGroup
from newfish.entity.fishgroup import superboss_fish_group
from newfish.player.multiple_player import FishMultiplePlayer


class FishMultipleTable(FishFriendTable):

    def createPlayer(self, table, seatIndex, clientId):
        """
        新创建Player对象
        """
        return FishMultiplePlayer(table, seatIndex, clientId)

    def startFishGroup(self):
        """
        启动鱼阵
        """
        # if self.bigRoomId != 44412:
        #     super(FishNormalTable, self).startFishGroup()
        # else:
        self.fishGroupSystem = FishGroupSystem(self)
        # terror鱼初始化
        if self.runConfig.allTerrorGroupIds and not self.terrorFishGroup:
            self.terrorFishGroup = TerrorFishGroup(self)
        # if self.bigRoomId == 44412:
        # autofill鱼初始化
        if self.runConfig.allAutofillGroupIds and not self.autofillFishGroup:
            self.autofillFishGroup = AutofillFishGroup(self)
        # superboss鱼初始化
        if self.runConfig.allSuperBossGroupIds and not self.superBossFishGroup:
            self.superBossFishGroup = superboss_fish_group.createSuperBoss(self)

    def _afterSendTableInfo(self, userId):
        """
        发送桌子信息之后
        """
        super(FishMultipleTable, self)._afterSendTableInfo(userId)
        self.superBossFishGroup and self.superBossFishGroup.dealEnterTable(userId)