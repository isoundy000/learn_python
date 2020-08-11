#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/8/11
# 荣耀任务等级.(荣耀等级)

import json
import freetime.util.log as ftlog
from poker.entity.dao import gamedata, daobase
from newfish.entity import config, util
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData, UserData
from newfish.entity.achievement.fish_achievement_task import TaskState, Task_Error_Code


class AchievementLevel(object):

    def __init__(self, userId):
        self.userId = userId
        self.achLevel = 1
        self.achExp = 0
        self._loadUserData()