#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/8
"""
超级boss
"""
import random
import time

from freetime.util import log as ftlog
from newfish.entity import config, util


class SuperBossFishGroup(object):
    """
    超级boss鱼阵
    """
    def __init__(self):
        self._stageCount = 0

    def addTestSuperBoss(self):
        pass

    def isAppear(self):
        raise NotImplementedError

    def triggerCatchFishEvent(self, event):
        raise NotImplementedError

    def clearTimer(self):
        pass

    def dealEnterTable(self, userId):
        pass

    def frozen(self, fishId, fishType, frozenTime):
        pass

    def _getStageCount(self, fishType):
        """
        获取狂暴阶段数量
        """
        powerConf = config.getSuperbossPowerConf()
        countPctList = powerConf.get("power", {}).get(str(fishType), {}).get("countPct", [])
        if countPctList:
            idx = util.selectIdxByWeight(countPctList)
            return idx + 1 if idx >= 0 else 0
        else:
            return 0

    def _getPower(self, fishType):
        """
        获取狂暴阶段威力值
        """
        powerConf = config.getSuperbossPowerConf()
        basePower = powerConf.get("power", {}).get(str(fishType), {}).get("basePower", 0)
        if basePower:
            pctList = [val["probb"] for val in powerConf.get("powerRange", [])]
            idx = util.selectIdxByWeight(pctList)
            if idx >= 0:
                ratio = random.uniform(powerConf.get("powerRange")[idx]["min"], powerConf.get("powerRange")[idx]["max"])
                return int(basePower * ratio + 0.5)
        return 0

    def addFire(self, player, fId, weaponId, fpMultiple, multiple, fishType):
        """
        超级boss死亡后创建子弹数据
        """
        self._stageCount = self._getStageCount(fishType)
        if player and self._stageCount > 0:
            powerList = []
            for idx in range(self._stageCount):
                powerList.append(self._getPower(fishType))
            if ftlog.is_debug():
                ftlog.debug("SuperBossFishGroup, userId =", player.userId, "fId =", fId, "weaponId =", weaponId,
                            "fpMultiple =", fpMultiple, "fishType =", fishType, "powerList =", powerList)
            player.addFire(fId, weaponId, int(time.time()), fpMultiple, power=powerList,
                           multiple=multiple, clientFire=False, fishType=fishType)


def createSuperBoss(table):
    """
    超级boss鱼阵
    """
    from newfish.entity.fishgroup.box_fish_group import BoxFishGroup
    from newfish.entity.fishgroup.octopus_fish_group import OctopusFishGroup        # 巨型章鱼Boss鱼群
    from newfish.entity.fishgroup.queen_fish_group import QueenFishGroup
    superbossCls = {
        "44411": BoxFishGroup,
        "44412": OctopusFishGroup,
        "44414": QueenFishGroup
    }
    bigRoomId, _ = util.getBigRoomId(table.roomId)
    if ftlog.is_debug():
        ftlog.debug("createSuperBoss, tableId =", table.tableId, bigRoomId)
    if str(bigRoomId) in superbossCls:
        return superbossCls[str(bigRoomId)](table)
    return