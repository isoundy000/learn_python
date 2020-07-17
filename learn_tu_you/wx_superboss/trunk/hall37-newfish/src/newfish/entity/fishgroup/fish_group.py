# -*- coding=utf-8 -*-
"""
Created by lichen on 16/12/13.
"""

import time

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer


class FishGroup(object):
    """
    鱼群对象
    """
    def __init__(self, conf, enterTime, serverGroupId, startFishId, position=None, gameResolution=None, deadCallback=None):
        """
        :param conf: 鱼阵配置文件 group_44201_1: conf = {id: "group_44201_1", fishes: [{"fishType": 10002(fishid), "enterTime": 2:02, "exitTime": 10.03}], "totalTime": 10;03}
        :param enterTime: 该鱼群入场时间戳 10s
        :param serverGroupId: 鱼群ID 1、2、3、4、...
        :param startFishId: 该鱼群第一条鱼的鱼ID、10001、10002、| 10400
        :param position: 指定出现位置
        :param gameResolution: 召唤该鱼群的玩家的游戏分辨率
        """
        self.position = position if position else [0, 0]
        self.gameResolution = gameResolution if gameResolution else []
        self.enterTime = enterTime
        self.id = conf.get("id")                # 鱼群id
        groupType = self.id.split("_")[0]
        if self.id.startswith("call_"):         # call_11002_lv13
            groupType = self.id.split("_")[1]
        self.serverGroupId = serverGroupId      # 鱼群Id
        self.type = groupType
        self.totalTime = conf.get("totalTime")
        self.fishes = conf.get("fishes")        # 一个鱼群中的所有鱼
        self.fishCount = len(self.fishes)
        self.exitTime = self.enterTime + self.totalTime
        self.startFishId = startFishId
        self.endFishId = startFishId + self.fishCount - 1
        self.maxEnterTime = self._getMaxEnterTime()
        self.isClear = False
        # 鱼群被冰冻后延长的存活时间
        self.addTime = 0
        # Boss鱼群延迟出现时间
        self.extendGroupTime = 0
        # 鱼群死亡定时器
        self.deadTimer = None
        self.deadCallback = deadCallback
        if self.deadCallback:
            self.deadTimer = FTLoopTimer(self.totalTime, 0, self.deadCallback, self)
            self.deadTimer.start()

    def clear(self):
        """
        清除定时器等数据
        """
        if self.deadTimer:
            self.deadTimer.cancel()
            self.deadTimer = None
        self.isClear = True

    def isExist(self, nowTableTime):
        """
        该鱼群在当前时刻是否存在
        """
        return self.enterTime <= nowTableTime <= self.exitTime + self.addTime

    def fishExist(self, nowTableTime, fishId):
        """
        该鱼群中是否存在某条鱼
        """
        fish = self.fishes[fishId - self.startFishId]
        return (self.enterTime + fish["enterTime"] <= nowTableTime <= self.enterTime + fish["exitTime"] + self.addTime)

    def isAlive(self, nowTableTime, table=None):
        """
        该鱼群是否存活（包含特殊鱼及已生成但即将出现的鱼群）
        """
        # 客户端特殊处理的鱼群且鱼群中鱼的数量不多时，判断鱼群是否存活看其中鱼的存活状态
        if table and (self.type == "robot" or self.type == "piton" or self.type == "boss"):
            for fId in xrange(self.startFishId, self.endFishId + 1):
                isOK = table.findFish(fId)
                if isOK:
                    return isOK
        # 一般鱼群，判断鱼群是否存活看鱼群的整体退出时间，因为其中鱼的数量过多，避免循环查找
        return nowTableTime < self.exitTime + self.addTime

    def isVisible(self, table, userId):
        """
        该鱼群对某玩家是否可见
        """
        # 新手任务期间玩家自己可见的鱼.
        if self.type == "share" or self.type == "newbie" or self.type == "coupon" \
                or self.id.startswith("tuition_44499") or self.id.startswith("autofill_72025"):
            for fId in xrange(self.startFishId, self.endFishId + 1):
                if fId in table.fishMap:
                    if table.fishMap[fId]["owner"] is None or table.fishMap[fId]["owner"] == userId:
                        sendUsersList = table.fishMap[fId].get("sendUsersList")
                        if not sendUsersList or userId in sendUsersList:
                            return True
                        break
            return False
        return True

    def isCleared(self):
        """
        该鱼群是否已被清除
        """
        return self.isClear

    def _getMaxEnterTime(self):
        """
        获得该鱼群最后一条鱼在该鱼阵文件中的入场时间
        """
        fishEnterTimes = []
        for fish in self.fishes:
            fishEnterTimes.append(fish.get("enterTime"))
        fishEnterTimes.sort() 
        return fishEnterTimes[-1]

    def getNextGroupTime(self):
        """
        获得下个鱼群的入场时间
        """
        return round(self.maxEnterTime + self.enterTime, 2)

    def desc(self):
        """
        鱼群详情
        """
        info = [str(self.id), "enter:", str(self.enterTime), "exit:", str(self.exitTime), "startfishId:",
                str(self.startFishId), "endFishId:", str(self.endFishId), "addTime:", str(self.addTime)]
        info = " ".join(info)
        return info

    def adjust(self, addTime):
        """
        调整鱼群存活时间
        """
        self.addTime += addTime
        self.extendGroupTime += addTime
        if self.deadTimer:
            interval = self.deadTimer.getTimeOut() + self.addTime
            if interval > 0:
                self.deadTimer.reset(interval)