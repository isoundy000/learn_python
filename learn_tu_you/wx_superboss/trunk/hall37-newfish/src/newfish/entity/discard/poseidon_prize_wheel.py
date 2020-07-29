# -*- coding: utf-8 -*-
"""
Created by zhanglin on：2019-12-06
"""
import random
from newfish.entity.discard.grand_prix_prize_wheel import GrandPrixPrizeWheel
from freetime.util import log as ftlog
from newfish.entity.prize_wheel import PWState, PWValueSlot


class PoseidonPrizeWheel(GrandPrixPrizeWheel):

    def __init__(self, userId, fishPool, roomId):
        super(PoseidonPrizeWheel, self).__init__(userId, fishPool, roomId)
        self.fishPool = 44501     # 海皇来袭转盘和大奖赛转盘共享进度，共用一份存档

    def catchFish(self, fId, fishConf, fpMultiple, gunMultiple):
        """
        判断是否给轮盘充能
        """
        if not self._enable(self.fishPool, fpMultiple):
            return
        pwData = self._getData(self.fishPool, fpMultiple)
        if pwData[PWValueSlot.STATE] != PWState.NOT_SPIN and not self.isEnergyStorageMode:
            return
        if pwData[PWValueSlot.SPINTIMES] >= self.maxSpinTimes:
            return
        rate = fishConf.get("triggerRate", 0)
        rand = random.randint(1, 10000)
        if rand > rate:
            return
        val = fishConf.get("prizeWheelValue", 0) * fpMultiple * gunMultiple
        if val > 0:
            self.addEnergyPool(fpMultiple, val)
        addUnit = self.pwConf.get("energy")[0].get(str(fpMultiple), {}).get("addUnit", 0)
        if pwData[PWValueSlot.ENERGYPOOL] >= addUnit and val:
            if self._addEnergy(self.fishPool, fpMultiple, addUnit):
                pwData[PWValueSlot.ENERGYPOOL] -= addUnit
                self._setData(self.fishPool, fpMultiple)
                self.sendEnergyProgress(self.fishPool, fpMultiple, self.roomId, addUnit, fId)
        if ftlog.is_debug():
            ftlog.debug("poseidon_prize_wheel, userId =", self.userId,
                    "fpMultiple =", fpMultiple, addUnit, self._getData(self.fishPool, fpMultiple))
