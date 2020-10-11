# -*- coding=utf-8 -*-
"""
Created by lichen on 2020/3/27.
"""

import random
import time
from collections import OrderedDict

from freetime.util import log as ftlog
from newfish.table.normal_table import FishNormalTable
from newfish.player.multiple_player import FishMultiplePlayer
from newfish.entity import config, util
from newfish.entity.fishgroup.terror_fish_group import TerrorFishGroup
from newfish.entity.fishgroup.boss_fish_group_m import BossFishGroup
from newfish.entity.fishgroup.autofill_fish_group_m import AutofillFishGroup
from newfish.entity.fishgroup.superboss import superboss_fish_group
from newfish.entity.fishgroup.platter_fish_group import PlatterFishGroup
from newfish.entity.fishgroup.minigame_fish_group import MiniGameFishGroup
from newfish.entity.fishgroup.tide_fish_group import TideFishGroup


class FishMultipleTable(FishNormalTable):

    def __init__(self, room, tableId):
        super(FishMultipleTable, self).__init__(room, tableId)
        self.actionMap["dragon_iceball"] = self._dragon_iceball

    def createPlayer(self, table, seatIndex, clientId):
        """
        新创建Player对象
        """
        return FishMultiplePlayer(table, seatIndex, clientId)

    def startFishGroup(self):
        """
        启动鱼阵
        """
        # terror鱼初始化
        if self.runConfig.allTerrorGroupIds and not self.terrorFishGroup:
            self.terrorFishGroup = TerrorFishGroup(self)
        # 自动填充鱼初始化
        if self.runConfig.allAutofillGroupIds and not self.autofillFishGroup:
            self.autofillFishGroup = AutofillFishGroup(self)
        # 普通Boss初始化
        if self.runConfig.allBossGroupIds and not self.bossFishGroup:
            self.bossFishGroup = BossFishGroup(self)
        # 超级Boss初始化
        if self.runConfig.allSuperBossGroupIds and not self.superBossFishGroup:
            self.superBossFishGroup = superboss_fish_group.createSuperBoss(self)
        # 鱼潮初始化
        if self.runConfig.allTideGroupIds and not self.tideFishGroup:
            self.tideFishGroup = TideFishGroup(self)
        # 大盘鱼初始化
        if self.runConfig.allPlatterGroupIds and not self.platterFishGroup:
            self.platterFishGroup = PlatterFishGroup(self)
        # 小游戏鱼初始化
        if self.runConfig.allMiniGameGroupIds and not self.miniGameFishGroup:
            self.miniGameFishGroup = MiniGameFishGroup(self)

    def _afterSendTableInfo(self, userId):
        """
        发送桌子信息之后
        """
        super(FishMultipleTable, self)._afterSendTableInfo(userId)
        self.superBossFishGroup and self.superBossFishGroup.dealEnterTable(userId)

    def _catchFish(self, player, bulletId, wpId, fIds, extends, stageId):
        """
        检测能否捕到鱼
        :param player: 玩家
        :param bulletId: 子弹Id
        :param wpId: 武器ID
        :param fIds: 鱼
        :param extends: 扩展数据
        :param stageId: 阶段Id
        """
        catch, gain, gainChip, exp = [], [], 0, 0
        isInvalid, notCatchFids, fIdTypes = False, [], {}
        # 扩展Id（用于获取特殊武器的子弹数据，一般为特殊鱼的fId）
        extendId = extends[0] if extends else 0
        wpConf = config.getWeaponConf(wpId, mode=self.gameMode)
        wpType = util.getWeaponType(wpId)
        # 狂暴弹数据
        superBullet = player.getFire(bulletId).get("superBullet", {})
        # 子弹所属渔场倍率
        fpMultiple = player.getFireFpMultiple(bulletId, extendId)
        # 子弹所属的炮配置
        gunConf = player.getGunConf(bulletId, extendId)
        # 子弹所属火炮倍数（1-10000倍炮）
        gunX = player.getFireGunX(bulletId, extendId)
        # 子弹所属火炮倍率（单|双倍炮）
        gunMultiple = player.getFireGunMultiple(bulletId, extendId) or gunConf.get("multiple", 1)
        # 普通火炮一网单鱼，特殊武器一网多鱼
        fIds = fIds[-1:] if wpType == config.GUN_WEAPON_TYPE else fIds
        # 普通火炮概率系数
        gunOdds = player.dynamicOdds.getOdds()
        for fId in fIds:
            isOK, catchUserId = self.verifyFish(player.userId, fId)
            if isOK:
                # 特殊鱼互相之间不会触发捕获判定
                if (wpType in config.SPECIAL_WEAPON_TYPE_SET and
                    self.fishMap[fId]["type"] in config.SPECIAL_WEAPON_FISH_TYPE):
                    continue
            else:
                isInvalid = True
                # TODO (lichen) 需要测试前端鱼阵是否合法
                # ftlog.error("_catchFish error",
                #             "fId =", fId,
                #             "userId =", player.userId,
                #             "tableId =", self.tableId,
                #             "wpId =", wpId,
                #             "hasSuperBossFishGroup =", self.hasSuperBossFishGroup(),
                #             "hasTideFishGroup =", self.hasTideFishGroup())
                continue
            catchMap, catchMap["fId"], catchMap["reason"] = {}, fId, 1      # catchMap = {"fId": fId, "reason": 1}
