#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/14
from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from freetime.core.timer import FTLoopTimer
from poker.protocol import router
from poker.entity.dao import gamedata
from hall.entity import hallvip
from newfish.player.player_base import FishPlayer
from newfish.entity import config, util
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData
from newfish.entity.task.task_system_user import TaskSystemUser
from newfish.entity.skill import skill_system
from newfish.entity.event import UseCoolDownEvent
from newfish.entity.quest.main_quest import MainQuest


class FishNormalPlayer(FishPlayer):

    """普通渔场玩家"""
    def __init__(self, table, seatIndex, clientId=None):
        super(FishNormalPlayer, self).__init__(table, seatIndex, clientId)
        if "user" in table.runConfig.taskSystemType:
            self.taskSystemUser = TaskSystemUser(self.table, self)
        self.mainQuestSystem = MainQuest(self)
        self.refreshHoldCoin()

    def refreshSkillCD(self):
        """
        刷新技能CD时间
        :return:
        """
        if util.balanceItem(self.userId, config.SKILLCD_KINDID) > 0:
            pass