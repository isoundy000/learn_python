# -*- coding=utf-8 -*-
"""
Created by lichen on 2020/3/27.
"""

import random

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from newfish.player.normal_player import FishNormalPlayer
from newfish.entity import config, weakdata
from newfish.entity.redis_keys import WeakData, GameData
from newfish.entity.skill import skill_release_m
from newfish.entity.gun.gun_effect import GunEffect, State as GunEffectState
from poker.entity.dao import gamedata
from newfish.entity.event import ChangeGunLevelEvent
from newfish.entity.msg import GameMsg
from newfish.entity import mini_game


class FishMultiplePlayer(FishNormalPlayer):
    """千炮场的玩家"""
    def __init__(self, table, seatIndex, clientId):
        super(FishMultiplePlayer, self).__init__(table, seatIndex, clientId)
        self.gunEffect = GunEffect(table, self, self.table.gameMode)            # 皮肤炮的使用效果

    def tableMaxGunLevel(self, isSend=False):
        """
        扩展最大的等级
        """
        tableGunLevel = self.maxGunLevel()
        if isSend:
            self.gunChange(tableGunLevel if self.nowGunLevel >= tableGunLevel else self.nowGunLevel)
        return tableGunLevel

    def gunChange(self, gLv):
        """
        切换火炮等级
        """
        reason = 0
        if gLv > self.gunLevel or not config.getGunLevelConf(gLv, self.table.gameMode):
            reason = 1
        else:
            if gLv < self.table.runConfig.minGunLevel:
                return
            elif gLv > self.tableMaxGunLevel():
                return
            elif self.getUsingSkillInfo():
                # 技能处于使用中时，升级炮台，炮台等级需等技能状态结束后才会切换更新
                self.nowGunLevel = gLv
                return
        gunMultiple = config.getGunConf(self.gunId, self.clientId, self.gunLv, self.table.gameMode).get("multiple", 1)
        retMsg = MsgPack()
        retMsg.setCmd("gchg")
        retMsg.setResult("gameId", config.FISH_GAMEID)
        retMsg.setResult("gLv", gLv)
        retMsg.setResult("userId", self.userId)
        retMsg.setResult("seatId", self.seatId)
        retMsg.setResult("gunMultiple", gunMultiple)
        retMsg.setResult("gameMode", self.table.gameMode)
        retMsg.setResult("reason", reason)
        retMsg.setResult("tableMaxGunLevel", self.tableMaxGunLevel())
        GameMsg.sendMsg(retMsg, self.userId)
        if reason == 0:
            self.nowGunLevel = gLv
            result = retMsg.getKey("result")
            del result["reason"]
            GameMsg.sendMsg(retMsg, self.table.getBroadcastUids(self.userId))
            from newfish.game import TGFish
            event = ChangeGunLevelEvent(self.userId, config.FISH_GAMEID, self.table.bigRoomId, self.nowGunLevel)
            TGFish.getEventBus().publishEvent(event)
            self.syncSkillSlots()

    def _loadSkillData(self, skillId, skillType=0):
        """
        读取单个技能数据
        """
        if skillId in self.skillSlots:
            self.skillSlots[skillId][2] = None

    def gunEffectState(self, _type=-1, *args):
        """
        玩家皮肤炮狂暴的状态
        """
        gunId = self.gunId
        if _type == 0 and args:
            gunId = args[0]
            if (gunId in self.gunEffect.useGunEffect and
                self.gunEffect.useGunEffect[gunId]["state"] in [GunEffectState.USING, GunEffectState.PAUSE]):
                self.gunEffect.clearUeTimer()                                   # 旧的定时器清除掉
                self.gunEffect.updateFireOrEnergy(gunId, idx=1, absValue=1)     # 清理子弹数
                self.gunEffect._setData(gunId)
                if gunId in self.gunEffect.useGunEffect:
                    del self.gunEffect.useGunEffect[gunId]
        elif _type == 1:
            self.gunEffect.sendProgress(gunId, isSend=0)                        # 发送新的狂暴炮开火数 切换炮台
            self.gunEffect.sendUseEffectState(gunId)                            # 发送新的狂暴炮的状态 切换炮台
        elif _type == 2:
            self.gunEffect.usingOrPause()                                       # 使用技能的时候暂停或使用 | 技能使用结束
        elif _type == 3:
            self.gunEffect.addGunEffectFire(gunId, 1)                           # 狂暴增加开火次数
            self.gunEffect.addGunEffectEnergy(gunId, args[0])                   # 狂暴增加能量值
        elif _type == 4:
            self.gunEffect.clearTimer()                                         # 清理狂暴定时器
            self.gunEffect.dumpData(gunId)                                      # 保存数据
        elif _type == 5:
            self.gunEffect.sendProgress(gunId)                                  # 狂暴炮的能量和子弹 断线
            self.gunEffect.sendUseEffectState(gunId)                            # 狂暴炮的炮台信息
        elif _type == 6:
            self.gunEffect.firstFireEffect(gunId)                               # 触发狂暴效果
            return self.gunEffect.addGunEffectPower(args[0], args[1], args[2])  # 增加子弹威力


    def _miniMermaidStart(self, fishTypes, gunM):
        """
        开始小游戏美人鱼的馈赠, 8101是美人鱼小游戏id
        """
        isTrigger = False
        for fishType in fishTypes:
            if fishType in config.MINI_GAME_FISH_TYPE:
                isTrigger = True
                break
        if isTrigger and mini_game.addCard(self.table.roomId, self, gunM):
            ret = mini_game.miniGameStart(self.table, self, 1, gunM)
            msg = MsgPack()
            msg.setCmd("mini_game_start")
            msg.setResult("gameId", config.FISH_GAMEID)
            msg.setResult("userId", self.userId)
            msg.setResult("seatId", self.seatId)
            for key, value in ret.items():
                msg.setResult(key, value)
            GameMsg.sendMsg(msg, self.table.getBroadcastUids())