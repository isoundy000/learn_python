#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/17
from freetime.util import log as ftlog
from poker.entity.dao import gamedata
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData
from newfish.player.multiple_player import FishMultiplePlayer


class FishNewbiePlayer(FishMultiplePlayer):

    def __init__(self, table, seatIndex, clientId):
        super(FishMultiplePlayer, self).__init__(table, seatIndex, clientId)
        self.bossAppearCount = 0

    def catchBudget(self, gainChip, gainCoupon, items, nowExp=0, wpId=0):
        super(FishNewbiePlayer, self).catchBudget(gainChip, gainCoupon, items, nowExp=0, wpId=0)    # 捕获添加奖励
        if gainCoupon > 0:
            gamedata.incrGameAttr(self.userId, FISH_GAMEID, GameData.catchCouponFishCount, 1)

    def triggerCatchFishEvent(self, event):
        """捕鱼事件"""
        self.achieveSystem and self.achieveSystem.triggerCatchFishEvent(event)
        self.activitySystem and self.activitySystem.dealCatchFish(event)
        coinAddition = 0
        if 0 <= event.gainChip < self.catchBonus:
            coinAddition = event.gainChip
            self.catchBonus -= coinAddition
        ftlog.debug("triggerCatchFishEvent", event.userId, self.catchBonus, event.gainChip, coinAddition)
        self.taskSystemUser.dealCatchEvent(event, coinAddition)