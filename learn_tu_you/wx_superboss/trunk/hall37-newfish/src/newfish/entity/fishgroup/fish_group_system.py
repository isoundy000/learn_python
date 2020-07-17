# -*- coding=utf-8 -*-
"""
Created by lichen on 2017/4/12.
"""

import random
import time

from copy import deepcopy
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from newfish.entity import config
from newfish.entity.config import FISH_GAMEID
from newfish.entity.fishgroup.fish_group import FishGroup
from newfish.entity.msg import GameMsg


class FishGroupSystem(object):
    """
    渔场鱼群管理系统
    """
    def __init__(self, table):
        self.table = table
        # 唯一标识数量上限（单个鱼群最大存活时间不超过10分钟且平均每秒新增鱼数量小于100）
        self._maxLimitId = 60000
        self._clear()

    def _clear(self):
        """
        重置鱼群数据
        """
        # 在所有鱼群中每条鱼的唯一标识
        self._globalFishId = 10000          # 添加鱼生成的条数
        # 在所有鱼群中每个鱼群的唯一标识
        self._globalGroupId = 0

    def _getNewFishId(self, addCount):
        """
        获得新的鱼ID
        """
        if self._globalFishId >= self._maxLimitId + 10000:
            self._globalFishId = 10000
        fishId = self._globalFishId + 1
        self._globalFishId += addCount
        return fishId

    def _getNewGroupId(self):
        """
        获得新的鱼群ID
        """
        if self._globalGroupId >= self._maxLimitId:
            self._globalGroupId = 0
        self._globalGroupId += 1
        return self._globalGroupId

    def clear(self):
        """
        删除全部鱼群
        """
        for group in self.table.normalFishGroups.itervalues():
            group.clear()
        for group in self.table.callFishGroups.itervalues():
            group.clear()
        self.table.normalFishGroups.clear()
        self.table.callFishGroups.clear()
        self._clear()

    def deleteFishGroups(self, clearGroups, clearNum):
        """
        清除过期或已死亡的多个鱼群
        @param clearGroups: 待处理鱼群
        @param clearNum: 清除数量
        """
        nowTableTime = time.time() - self.table.startTime
        allGroupsLen = len(clearGroups)
        if ftlog.is_debug():
            ftlog.debug("deleteFishGroups:", self.table.tableId, nowTableTime, allGroupsLen)
        i = 0
        for serverGroupId in clearGroups.keys():
            group = clearGroups[serverGroupId]
            if not group.isAlive(nowTableTime) and allGroupsLen - i >= clearNum:
                if not group.isCleared():
                    self.deleteFishGroup(group, clearGroups)
            else:
                break
            i += 1

    def deleteFishGroup(self, group, clearGroups=None):
        """
        删除单个鱼群
        """
        if ftlog.is_debug():
            ftlog.debug("deleteFishGroup:", self.table.tableId, group.desc())
        startFishId = group.startFishId
        fishCount = group.fishCount
        serverGroupId = group.serverGroupId
        group.clear()
        for i in xrange(fishCount):
            _fish = self.table.fishMap.get(startFishId + i)
            if _fish:
                if _fish["alive"]:
                    self.table.refreshFishTypeCount(_fish)
                del self.table.fishMap[startFishId + i]
        if clearGroups:
            del clearGroups[serverGroupId]
        elif serverGroupId in self.table.callFishGroups:
            del self.table.callFishGroups[serverGroupId]
        elif serverGroupId in self.table.normalFishGroups:
            del self.table.normalFishGroups[serverGroupId]

    def insertFishGroup(self, groupNames, position=None, HP=None, buffer=None, userId=None, score=None,
                        sendUserId=None, gameResolution=None):
        """
        召唤鱼群（调用后立即出现的鱼群）
        :param groupNames: 鱼阵文件名称 tide_44002_1、terror_77228_2、
        :param position: 出现位置
        :param HP: 鱼群中鱼的血量
        :param buffer: 鱼群中鱼的buffer
        :param userId: 归属玩家
        :param score: 指定鱼群中鱼的分数
        :param sendUserId: 指定该鱼群的可见玩家
        :param gameResolution: 召唤该鱼群的玩家的游戏分辨率
        :param isBroadcast: 是否需要广播通知
        """
        buffer = [buffer] if buffer else []
        groupNames = groupNames if isinstance(groupNames, list) else [groupNames]
        allGroups = self.table.runConfig.fishGroups
        newGroups = []
        for _, groupName in enumerate(groupNames):
            if groupName not in allGroups:
                ftlog.error("invalid fish groupType", groupName)
                return None
            groupConf = allGroups[groupName]
            if ftlog.is_debug():
                ftlog.debug("insertFishGroup->groupConf =", groupName, groupConf)
            enterTime = time.time() - self.table.startTime
            startFishId = self._getNewFishId(len(groupConf["fishes"]))
            group = FishGroup(groupConf, enterTime, self._getNewGroupId(), startFishId, position, gameResolution,
                              deadCallback=self.deleteFishGroup)
            if ftlog.is_debug():
                ftlog.debug("insertFishGroup:", group.desc(), self.table.tableId, enterTime)
            for i in xrange(group.fishCount):
                conf = group.fishes[i]
                fishType = conf.get("fishType")
                fishConf = config.getFishConf(fishType, self.table.typeName, self.table.runConfig.multiple)
                HP = HP if HP else fishConf["HP"]
                self.table.fishMap[startFishId + i] = {
                    "group": group,
                    "conf": conf,
                    "HP": HP,
                    "buffer": deepcopy(buffer),
                    "multiple": 1,
                    "alive": True,
                    "owner": userId,
                    "score": score,
                    "fishType": fishType,
                    "sendUsersList": sendUserId if isinstance(sendUserId, list) else None
                }
                self.table.fishCountMap[fishType] = self.table.fishCountMap.setdefault(fishType, 0) + 1
            self.table.callFishGroups[group.serverGroupId] = group
            # ftlog.debug("insertFishGroup", self.table.tableId, group.serverGroupId, self.table.callFishGroups.keys())
            newGroups.append(group)
        self.broadcastAddGroup(newGroups, sendUserId)
        return newGroups[0] if len(newGroups) == 1 else newGroups

    def addNormalFishGroups(self, groupNames):
        """
        普通鱼群（单个鱼群时长一般为1分钟左右，鱼群中含有多条鱼且可以延迟出现）
        """
        fishType = None
        try:
            nowTableTime = time.time() - self.table.startTime
            allGroups = self.table.runConfig.fishGroups
            fixedMultipleFish = config.getFixedMultipleFishConf(self.table.runConfig.fishPool)
            newGroups = []
            for _, groupName in enumerate(groupNames):
                groupConf = allGroups[groupName]
                enterTime = self.table.getNextGroupEnterTime()
                enterTime = enterTime if enterTime > nowTableTime else nowTableTime + 1
                startFishId = self._getNewFishId(len(groupConf["fishes"]))
                group = FishGroup(groupConf, enterTime, self._getNewGroupId(), startFishId)
                if ftlog.is_debug():
                    ftlog.debug("addNormalFishGroups new group:", group.desc(), self.table.tableId, nowTableTime)
                for i in xrange(group.fishCount):
                    conf = group.fishes[i]
                    fishType = conf.get("fishType")
                    multiple = 1
                    if fixedMultipleFish:   # 随机生成固定倍率鱼（目前只在比赛场使用）
                        if fishType in fixedMultipleFish["range"]:
                            if random.randint(1, 10000) <= fixedMultipleFish["probb"]:
                                randInt = random.randint(1, 10000)
                                for _, multipleMap in enumerate(fixedMultipleFish["multiples"]):
                                    probb = multipleMap["probb"]
                                    if probb[0] <= randInt <= probb[1]:
                                        multiple = multipleMap["multiple"]
                                        break
                    fishConf = config.getFishConf(fishType, self.table.typeName, self.table.runConfig.multiple)
                    self.table.fishMap[startFishId + i] = {
                        "group": group,
                        "conf": conf,
                        "HP": fishConf["HP"],
                        "buffer": [],
                        "multiple": multiple,
                        "alive": True,
                        "owner": None,
                        "score": None,
                        "fishType": fishType
                    }
                    self.table.fishCountMap[fishType] = self.table.fishCountMap.setdefault(fishType, 0) + 1
                self.table.normalFishGroups[group.serverGroupId] = group
                newGroups.append(group)
                if ftlog.is_debug():
                    ftlog.debug("addNormalFishGroups group info:",
                                self.table.tableId, groupName, group.serverGroupId,
                                self.table.startTime + group.enterTime,
                                self.table.startTime + group.exitTime + group.addTime)
            self.deleteFishGroups(self.table.normalFishGroups, len(newGroups))
            self.broadcastAddGroup(newGroups)
        except:
            ftlog.error("addNormalFishGroups error", fishType)

    def sendAddGroupMsg(self, groups, userIds):
        """
        发送新增鱼群消息
        """
        msg = MsgPack()
        msg.setCmd("add_group")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("groups", groups)
        GameMsg.sendMsg(msg, userIds)

    def broadcastAddGroup(self, newGroups, sendUserId=None):
        """
        处理新生成的鱼群详情信息，并广播发送
        """
        allUids = self.table.getBroadcastUids()
        if sendUserId:
            if isinstance(sendUserId, list):
                allUids = sendUserId
            else:
                allUids = [sendUserId]
        resGroups = []
        for _, group in enumerate(newGroups):
            groupMap = {}
            groupMap["grpId"] = group.id                    # call_11002_lv13
            groupMap["enT"] = round(group.enterTime, 2)
            groupMap["fishesStartId"] = group.startFishId
            groupMap["position"] = group.position
            groupMap["gameResolution"] = group.gameResolution
            HPFish = {}                                     # 带血的鱼
            bufferFish = {}                                 # 带buffer的鱼
            multipleFish = {}                               # 倍率鱼
            for fId in xrange(group.startFishId, group.startFishId + group.fishCount):
                if self.table.fishMap[fId]["HP"] > 0:
                    HPFish[fId] = self.table.fishMap[fId]["HP"]
                if self.table.fishMap[fId]["buffer"]:
                    bufferFish[fId] = self.table.fishMap[fId]["buffer"]
                if self.table.fishMap[fId]["multiple"] > 1:
                    multipleFish[fId] = self.table.fishMap[fId]["multiple"]
            if HPFish:
                groupMap["HP"] = HPFish
            if bufferFish:
                groupMap["buffer"] = bufferFish
            if multipleFish:
                groupMap["multiple"] = multipleFish
            resGroups.append(groupMap)
        self.sendAddGroupMsg(resGroups, allUids)