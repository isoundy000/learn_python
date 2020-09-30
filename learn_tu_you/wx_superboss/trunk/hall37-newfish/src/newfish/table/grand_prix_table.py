# -*- coding=utf-8 -*-
"""
大奖赛table逻辑
"""
# @Author  : Kangxiaopeng
# @Time    : 2019/10/08

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack

from newfish.entity import config
from newfish.entity.config import FISH_GAMEID
from newfish.entity.msg import GameMsg
from newfish.table.multiple_table import FishMultipleTable
from newfish.entity.fishgroup.terror_fish_group import TerrorFishGroup
from newfish.entity.fishgroup.autofill_fish_group_m import AutofillFishGroup
from newfish.entity.fishgroup.platter_fish_group import PlatterFishGroup
from newfish.player.grand_prix_player import FishGrandPrixPlayer
from newfish.entity.fishgroup.grandprix_fish_group import GrandPrixFishGroup


class FishGrandPrixTable(FishMultipleTable):

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
        # 大盘鱼初始化
        if self.runConfig.allPlatterGroupIds and not self.platterFishGroup:
            self.platterFishGroup = PlatterFishGroup(self)
        # grandprix鱼初始化
        if self.runConfig.allGrandPrixGroupIds and not self.grandPrixFishGroup:
            self.grandPrixFishGroup = GrandPrixFishGroup(self)

    def createPlayer(self, table, seatIndex, clientId):
        """
        新创建Player对象
        """
        return FishGrandPrixPlayer(table, seatIndex, clientId)

    def _afterSendTableInfo(self, userId):
        """
        发送桌子信息之后
        """
        super(FishGrandPrixTable, self)._afterSendTableInfo(userId)
        player = self.getPlayer(userId)
        if player:
            player.startGrandPrix()
            player.setTipTimer()

    def dealAfterCatchFish(self, player, fId, fishConf, fpMultiple, gunMultiple, gunX, wpId, catchMap):
        """
        在捕获结算之后处理部分鱼涉及的一些功能
        """
        # 大奖赛计算捕鱼积分
        if fishConf.get("score", 0) > 0 and fishConf["type"] not in config.TERROR_FISH_TYPE:
            fishType = self.fishMap[fId]["fishType"]
            point = fishConf["score"]
            if fishConf["type"] in config.MULTIPLE_FISH_TYPE and catchMap.get("fishMultiple", 1) > 1:
                point *= catchMap["fishMultiple"]
            point = player.addGrandPrixFishPoint(point, str(fishType), gunMultiple * gunX)
            if point:
                return {"fishPoint": {"fId": fId, "point": point}}
        return None

    def broadcastSkillUse(self, skill, select, userId, orgState):
        """
        广播选中/取消技能消息
        """
        msg = MsgPack()
        msg.setCmd("skill_use")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", skill.player.userId)
        msg.setResult("seatId", skill.player.seatId)
        msg.setResult("skillId", int(skill.skillId))
        msg.setResult("skillType", skill.skillType)
        msg.setResult("select", select)                         # 1选中|0取消
        msg.setResult("clip", skill.player.clip)                # 玩家子弹数
        msg.setResult("skillClip", skill.clip)                  # 技能子弹数
        GameMsg.sendMsg(msg, self.getBroadcastUids(userId))
        useSkillTimes = self.installGrandPrixUseSkillTimes(userId, skill, select, orgState)
        if useSkillTimes:
            msg.setResult("useSkillTimes", useSkillTimes)       # 可使用的次数
        GameMsg.sendMsg(msg, userId)
        if ftlog.is_debug():
            ftlog.debug("broadcastSkillUse, userId =", userId, int(skill.skillId), skill.skillType, select, orgState)

    def installGrandPrixUseSkillTimes(self, userId, skill, select, orgState):
        """初始化大奖赛使用技能次数"""
        player = self.getPlayer(userId)
        useSkillTimes = []
        if player and player.isGrandPrixMode():
            for idx, val in enumerate(player.grandPrixUseSkillTimes):
                if isinstance(val, dict) and val.get("skillId") == int(skill.skillId) and val.get("skillType", 0) == skill.skillType:
                    if select and orgState == 0:
                        player.grandPrixUseSkillTimes[idx]["count"] -= 1    # 使用减少一次
                    elif not select and orgState == 1:
                        player.grandPrixUseSkillTimes[idx]["count"] += 1    # 增加一次
                    player.grandPrixUseSkillTimes[idx]["count"] = min(player.grandPrixUseSkillTimes[idx]["count"], config.getGrandPrixConf("fireCount")[1])
                    player.grandPrixUseSkillTimes[idx]["count"] = max(player.grandPrixUseSkillTimes[idx]["count"], 0)
                    break
            useSkillTimes = {val.get("skillId"): val.get("count", 0) for val in player.grandPrixUseSkillTimes}
        return useSkillTimes

    def _skill_install(self, msg, userId, seatId):
        """大奖赛不能技能装备:1、卸下:0"""
        player = self.getPlayer(userId)
        if player and player.isGrandPrixMode():
            return
        super(FishGrandPrixTable, self)._skill_install(msg, userId, seatId)

    def _skill_replace(self, msg, userId, seatId):
        """大奖赛事件不能技能替换 uninstallSkillId 要卸下的技能ID"""
        player = self.getPlayer(userId)
        if player and player.isGrandPrixMode():
            return
        super(FishGrandPrixTable, self)._skill_replace(msg, userId, seatId)

    def _skill_upgrade(self, msg, userId, seatId):
        """大奖赛事件不能升级|升星 技能升级0、升星1"""
        player = self.getPlayer(userId)
        if player and player.isGrandPrixMode():
            return
        super(FishGrandPrixTable, self)._skill_upgrade(msg, userId, seatId)

    def _refresh_skill_cd(self, msg, userId, seatId):
        """大奖赛不能刷新cd时间"""
        player = self.getPlayer(userId)
        if player and player.isGrandPrixMode():
            return
        super(FishGrandPrixTable, self)._refresh_skill_cd(msg, userId, seatId)

    def _broadcastPlayerLeave(self, userId, seatId):
        msg = MsgPack()
        msg.setCmd("leave")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", userId)
        msg.setResult("seatId", seatId)
        GameMsg.sendMsg(msg, self.getBroadcastUids(userId))