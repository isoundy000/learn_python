# -*- coding=utf-8 -*-
"""
概述模块或脚本
"""
# @Author  : Kangxiaopeng
# @Time    : 2019/11/12

import json
import random
from copy import deepcopy

from poker.entity.dao import userchip, daobase
from poker.entity.configure import gdata
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from newfish.entity.msg import GameMsg
from newfish.entity.redis_keys import GameData
from newfish.entity.config import FISH_GAMEID
from newfish.entity import config, util
from newfish.entity.event import PrizeWheelSpinEvent
from newfish.entity.prize_wheel import PrizeWheel, PWState, PWValueSlot


class GrandPrixPrizeWheel(PrizeWheel):

    # 能量值，转盘状态，抽奖结果索引(包含选择押注的结果)，已获得的奖励索引，十倍场首次双倍竞猜必中双倍标记，选中的竞猜倍数, 充能池, 可用抽奖次数
    # ENERGY, STATE, RET, TAKEN, BETCOUNT, BET, ENERGYPOOL, SPINTIMES
    gp_default_val = [0, 0, [], [], 0, 0, 0, 0]

    def __init__(self, userId, fishPool, roomId):
        super(GrandPrixPrizeWheel, self).__init__(userId, fishPool, roomId)
        self.pwConf = config.getGrandPrixPrizeWheelConf()
        self.fireRatio = self.pwConf.get("ratio", {}).get("fire", 0)    # 开火充能系数
        self.lossRatio = self.pwConf.get("ratio", {}).get("loss", 0)    # 亏损充能系数
        self.maxSpinTimes = self.pwConf.get("maxSpinTimes", 1)
        self.isEnergyStorageMode = (self.maxSpinTimes > 1)

    def dumpData(self):
        if str(self.fishPool) in self.pwData and self.pwData[str(self.fishPool)].keys():
            self._setData(self.fishPool, self.pwData[str(self.fishPool)].keys()[0])

    def _enable(self, fishPool, fpMultiple):
        """
        渔场是否开启轮盘
        """
        fpMultiple = str(fpMultiple)
        return fpMultiple in self.pwConf["prize"]

    def _getData(self, fishPool, fpMultiple):
        """
        获取渔场转盘数据
        """
        fishPool = str(fishPool)
        fpMultiple = str(fpMultiple)
        if fishPool not in self.pwData:
            val = daobase.executeUserCmd(self.userId, "HGET", self.rdKey, fishPool)
            val = json.loads(val) if val else {}
            self.pwData[fishPool] = val
        self.pwData[fishPool].setdefault(fpMultiple, deepcopy(self.gp_default_val))
        # 处理新增数据.
        isUpdate = False
        for _idx, _value in enumerate(deepcopy(self.gp_default_val)):
            if _idx >= len(self.pwData[fishPool][fpMultiple]):  # 有新增的数据
                isUpdate = True
                if _idx == PWValueSlot.SPINTIMES:
                    self.pwData[fishPool][fpMultiple].insert(_idx, 0)
                    idx = len(self.pwData[fishPool][fpMultiple][PWValueSlot.TAKEN]) % len(self.pwConf["energy"])
                    total = self.pwConf["energy"][idx][fpMultiple]["cost"]
                    if self.pwData[fishPool][fpMultiple][PWValueSlot.ENERGY] >= total and self.pwData[fishPool][fpMultiple][PWValueSlot.STATE] == PWState.NOT_SPIN:
                        self.pwData[fishPool][fpMultiple][PWValueSlot.ENERGY] = 0
                        self.pwData[fishPool][fpMultiple][PWValueSlot.SPINTIMES] = 1
                    continue
                self.pwData[fishPool][fpMultiple].insert(_idx, _value)
        if self.pwData[fishPool][fpMultiple][PWValueSlot.SPINTIMES] > self.maxSpinTimes:
            self.pwData[fishPool][fpMultiple][PWValueSlot.SPINTIMES] = self.maxSpinTimes
            isUpdate = True
        # 限制能量池中的能量最多为1次抽奖的能量.
        idx = len(self.pwData[fishPool][fpMultiple][PWValueSlot.TAKEN]) % len(self.pwConf["energy"])
        total = self.pwConf["energy"][idx][fpMultiple]["cost"]
        if self.pwData[fishPool][fpMultiple][PWValueSlot.ENERGYPOOL] > total:
            self.pwData[fishPool][fpMultiple][PWValueSlot.ENERGYPOOL] = total
            isUpdate = True
        if isUpdate:
            self._setData(fishPool, fpMultiple)
        return self.pwData[fishPool][fpMultiple]

    def _getCostEnergy(self, fishPool, fpMultiple):
        """
        当前抽奖需要消耗的能量
        """
        if not self._enable(fishPool, fpMultiple):
            return 0
        fishPool = str(fishPool)
        fpMultiple = str(fpMultiple)
        pwData = self._getData(fishPool, fpMultiple)
        idx = self._getEnergyIdx(fishPool, fpMultiple)                  # len(pwData[PWValueSlot.TAKEN])
        try:
            total = self.pwConf["energy"][idx][fpMultiple]["cost"]
        except:
            ftlog.error("grand_prix_prize_wheel, userId =", self.userId,
                        "fishPool =", fishPool, "fpMultiple =", fpMultiple, "pwData =", pwData)
            total = 0
        return total

    def getPrizeConf(self, fishPool, fpMultiple):
        """
        获取转盘奖励配置
        """
        fpMultiple = str(fpMultiple)
        return self.pwConf["prize"].get(fpMultiple, {})

    def spin(self, weightList, fpMultiple):
        """
        转动轮盘
        """
        fishPool = str(self.fishPool)
        fpMultiple = str(fpMultiple)
        prizeConf = self.getPrizeConf(fishPool, fpMultiple)
        pwData = self._getData(fishPool, fpMultiple)
        try:
            # 获取轮盘结果
            idx = util.selectIdxByWeight(weightList)
            rewards = prizeConf["wheel"][idx]["rewards"]
            ratioList = self._buildRetData(fishPool, fpMultiple, rewards)
            pwData[PWValueSlot.RET] = ratioList
        except:
            code = 1
            self._resetPrizeWheelState(fishPool, fpMultiple)
            ftlog.error("grand_prix_prize_wheel, userId =", self.userId)
            return code
        else:
            code = 0
            _idx = len(pwData[PWValueSlot.TAKEN])
            if _idx >= len(self.pwConf["energy"]):
                _idx = -1
            pwData[PWValueSlot.TAKEN].append(idx)
            if not self.isEnergyStorageMode:
                pwData[PWValueSlot.SPINTIMES] = 0
            else:
                pwData[PWValueSlot.SPINTIMES] -= 1
                pwData[PWValueSlot.SPINTIMES] = max(0, pwData[PWValueSlot.SPINTIMES])
            pwData[PWValueSlot.STATE] = PWState.NOT_TAKE_REWARD
            self.sendEnergyProgress(self.fishPool, fpMultiple, self.roomId, -1)
            # 给其他渔场充能
            addEnergy = self.pwConf["energy"][_idx].get(fpMultiple, {}).get("add", {})
            for roomId, val in addEnergy.iteritems():
                roomId = int(roomId)
                bigRoomId, _ = util.getBigRoomId(roomId)
                fp = util.getFishPoolByBigRoomId(bigRoomId)
                if self._addEnergy(fp, fpMultiple, val):
                    self.sendEnergyProgress(fp, fpMultiple, roomId, val)
            self._setData(fishPool, fpMultiple)
            from newfish.game import TGFish
            event = PrizeWheelSpinEvent(self.userId, config.FISH_GAMEID, self.roomId)
            TGFish.getEventBus().publishEvent(event)
            return code

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
        addUnit = self.pwConf.get("energy")[0].get(str(fpMultiple), {}).get("addUnit", 0)
        if pwData[PWValueSlot.ENERGYPOOL] >= addUnit:
            if self._addEnergy(self.fishPool, fpMultiple, addUnit):
                pwData[PWValueSlot.ENERGYPOOL] -= addUnit
                self._setData(self.fishPool, fpMultiple)
                self.sendEnergyProgress(self.fishPool, fpMultiple, self.roomId, addUnit, fId)
        ftlog.debug("grand_prix_prize_wheel, userId =", self.userId,
                    "fpMultiple =", fpMultiple, addUnit, self._getData(self.fishPool, fpMultiple))

    def _resetEnergy(self, fishPool, fpMultiple, lastIdx):
        """
        充值转盘充能数据
        """
        if not self._enable(fishPool, fpMultiple):
            return
        fishPool = str(fishPool)
        pwData = self._getData(fishPool, fpMultiple)
        if not self.isEnergyStorageMode and (pwData[PWValueSlot.ENERGY] or pwData[PWValueSlot.ENERGYPOOL]):
            pwData[PWValueSlot.ENERGY] = 0
            pwData[PWValueSlot.ENERGYPOOL] = 0
            self._setData(fishPool, fpMultiple)
        if ftlog.is_debug():
            ftlog.debug("grand_prix_prize_wheel, userId =", self.userId,
                        "fishPool =", fishPool, "fpMultiple =", fpMultiple, "data =", pwData)

    def getConsumeDiamond(self, pwData):
        """
        获取钻石抽奖需要消耗的钻石数量
        """
        for item in pwData[PWValueSlot.RET]:
            if item["ratio"] == 1:
                rewards = item["rewards"][0]
                if rewards["name"] in config.BULLET_KINDIDS:
                    consumeDiamond = (config.BULLET_KINDIDS[rewards["name"]] * rewards["count"]) // 2000  # 抽奖需要消耗的钻石数量
                else:
                    consumeDiamond = rewards["count"] // 2000  # 抽奖需要消耗的钻石数量
                return consumeDiamond, rewards
        return 0, {}

    def setRewards(self, fpMultiple, bet, betType=None):
        """
        确定转盘奖励结果
        """
        rewards = []
        fishPool = str(self.fishPool)
        pwData = self._getData(fishPool, fpMultiple)
        prizeConf = self.getPrizeConf(fishPool, fpMultiple)
        weightList = []
        if self._enable(fishPool, fpMultiple):
            for idx, item in enumerate(prizeConf.get("wheel", [])):
                enable = 1 if idx not in pwData[PWValueSlot.TAKEN] else 0
                weightList.append(item["rate"] if enable else 0)
        code = 1
        if pwData[PWValueSlot.STATE] in [PWState.NOT_TAKE_REWARD, PWState.FAIL_SPIN] and len(pwData[PWValueSlot.RET]) > 0:
            if pwData[PWValueSlot.STATE] == PWState.NOT_TAKE_REWARD and betType == "bet":
                for item in pwData[PWValueSlot.RET]:
                    if item["ratio"] == bet:
                        try:
                            rewards = [item["rewards"][item["ret"]]]
                            if rewards and rewards[0].get("count", 0) > 0:  # 抽奖成功，获得奖励
                                code = util.addRewards(self.userId, rewards, "BI_NFISH_PRIZE_WHEEL_REWARDS",
                                                       int(fishPool), self.roomId, fpMultiple)
                                self.addRoomLotteryProfitCoin(rewards)
                            else:
                                if ftlog.is_debug():
                                    ftlog.debug("prize_wheel, userId =", self.userId, "fishPool =", fishPool,
                                                "bet =", bet, code, "data =", pwData[PWValueSlot.RET])
                            self._resetPrizeWheelState(fishPool, fpMultiple)
                        except:
                            ftlog.error("prize_wheel, userId =", self.userId, "fishPool =", fishPool, "bet =", bet, code, "data =", pwData[PWValueSlot.RET])
                        break
        self._setData(fishPool, fpMultiple)
        mo = MsgPack()
        mo.setCmd("prize_wheel_bet")
        mo.setResult("betType", betType)
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", self.userId)
        mo.setResult("code", code)
        mo.setResult("bet", bet)
        mo.setResult("rewards", rewards)
        GameMsg.sendMsg(mo, self.userId)
        self.sendEnergyProgress(self.fishPool, fpMultiple, self.roomId, 0)

    def addEnergyPool(self, fpMultiple, val):
        """
        渔场倍率充能池
        """
        pwData = self._getData(self.fishPool, fpMultiple)
        if pwData[PWValueSlot.STATE] != PWState.NOT_SPIN and not self.isEnergyStorageMode:
            return
        # total = self._getCostEnergy(self.fishPool, fpMultiple)
        # if total and pwData[PWValueSlot.ENERGY] >= total
        #     return
        if pwData[PWValueSlot.SPINTIMES] >= self.maxSpinTimes:
            return
        pwData[PWValueSlot.ENERGYPOOL] += val
        # 限制能量池中的能量最多为1次抽奖的能量.
        fpMultiple = str(fpMultiple)
        idx = self._getEnergyIdx(self.fishPool, fpMultiple)
        total = self.pwConf["energy"][idx][fpMultiple]["cost"]
        if pwData[PWValueSlot.ENERGYPOOL] > total:
            pwData[PWValueSlot.ENERGYPOOL] = total

    def fireCoin(self, fpMultiple, val):
        """
        开火累计倍率充能池
        """
        if not self._enable(self.fishPool, fpMultiple):
            return
        _val = val * self.fireRatio
        if _val > 0:
            self.addEnergyPool(fpMultiple, _val)
        ftlog.debug("grand_prix_prize_wheel, userId =", self.userId,
                    "fpMultiple =", fpMultiple, val, self.fireRatio, _val, self._getData(self.fishPool, fpMultiple))

    def lossCoin(self, fpMultiple, val):
        """
        亏损累计倍率充能池
        """
        if not self._enable(self.fishPool, fpMultiple) or val >= 0:
            return False
        _val = abs(val) * self.lossRatio
        ftlog.debug("grand_prix_prize_wheel, userId =", self.userId,
                    "fpMultiple =", fpMultiple, val, self.lossRatio, _val, self._getData(self.fishPool, fpMultiple))
        if _val > 0:
            self.addEnergyPool(fpMultiple, _val)
            return True
        return False
