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

    def _loadUserData(self):
        """加载用户数据"""
        receiveLevelState = daobase.executeUserCmd(self.userId, "HGET", self._getTaskKey(), self._levelKey())
        achLevel, achExp = gamedata.getGameAttrs(self.userId, FISH_GAMEID, [GameData.achievementLevel, GameData.achievementExp])
        self.receivedLevel = json.loads(receiveLevelState) if receiveLevelState else []         # [2,3,4,5,6,...]
        self.achExp = achExp or self.achExp
        self.achLevel = achLevel or self.achLevel

    def getAchieveLevel(self):
        """
        获取荣耀等级
        """
        return self.achLevel

    def getAchieveExp(self):
        """
        获取荣耀经验值
        """
        return self.achExp

    def getAchieveTotalExp(self):
        """
        获取当前升级经验值
        """
        return config.getAchievementLevelConfig(self.achLevel).get("exp", -1)

    def addAchievementExp(self, exp):
        """
        增加荣耀经验值
        """
        curExp = self.achExp + exp
        levelConf = config.getAchievementLevelConfig(self.achLevel)
        isLevelUp = False
        while levelConf and curExp >= levelConf["exp"] and levelConf["exp"] != -1:
            self.achLevel += 1
            isLevelUp = True
            # curExp -= levelConf["exp"]
            levelConf = config.getAchievementLevelConfig(self.achLevel)
        self.achExp = curExp
        gamedata.setGameAttrs(self.userId, FISH_GAMEID, [GameData.achievementLevel, GameData.achievementExp], [self.achLevel, self.achExp])
        if isLevelUp:
            from newfish.game import TGFish
            from newfish.entity.event import AchievementLevelUpEvent
            event = AchievementLevelUpEvent(self.userId, FISH_GAMEID, self.achLevel)
            TGFish.getEventBus().publishEvent(event)

    def _getTaskKey(self):
        """荣耀数据的key"""
        return UserData.achievement % (FISH_GAMEID, self.userId)

    def _levelKey(self):
        """
        已领取奖励的荣耀等级
        """
        return "levelReceived"

    def getCurAchievementLevelReward(self):
        """获取当前成就任务的等级和奖励"""
        result = {}
        achKeys = config.getAchievementConf().get("level", {}).keys()
        achKeys = [int(x) for x in achKeys]
        if not self.receivedLevel:
            levelConf = config.getAchievementLevelConfig(2)
            result["reward"] = levelConf.get("reward")
            result["level"] = 2
        else:
            achKeys.sort()
            del achKeys[0]
            difLevel = set(achKeys) - set(self.receivedLevel)
            if not difLevel:
                curLevel = max(achKeys)
            else:
                curLevel = min(difLevel)
            levelConf = config.getAchievementLevelConfig(curLevel)
            if not levelConf:                                       # 取到最大值
                levelConf = config.getAchievementLevelConfig(curLevel - 1)
            result["reward"] = levelConf.get("reward")
            result["level"] = levelConf["level"]

        if result["level"] in self.receivedLevel:
            result["state"] = TaskState.Received
        elif self.achLevel >= result["level"]:
            result["state"] = TaskState.Complete
        else:
            result["state"] = TaskState.Normal
        result["maxLevel"] = max(achKeys)
        return result

    def receiveLevelReward(self, level):
        """
        领取荣耀等级奖励
        """
        if int(level) in self.receivedLevel:
            return Task_Error_Code.RECEIVE, []
        if self.achLevel < level:
            return Task_Error_Code.NOTCOMPLETE, []
        levelConf = config.getAchievementLevelConfig(level)
        if not levelConf:
            return 99, []
        rewards = [levelConf.get("reward")] if levelConf.get("reward") else []
        code = util.addRewards(self.userId, rewards, "BI_NFISH_ACHIEVEMENT_REWARDS", int(level))
        self.receivedLevel.append(level)
        daobase.executeUserCmd(self.userId, "HSET", self._getTaskKey(), self._levelKey(), json.dumps(self.receivedLevel))
        return code, rewards

    def getAllLevelInfos(self):
        """
        获取荣耀等级数据
        """
        levelConfs = config.getAchievementConf().get("level")
        levelInfos = []
        for level, conf in levelConfs.iteritems():
            levelInfo = {}
            level = int(level)
            if not conf.get("reward"):
                continue
            levelInfo["reward"] = conf["reward"]
            if level in self.receivedLevel:
                levelInfo["state"] = TaskState.Received
            elif self.achLevel >= int(level):
                levelInfo["state"] = TaskState.Complete
            else:
                levelInfo["state"] = TaskState.Normal
            levelInfo["level"] = level
            levelInfos.append(levelInfo)
        num = int(self.achLevel) / 5 * 5 + 10
        levelInfos.sort(key=lambda info: int(info["level"]))
        levelInfos = levelInfos[0: (num - 1)]
        return levelInfos