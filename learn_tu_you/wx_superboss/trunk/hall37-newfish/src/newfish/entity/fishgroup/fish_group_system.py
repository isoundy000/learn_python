#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/8


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
        self._clear()

    def _clear(self):
        """
        重置鱼群数据
        """
        self._globalFishId = 10000      # 累计生成的鱼数量
        self._globalGroupId = 0         # 累计生成的鱼群数量

    def _getNewFishId(self, addCount):
        """
        获得新的鱼ID 开始的鱼的ID
        """
        if self._globalFishId >= 60000 + 10000:
            if ftlog.is_debug():
                ftlog.debug("globalFishId reset to 10000, from:", self._globalFishId)
            self._globalFishId = 10000
        fishId = self._globalFishId + 1
        self._globalFishId += addCount
        return fishId

    def _getNewGroupId(self):
        """
        获得新的鱼群ID
        """
        self._globalGroupId += 1
        return self._globalGroupId

    def _getNextGroupEnterTime(self):
        """
        获得下一个鱼群的入场时间戳
        """
        if len(self.table.normalFishGroups):
            group = self.table.normalFishGroups[-1]
            return group.getNextGroupTime()
        else:
            return time.time() - self.table.startTime + 1

    def _deleteGroup(self, clearGroups):
        """
        清除过期、已死亡的鱼群
        """
        nowTableTime = time.time() - self.table.startTime
        delGroups = []
        if ftlog.is_debug():
            ftlog.debug("_deleteGroup now group num:", len(clearGroups), self.table.tableId, nowTableTime)
        allGroupsLen = len(clearGroups)
        for i, group in enumerate(clearGroups):
            if not group.isAlive(nowTableTime) and allGroupsLen - i >= 10:
                delGroups.append(group)
            else:
                break
        for _, group in enumerate(delGroups):
            self.deleteFishGroup(group)
            clearGroups.remove(group)

    def clear(self):
        """
        删除全部鱼群
        """
        self._clear()
        
    def deleteFishGroup(self, group):
        """
        删除单个鱼群
        """
        if ftlog.is_debug():
            ftlog.debug("deleteFishGroup:", group.desc(), self.table.tableId)
        startFishId = group.startFishId
        fishCount = group.fishCount
        for i in xrange(fishCount):
            _fish = self.table.fishMap.get(startFishId + i)
            if _fish:
                if _fish["alive"]:
                    self.table.refreshFishTypeCount(_fish)
                del self.table.fishMap[startFishId + i]
        
    def insertFishGroup(self, groupName, position=None, HP=None, buffer=None, userId=None, score=None,
                        sendUserId=None, gameResolution=None):
        """
        召唤鱼群（与普通鱼群同级，根据特殊规则，单独召唤出现的鱼群）
        :param groupName: 鱼阵文件名称 tide_44002_1、terror_77228_2、
        :param position: 出现位置
        :param HP: 鱼群中鱼的血量
        :param buffer: 鱼群中鱼的buffer
        :param userId: 归属玩家
        :param score: 指定鱼群中鱼的分数
        :param sendUserId: 指定该鱼群的可见玩家
        :param gameResolution: 召唤该鱼群的玩家的游戏分辨率
        """
        buffer = [buffer] if buffer else []
        allGroups = self.table.runConfig.fishGroups
        if groupName not in allGroups:
            ftlog.error("invalid fish groupType", groupName)
            return None
        groupConf = allGroups[groupName]
        if ftlog.is_debug():
            ftlog.debug("insertFishGroup->groupConf =", groupName, groupConf)
        enterTime = time.time() - self.table.startTime
        startFishId = self._getNewFishId(len(groupConf["fishes"]))
        group = FishGroup(groupConf, enterTime, self._getNewGroupId(), startFishId, position, gameResolution)
        if ftlog.is_debug():
            ftlog.debug("insertFishGroup:", group.desc(), self.table.tableId, enterTime)
        self.table.callFishGroups.append(group)
        self._deleteGroup(self.table.callFishGroups)
        for i in xrange(group.fishCount):
            conf = group.fishes[i]
            fishType = conf.get("fishType")
            fishConf = config.getFishConf(fishType, self.table.typeName, self.table.runConfig.multiple)
            HP = HP if HP else fishConf["HP"]
            self.table.fishMap[startFishId + i] = {
                "group": group,                 # 鱼群对象
                "conf": conf,                   # 鱼的进场、出场、类型
                "HP": HP,                       # 鱼的血
                "buffer": deepcopy(buffer),     # 鱼代buffer
                "multiple": 1,                  # 倍率
                "alive": True,                  # 存活
                "owner": userId,                # 拥有者
                "score": score,                 # 指定鱼群中鱼的分数
                "fishType": fishType,           # 鱼的ID
                "sendUsersList": sendUserId if isinstance(sendUserId, list) else None   # 指定该鱼群的可见玩家
            }
            self.table.ftCount[fishType] = self.table.ftCount.setdefault(fishType, 0) + 1
        self._broadcastAddGroup([group], sendUserId)
        return group
    
    def addNormalFishGroups(self, groupIds):
        """
        普通鱼群，一次生成多个鱼群，一起发给客户端
        """
        fishType = None
        try:
            nowTableTime = time.time() - self.table.startTime
            allGroups = self.table.runConfig.fishGroups
            fixedMultipleFish = config.getFixedMultipleFishConf(self.table.runConfig.fishPool)
            newGroups = []
            for _, groupId in enumerate(groupIds):
                groupConf = allGroups[groupId]
                enterTime = self._getNextGroupEnterTime()
                enterTime = enterTime if enterTime > nowTableTime else nowTableTime + 1
                startFishId = self._getNewFishId(len(groupConf["fishes"]))
                group = FishGroup(groupConf, enterTime, self._getNewGroupId(), startFishId)
                if ftlog.is_debug():
                    ftlog.debug("addNormalFishGroups new group:", group.desc(), self.table.tableId, nowTableTime)
                for i in xrange(group.fishCount):
                    conf = group.fishes[i]
                    fishType = conf.get("fishType")
                    multiple = 1
                    if fixedMultipleFish:  # 随机生成固定倍率鱼（目前只在比赛场使用）
                        if fishType in fixedMultipleFish["range"]:
                            if random.randint(1, 10000) <= fixedMultipleFish["probb"]:              # 固定倍率鱼概率
                                randInt = random.randint(1, 10000)
                                for _, multipleMap in enumerate(fixedMultipleFish["multiples"]):    # 2倍:3000, 3倍:3000, 4倍:2000, 5倍:2000
                                    probb = multipleMap["probb"]
                                    if probb[0] <= randInt <= probb[1]:
                                        multiple = multipleMap["multiple"]
                                        break
                    fishConf = config.getFishConf(fishType, self.table.typeName, self.table.runConfig.multiple)  # 场次倍率
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
                    self.table.ftCount[fishType] = self.table.ftCount.setdefault(fishType, 0) + 1
                if ftlog.is_debug():
                    ftlog.debug("addNormalFishGroups group info :", self.table.tableId, groupId, group.id,
                                self.table.startTime + group.enterTime,
                                self.table.startTime + group.exitTime + group.addTime)
                self.table.normalFishGroups.append(group)                   # 普通鱼群增加一个新的鱼群
                newGroups.append(group)
            self._deleteGroup(self.table.normalFishGroups)                  # 删除普通鱼群集合中 过期的鱼群
            self._broadcastAddGroup(newGroups)
        except:
            ftlog.error("addNormalFishGroups error", fishType)

    def _sendAddGroupMsg(self, groups, userIds):
        """
        发送新增鱼群消息[groupMap]
        """
        msg = MsgPack()
        msg.setCmd("add_group")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("groups", groups)
        GameMsg.sendMsg(msg, userIds)

    def _broadcastAddGroup(self, newGroups, sendUserId=None):
        """
        处理新生成的鱼群详情信息，并广播发送
        newGroups: [group、group1、group2鱼群对象]
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
        self._sendAddGroupMsg(resGroups, allUids)