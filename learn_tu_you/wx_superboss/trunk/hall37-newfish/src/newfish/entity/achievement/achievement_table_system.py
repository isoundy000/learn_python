# -*- coding=utf-8 -*-
"""
Created by hhx on 17/10/10.
"""

import freetime.util.log as ftlog
from newfish.entity import config,  module_tip
from newfish.entity.achievement.fish_achievement_task import FishAchievementTask
from newfish.entity.achievement.fish_achievement_task import AchieveType


class AchievementTableSystem(object):
    """成就系统"""
    def __init__(self, table, player):
        self.table = table
        self.player = player
        self.achieveTasks = []
        self.holdAssetTasks = []

    def _clearTimer(self):
        pass

    # 初始化用户成就任务
    def _initPlayerAchieveTasks(self, userId):
        taskObjects = []
        if self.player.level < config.getCommonValueByKey("achievementOpenLevel"):
            return taskObjects
        # 渔场内支持的任务类型，数据会及时刷新。
        tableTypes = [AchieveType.CatchFishNum, AchieveType.CatchBetFishNum, AchieveType.CatchBossNum]
        achConfigs = config.getAchievementConf().get("tasks")
        for honorId, tasksConf in achConfigs.iteritems():
            for _, conf in tasksConf.iteritems():
                if conf["type"] in tableTypes:
                    taskClass = FishAchievementTask(userId, conf)
                    taskObjects.append(taskClass)
        return taskObjects

    def triggerCatchFishEvent(self, event):
        """捕获鱼"""
        if self.table.typeName not in config.NORMAL_ROOM_TYPE:
            return
        if not self.player or self.player.userId <= 0:
            return
        if self.player.level < config.getCommonValueByKey("achievementOpenLevel"):
            return
        if not self.achieveTasks:
            self.achieveTasks = self._initPlayerAchieveTasks(self.player.userId)
        if hasattr(event, "fpMultiple"):
            fpMultiple = event.fpMultiple
        else:
            fpMultiple = self.table.runConfig.multiple
        fishIds = event.fishTypes               # 鱼种类
        fTypes = []
        betFishMap = {}                         # 计算倍率鱼 个数
        bossNum = 0                             # boss个数
        for fishType in fishIds:
            fishConf = config.getFishConf(fishType, self.table.typeName, self.player.fpMultiple)
            if fishConf["type"] in config.BOSS_FISH_TYPE:
                bossNum += 1
            fTypes.append(fishConf["type"])

        for gainMap in event.gain:
            fishConf = config.getFishConf(gainMap["fishType"], self.table.typeName, self.player.fpMultiple)
            itemId = gainMap["itemId"]
            itemCount = gainMap["count"]
            if fishConf["type"] not in config.MULTIPLE_FISH_TYPE:
                continue
            if itemId == config.CHIP_KINDID:    # 金币
                bet = itemCount / fishConf["score"] / fpMultiple
                if str(bet) not in betFishMap:
                    betFishMap[str(bet)] = 1
                else:
                    betFishMap[str(bet)] += 1

        tipHonorIds = []
        for taskClass in self.achieveTasks:
            hasComplete = False
            taskConf = taskClass.getTaskConf()
            if taskConf["type"] == AchieveType.CatchFishNum:                        # 捕获鱼多少条
                count = len(fishIds)
                fishTypes = taskConf["target"].get("fishType")
                if fishTypes:
                    count = sum([fTypes.count(type_) for type_ in fishTypes])
                hasComplete = taskClass.addProgress(count, inTable=True)
            elif taskConf["type"] == AchieveType.CatchBetFishNum:                   # 捕获倍率鱼总数
                betNum = 0
                targetBet = taskConf["target"]["condition"]
                for bet in betFishMap:
                    if int(bet) >= targetBet:
                        betNum += betFishMap[bet]
                hasComplete = taskClass.addProgress(betNum, inTable=True)
            elif taskConf["type"] == AchieveType.CatchBossNum and (taskConf["target"].get("condition", self.table.runConfig.multiple) == self.table.runConfig.multiple):  # 捕获boss个数
                hasComplete = taskClass.addProgress(bossNum, inTable=True)
            # 添加小红点
            if hasComplete and taskClass.getHonorId() not in tipHonorIds:
                tipHonorIds.append(taskClass.getHonorId())
        if tipHonorIds:
            module_tip.addModuleTipEvent(self.player.userId, "achievement", tipHonorIds)

    def updateStateAndSave(self):
        """更新任务状态并且保存到数据库"""
        if self.table.typeName in config.NORMAL_ROOM_TYPE and self.player and self.player.userId:
            if self.achieveTasks:
                for taskClass in self.achieveTasks:
                    taskClass.updateStateAndSave()

    def refreshAchievementTask(self):
        """刷新成就任务"""
        self.achieveTasks = self._initPlayerAchieveTasks(self.player.userId)

    def dealLeaveTable(self):
        """
        处理离开桌子
        """
        self.updateStateAndSave()
        self._clearTimer()