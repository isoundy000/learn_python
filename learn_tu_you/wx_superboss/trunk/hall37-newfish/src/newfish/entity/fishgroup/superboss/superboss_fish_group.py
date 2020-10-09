# -*- coding=utf-8 -*-
"""
超级boss
"""
# @Author  : Kangxiaopeng
# @Time    : 2019/11/26


import random
import time

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config, util


class SuperBossFishGroup(object):
    """
    超级boss鱼阵
    """
    def __init__(self, table):
        self.table = table

    def clearTimer(self):
        """清理定时器"""
        pass

    def addTestSuperBoss(self):
        """添加测试Boss"""
        pass

    def isAppear(self):
        """是否出现"""
        raise NotImplementedError

    def triggerCatchFishEvent(self, event):
        """触发捕鱼事件"""
        raise NotImplementedError

    def dealEnterTable(self, userId):
        """处理进入桌子"""
        pass

    def frozen(self, fishId, fishType, frozenTime):
        """冰冻"""
        pass

    def appear(self):
        """
        超级Boss出现（含出现提示动画阶段）
        """
        self.table.autofillFishGroup and self.table.autofillFishGroup.startSuperBossAutofillFish()

    def leave(self):
        """
        超级Boss退场后添加鱼潮
        """
        self.table.clearFishGroup()
        self.table.tideFishGroup and self.table.tideFishGroup.addTideFishGroup()


def createSuperBoss(table):
    """
    超级boss鱼阵
    """
    from newfish.entity.fishgroup.superboss.box_fish_group import BoxFishGroup              # 宝箱怪鱼阵
    from newfish.entity.fishgroup.superboss.octopus_fish_group import OctopusFishGroup		# 巨型章鱼Boss鱼群
    from newfish.entity.fishgroup.superboss.queen_fish_group import QueenFishGroup          # 龙女王鱼阵
    from newfish.entity.fishgroup.superboss.dragon_fish_group import DragonFishGroup        # 远古寒龙Boss鱼群
    superBossCls = {
        "44411": BoxFishGroup,
        "44412": OctopusFishGroup,
        "44414": QueenFishGroup,
        "44415": DragonFishGroup
    }
    bigRoomId = str(table.bigRoomId)
    if ftlog.is_debug():
        ftlog.debug("createSuperBoss, tableId =", table.tableId, bigRoomId)
    if bigRoomId in superBossCls:
        return superBossCls[bigRoomId](table)
    return None