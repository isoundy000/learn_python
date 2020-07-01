#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/29

import random

from freetime.util import log as ftlog
from newfish.player.normal_player import FishNormalPlayer


class FishFriendPlayer(FishNormalPlayer):
    """好友的玩家"""
    def triggerCatchFishEvent(self, event):
        """覆盖父类的方法"""
        self.achieveSystem and self.achieveSystem.triggerCatchFishEvent(event)
        self.activitySystem and self.activitySystem.dealCatchFish(event)
        coinAddition = 0
        if 0 < event.gainChip < self.catchBonus:        # 捕获金币加成
            coinAddition = event.gainChip
            self.catchBonus -= coinAddition
        ftlog.debug("triggerCatchFishEvent", event.userId, self.catchBonus, event.gainChip, coinAddition)
        for player in self.table.players:
            if player and player.taskSystemUser:
                player.taskSystemUser.dealCatchEvent(event, coinAddition)

    def triggerComboEvent(self, event):
        """触发连击事件"""
        for player in self.table.players:
            if player and player.taskSystemUser:
                player.taskSystemUser.dealComboEvent(event)

    def triggerUseSkillEvent(self, event):
        """处理使用技能事件"""
        self.activitySystem and self.activitySystem.useSkill(event.skillId)
        for player in self.table.players:
            if player and player.taskSystemUser:
                player.taskSystemUser.dealUserSkillEvent(event)