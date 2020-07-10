# -*- coding=utf-8 -*-
"""
大奖赛table逻辑
"""
# @Author  : Kangxiaopeng
# @Time    : 2019/10/08

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.entity.dao import userdata
from newfish.entity import config
from newfish.entity.config import FISH_GAMEID
from newfish.entity.msg import GameMsg
from newfish.entity.fishgroup.fish_group_system import FishGroupSystem
from newfish.entity.fishgroup.normal_fish_group import NormalFishGroup
from newfish.table.friend_table import FishFriendTable
from newfish.entity.fishgroup.boss_fish_group import BossFishGroup
from newfish.entity.fishgroup.terror_fish_group import TerrorFishGroup
from newfish.entity.fishgroup.autofill_fish_group import AutofillFishGroup
from newfish.entity.fishgroup.grandprix_fish_group import GrandPrixFishGroup
from newfish.player.grand_prix_player import FishGrandPrixPlayer


class FishGrandPrixTable(FishFriendTable):

    def startFishGroup(self):
        """
        启动鱼阵
        """
        self.fishGroupSystem = FishGroupSystem(self)
        if self.runConfig.allNormalGroupIds:
            self.normalFishGroup = NormalFishGroup(self)
        # Boss鱼初始化
        if self.runConfig.allBossGroupIds:
            self.bossFishGroup = BossFishGroup(self)
        # terror鱼初始化
        if self.runConfig.allTerrorGroupIds:
            self.terrorFishGroup = TerrorFishGroup(self)
        # autofill鱼初始化
        if self.runConfig.allAutofillGroupIds:
            self.autofillFishGroup = AutofillFishGroup(self)
        # grandprix鱼初始化
        if self.runConfig.allGrandPrixGroupIds:
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
            # player.sendGrandPrixInfo()
            player.startGrandPrix()
            player.setTipTimer()

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
        player = self.getPlayer(userId)
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
            useSkillTimes = [val.get("count", 0) for val in player.grandPrixUseSkillTimes]
            msg.setResult("useSkillTimes", useSkillTimes)       # 可使用的次数
        GameMsg.sendMsg(msg, userId)
        ftlog.debug("broadcastSkillUse, userId =", userId, int(skill.skillId), skill.skillType, select, orgState)

    def _skill_install(self, msg, userId, seatId):
        """技能装备:1、卸下:0"""
        player = self.getPlayer(userId)
        if player and player.isGrandPrixMode():
            return
        super(FishGrandPrixTable, self)._skill_install(msg, userId, seatId)

    def _skill_replace(self, msg, userId, seatId):
        """技能替换 uninstallSkillId 要卸下的技能ID"""
        player = self.getPlayer(userId)
        if player and player.isGrandPrixMode():
            return
        super(FishGrandPrixTable, self)._skill_replace(msg, userId, seatId)

    def _skill_upgrade(self, msg, userId, seatId):
        """技能升级0、升星1"""
        player = self.getPlayer(userId)
        if player and player.isGrandPrixMode():
            return
        super(FishGrandPrixTable, self)._skill_upgrade(msg, userId, seatId)

    def _refresh_skill_cd(self, msg, userId, seatId):
        """刷新cd时间"""
        player = self.getPlayer(userId)
        if player and player.isGrandPrixMode():
            return
        super(FishGrandPrixTable, self)._refresh_skill_cd(msg, userId, seatId)
