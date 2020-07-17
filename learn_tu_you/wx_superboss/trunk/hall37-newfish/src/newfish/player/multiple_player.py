# -*- coding=utf-8 -*-
"""
Created by lichen on 2020/3/27.
"""

import random

from freetime.util import log as ftlog
from newfish.player.normal_player import FishNormalPlayer
from newfish.entity import config
from newfish.entity.skill import skill_release_m
from newfish.entity.gun.gun_effect import GunEffect, State as GunEffectState


class FishMultiplePlayer(FishNormalPlayer):
    """千炮场的玩家"""
    def __init__(self, table, seatIndex, clientId):
        super(FishMultiplePlayer, self).__init__(table, seatIndex, clientId)
        self.gunEffect = GunEffect(table, self, self.table.gameMode)        # 皮肤炮的使用效果

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
            self.gunEffect.addGunEffectFire(self.gunId, 1)                      # 狂暴增加开火次数
            self.gunEffect.addGunEffectEnergy(self.gunId, args[0])              # 狂暴增加能量值
        elif _type == 4:
            self.gunEffect.clearTimer()                                         # 清理狂暴定时器
            self.gunEffect.dumpData(gunId)                                      # 保存数据
        elif _type == 5:
            self.gunEffect.sendProgress(gunId)                                  # 狂暴炮的能量和子弹 断线
            self.gunEffect.sendUseEffectState(gunId)                            # 狂暴炮的炮台信息