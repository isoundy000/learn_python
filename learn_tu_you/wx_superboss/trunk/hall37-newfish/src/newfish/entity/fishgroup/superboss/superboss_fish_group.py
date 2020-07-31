# -*- coding=utf-8 -*-
"""
超级boss
"""
# @Author  : Kangxiaopeng
# @Time    : 2019/11/26


import random
import time

from freetime.util import log as ftlog
from newfish.entity import config, util


class SuperBossFishGroup(object):
    """
    超级boss鱼阵
    """
    def __init__(self):
        self._stageCount = 0                                # 获取狂暴阶段数量

    def addTestSuperBoss(self):
        """添加测试Boss"""
        pass

    def isAppear(self):
        """是否出现"""
        raise NotImplementedError

    def triggerCatchFishEvent(self, event):
        """触发捕鱼事件"""
        raise NotImplementedError

    def clearTimer(self):
        """清理定时器"""
        pass

    def dealEnterTable(self, userId):
        """处理进入桌子"""
        pass

    def frozen(self, fishId, fishType, frozenTime):
        """冰冻"""
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

    def addFire(self, player, fId, weaponId, fpMultiple, gunMultiple, fishType):
        """
        超级boss死亡后创建子弹数据
        """
        self._stageCount = self._getStageCount(fishType)                            # 狂暴次数
        if player and self._stageCount > 0:
            powerList = []
            for idx in range(self._stageCount):
                powerList.append(self._getPower(fishType))                          # 狂暴威力值
            if ftlog.is_debug():
                ftlog.debug("SuperBossFishGroup, userId =", player.userId, "fId =", fId, "weaponId =", weaponId,
                            "fpMultiple =", fpMultiple, "fishType =", fishType, "powerList =", powerList)
            player.addFire(fId, weaponId, int(time.time()), fpMultiple, power=powerList,
                           gunMultiple=gunMultiple, clientFire=False, fishType=fishType)


def createSuperBoss(table):
    """
    超级boss鱼阵
    """
    from newfish.entity.fishgroup.superboss.box_fish_group import BoxFishGroup              # 宝箱怪鱼阵
    from newfish.entity.fishgroup.superboss.octopus_fish_group import OctopusFishGroup		# 巨型章鱼Boss鱼群
    from newfish.entity.fishgroup.superboss.queen_fish_group import QueenFishGroup          # 龙女王鱼阵
    from newfish.entity.fishgroup.superboss.dragon_fish_group import DragonFishGroup        # 远古寒龙Boss鱼群
    superbossCls = {
        "44411": BoxFishGroup,
        "44412": OctopusFishGroup,
        "44414": QueenFishGroup,
        "44415": DragonFishGroup
    }
    bigRoomId, _ = util.getBigRoomId(table.roomId)
    if ftlog.is_debug():
        ftlog.debug("createSuperBoss, tableId =", table.tableId, bigRoomId)
    if str(bigRoomId) in superbossCls:
        return superbossCls[str(bigRoomId)](table)
    return