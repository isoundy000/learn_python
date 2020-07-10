# -*- coding=utf-8 -*-
"""
Created by lichen on 16/12/13.
"""

import traceback
from datetime import datetime

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.entity.dao import userdata
from newfish.entity import util
from newfish.entity.config import FISH_GAMEID
from newfish.entity.msg import GameMsg
from newfish.table.table_base import FishTable
from newfish.entity.fishgroup.boss_fish_group import BossFishGroup
from newfish.entity.fishgroup.coupon_fish_group import CouponFishGroup
from newfish.entity.fishgroup.chest_fish_group import ChestFishGroup
from newfish.entity.fishgroup.activity_fish_group import ActivityFishGroup
from newfish.entity.fishgroup.terror_fish_group import TerrorFishGroup
from newfish.entity.fishgroup.autofill_fish_group import AutofillFishGroup
from newfish.entity.fishgroup.tt_autofill_fish_group import TTAutofillFishGroup
from newfish.player.normal_player import FishNormalPlayer


class FishNormalTable(FishTable):
    """普通桌子"""
    def _doTableCall(self, msg, userId, seatId, action, clientId):
        try:
            if not super(FishNormalTable, self)._doTableCall(msg, userId, seatId, action, clientId):
                if seatId == 0 and action not in ["task_ready",
                                                  "task_start",
                                                  "task_end"]:
                    ftlog.warn("invalid seatId")
                    return
                func = self.systemTableActionMap.get(action) if hasattr(self, "systemTableActionMap") else None
                if func:
                    func(msg, userId, seatId)
                else:
                    ftlog.warn("not reconized action:", action)
        except:
            ftlog.error("_doTableCall error clear table", userId, msg, traceback.format_exc())
            self._clearTable()

    def startFishGroup(self):
        """
        启动鱼阵
        """
        super(FishNormalTable, self).startFishGroup()
        # Boss鱼初始化
        if self.runConfig.allBossGroupIds:
            self.bossFishGroup = BossFishGroup(self)
        # 奖券鱼初始化
        if self.runConfig.allCouponGroupIds:
            self.couponFishGroup = CouponFishGroup(self)
        # 金币宝箱鱼初始化
        if self.runConfig.allChestGroupIds:
            self.chestFishGroup = ChestFishGroup(self)
        # 活动鱼初始化
        if self.runConfig.allActivityGroupIds:
            self.activityFishGroup = ActivityFishGroup(self)
        # terror鱼初始化
        if self.runConfig.allTerrorGroupIds:
            self.terrorFishGroup = TerrorFishGroup(self)
        # autofill鱼初始化
        if self.runConfig.allAutofillGroupIds:
            self.autofillFishGroup = AutofillFishGroup(self)
        # ttautofill鱼初始化
        if self.runConfig.allAutofillGroupIds:
            self.ttAutofillFishGroup = TTAutofillFishGroup(self)

    def createPlayer(self, table, seatIndex, clientId):
        """
        新创建Player对象
        """
        return FishNormalPlayer(table, seatIndex, clientId)