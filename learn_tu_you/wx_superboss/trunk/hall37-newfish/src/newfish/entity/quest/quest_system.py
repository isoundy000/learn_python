#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/8

import time

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.events.tyevent import EventUserLogin
from newfish.entity import weakdata
from newfish.entity.config import FISH_GAMEID
from newfish.entity.quest import daily_quest, main_quest
from newfish.entity.event import CatchEvent, GameTimeEvent, LevelUpEvent, \
    OpenChestEvent, BuyChestEvent, UseSkillEvent, UseSmiliesEvent, \
    WinCmpttTaskEvent, WinNcmpttTaskEvent, WinBonusTaskEvent, EnterTableEvent, \
    StoreBuyEvent, TableTaskEndEvent, ShareFinishEvent, CheckinEvent, UseCoolDownEvent, \
    FireEvent, ItemChangeEvent, GainChestEvent, RobberyBulletProfitEvent, \
    SkillLevelUpEvent, AchievementLevelUpEvent





_inited = False


def initialize():
    ftlog.info("newfish quest_system initialize begin")
    global _inited
    if not _inited:
        _inited = True
        # 每日任务系统初始化
        daily_quest.initialize()
        from newfish.game import TGFish
