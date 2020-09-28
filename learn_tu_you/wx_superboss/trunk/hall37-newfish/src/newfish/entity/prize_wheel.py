# -*- coding=utf-8 -*-
"""
渔场转盘
"""
# @Author  : Kangxiaopeng
# @Time    : 2019/8/12

import json
import random
from copy import deepcopy

from hall.entity import datachangenotify
from poker.entity.dao import userchip, daobase
from poker.entity.configure import gdata
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from newfish.entity.msg import GameMsg
from newfish.entity.redis_keys import GameData, UserData
from newfish.entity.config import FISH_GAMEID
from newfish.entity import config, util
from newfish.entity.event import PrizeWheelSpinEvent


# 测试时增加能量获取相应的倍数.
test_add_energy_ratio = 1
test_trigger_ratio = 1


# 转盘状态
class PWState:
    NOT_SPIN = 0            # 未抽奖
    NOT_TAKE_REWARD = 1     # 未领奖
    FAIL_SPIN = 3           # 抽奖失败


# 转盘存档数据
class PWValueSlot:
    ENERGY = 0          # 能量值
    STATE = 1           # 转盘状态
    RET = 2             # 转盘结果
    TAKEN = 3           # 已领取的奖励
    BETCOUNT = 4        # 多倍竞猜次数
    BET = 5             # 选中的竞猜倍数
    ENERGYPOOL = 6      # 充能池
    SPINTIMES = 7       # 可用抽奖次数


def setUserPrizeWheelData(userId, fishPool=0, val=None):
    """
    设置玩家渔场转盘存档，慎用！
    """
    rdKey = UserData.prizeWheelData % (FISH_GAMEID, userId)
    # 删除对应渔场数据
    if val is None:
        if fishPool != 0:
            daobase.executeUserCmd(userId, "HDEL", rdKey, str(fishPool))
        else:
            daobase.executeUserCmd(userId, "DEL", rdKey)
    else:
        if fishPool != 0:
            daobase.executeUserCmd(userId, "HSET", rdKey, str(fishPool), json.dumps(val))


class PrizeWheel(object):

    # 能量值，转盘状态，抽奖结果索引(包含选择押注的结果)，已获得的奖励索引，十倍场首次双倍竞猜必中双倍标记，选中的竞猜倍数, 占位, 可用抽奖次数
    # ENERGY, STATE, RET, TAKEN, BETCOUNT, BET, ENERGYPOOL, SPINTIMES
    default_val = [0, 0, [], [], 0, 0, 0, 0]

    def __init__(self, userId, fishPool, roomId):
        self.userId = userId
        self.fishPool = fishPool
        self.roomId = roomId
        self.rdKey = UserData.prizeWheelData % (FISH_GAMEID, self.userId)
        self.pwData = {}
        self.pwConf = config.getPrizeWheelConf()
        # 是否为储能模式
        self.maxSpinTimes = self.pwConf.get("maxSpinTimes", 1)
        self.isEnergyStorageMode = (self.maxSpinTimes > 1)

    def dumpData(self):
        pass

    def _enable(self, fishPool, fpMultiple):
        """
        渔场是否开启轮盘
        """
        fishPool = str(fishPool)
        return fishPool in self.pwConf["prize"]

    def _getData(self, fishPool, fpMultiple):
        """
        获取渔场转盘数据
        """
        fishPool = str(fishPool)
        if fishPool not in self.pwData:
            val = daobase.executeUserCmd(self.userId, "HGET", self.rdKey, fishPool)
            val = json.loads(val) if val else deepcopy(self.default_val)
            self.pwData[fishPool] = val
            # 处理新增数据.
            isUpdate = False
            for _idx, _value in enumerate(deepcopy(self.default_val)):
                if _idx + 1 > len(val):                                     # 有新增的数据
                    isUpdate = True
                    if _idx == PWValueSlot.BETCOUNT:
                        _value = 1                                          # 老用户多倍竞猜次数为1
                    elif _idx == PWValueSlot.SPINTIMES:
                        self.pwData[fishPool].insert(_idx, 0)
                        idx = len(self.pwData[fishPool][PWValueSlot.TAKEN]) % len(self.pwConf["energy"])
                        total = self.pwConf["energy"][idx][fishPool]["cost"]
                        if self.pwData[fishPool][PWValueSlot.ENERGY] >= total and self.pwData[fishPool][PWValueSlot.STATE] == PWState.NOT_SPIN:
                            self.pwData[fishPool][PWValueSlot.ENERGY] = 0
                            self.pwData[fishPool][PWValueSlot.SPINTIMES] = 1
                        continue
                    self.pwData[fishPool].insert(_idx, _value)
            if self.pwData[fishPool][PWValueSlot.SPINTIMES] > self.maxSpinTimes:
                self.pwData[fishPool][PWValueSlot.SPINTIMES] = self.maxSpinTimes
                isUpdate = True
            if isUpdate:
                self._setData(fishPool, fpMultiple)
        return self.pwData[fishPool]

    def _setData(self, fishPool, fpMultiple):
        """
        设置渔场转盘数据
        """
        if not self._enable(fishPool, fpMultiple):
            return
        fishPool = str(fishPool)
        val = self.pwData.get(fishPool)
        if val:
            daobase.executeUserCmd(self.userId, "HSET", self.rdKey, fishPool, json.dumps(val))

    def _getEnergyIdx(self, fishPool, fpMultiple):
        """
        获取当前充能阶段索引
        """
        fishPool = str(fishPool)
        pwData = self._getData(fishPool, fpMultiple)
        return (len(pwData[PWValueSlot.TAKEN]) + pwData[PWValueSlot.SPINTIMES]) % len(self.pwConf["energy"])

    def _getCostEnergy(self, fishPool, fpMultiple):
        """
        当前抽奖需要消耗的能量
        """
        if not self._enable(fishPool, fpMultiple):
            return 0
        fishPool = str(fishPool)
        pwData = self._getData(fishPool, fpMultiple)
        idx = self._getEnergyIdx(fishPool, fpMultiple)
        try:
            total = self.pwConf["energy"][idx][fishPool]["cost"]
        except:
            ftlog.error("prize_wheel, userId =", self.userId,
                        "fishPool =", fishPool, "fpMultiple =", fpMultiple, "pwData =", pwData)
            total = 0
        if ftlog.is_debug():
            ftlog.debug("prize_wheel, userId =", self.userId, "fishPool =", fishPool, "fpMultiple =", fpMultiple,
                        "idx =", idx, "pwData =", pwData)
        return total

    def _addEnergy(self, fishPool, fpMultiple, value):
        """
        增加转盘抽奖点数
        """
        if ftlog.is_debug():
            value *= test_add_energy_ratio
        ret = False
        fishPool = str(fishPool)
        pwData = self._getData(fishPool, fpMultiple)
        if pwData[PWValueSlot.SPINTIMES] >= self.maxSpinTimes:
            if ftlog.is_debug():
                ftlog.debug("prize_wheel 1, userId =", self.userId, "ret =", ret,
                            "fishPool =", fishPool, "fpMultiple =", fpMultiple, "value =", value, "pwData =", pwData)
            return ret
        if self.isEnergyStorageMode or pwData[PWValueSlot.STATE] == PWState.NOT_SPIN:
            total = self._getCostEnergy(fishPool, fpMultiple)
            if total > 0 and pwData[PWValueSlot.ENERGY] < total:
                pwData[PWValueSlot.ENERGY] += value
                if pwData[PWValueSlot.ENERGY] >= total:
                    pwData[PWValueSlot.ENERGY] = 0
                    if self.isEnergyStorageMode:
                        pwData[PWValueSlot.SPINTIMES] += 1
                        if pwData[PWValueSlot.SPINTIMES] >= self.maxSpinTimes:
                            pwData[PWValueSlot.SPINTIMES] = self.maxSpinTimes
                            ftlog.info("prize_wheel, userId =", self.userId, "fishPool =", fishPool,
                                       "fpMultiple =", fpMultiple, "pwData =", pwData)
                    else:
                        pwData[PWValueSlot.SPINTIMES] = 1
                    if ftlog.is_debug():
                        ftlog.debug("prize_wheel 2, userId =", self.userId, "fishPool =", fishPool,
                                    "fpMultiple =", fpMultiple, "pwData =", pwData)
                self._setData(fishPool, fpMultiple)
                ret = True
        if ftlog.is_debug():
            ftlog.debug("prize_wheel, userId =", self.userId, "ret =", ret,
                        "fishPool =", fishPool, "fpMultiple =", fpMultiple, "value =", value, "pwData =", pwData)
        return ret

    def _resetEnergy(self, fishPool, fpMultiple, lastIdx):
        """
        充值转盘充能数据
        """
        if not self._enable(fishPool, fpMultiple):
            return
        fishPool = str(fishPool)
        pwData = self._getData(fishPool, fpMultiple)
        if pwData[PWValueSlot.ENERGY] != 0:
            try:
                if self.isEnergyStorageMode:
                    idx = self._getEnergyIdx(fishPool, fpMultiple)
                    total = self.pwConf["energy"][idx][fishPool]["cost"]
                    lastTotal = self.pwConf["energy"][lastIdx][fishPool]["cost"]
                    pwData[PWValueSlot.ENERGY] = min(int(1. * pwData[PWValueSlot.ENERGY] * total / lastTotal), total)
                else:
                    pwData[PWValueSlot.ENERGY] = 0
            except:
                pwData[PWValueSlot.ENERGY] = 0
            self._setData(fishPool, fpMultiple)

    def _getEnergyPct(self, fishPool, fpMultiple):
        """
        获取渔场轮盘充能进度
        """
        if not self._enable(fishPool, fpMultiple):
            return 0
        pwData = self._getData(fishPool, fpMultiple)
        if not self.isEnergyStorageMode:
            if pwData[PWValueSlot.STATE] != PWState.NOT_SPIN:
                return 0
        if pwData[PWValueSlot.SPINTIMES] > 0:
            return 100
        fishPool = str(fishPool)
        total = self._getCostEnergy(fishPool, fpMultiple)
        try:
            pct = int(100 * pwData[PWValueSlot.ENERGY] * 1. / total)
            pct = max(0, min(pct, 100))
        except:
            ftlog.error("prize_wheel, userId =", self.userId,
                        "fishPool =", fishPool, "fpMultiple =", fpMultiple, "total =", total, "pwData =", pwData)
            pct = 0
        return pct

    def sendEnergyProgress(self, fishPool, fpMultiple, roomId, changed, fId=0):
        """
        发送轮盘进度
        """
        if not self._enable(fishPool, fpMultiple):
            return
        fishPool = str(fishPool)
        pwData = self._getData(fishPool, fpMultiple)
        mo = MsgPack()
        mo.setCmd("prize_wheel_progress")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", self.userId)
        mo.setResult("roomId", roomId)
        mo.setResult("fId", fId)
        mo.setResult("progressPct", self._getEnergyPct(fishPool, fpMultiple))
        mo.setResult("state", pwData[PWValueSlot.STATE])
        mo.setResult("progressChanged", changed)
        mo.setResult("curRemainTimes", pwData[PWValueSlot.SPINTIMES])
        GameMsg.sendMsg(mo, self.userId)
        if ftlog.is_debug():
            ftlog.debug("prize_wheel, userId =", self.userId,
                        "fishPool =", fishPool, "fpMultiple =", fpMultiple, "mo =", mo)

    def getPrizeConf(self, fishPool, fpMultiple):
        """
        获取转盘奖励配置
        """
        fishPool = str(fishPool)
        return self.pwConf["prize"].get(fishPool, {})

    def getInfo(self, fpMultiple, action=0):
        """
        获取轮盘数据
        """
        fishPool = str(self.fishPool)
        pwData = self._getData(fishPool, fpMultiple)
        code = 1

        mo = MsgPack()
        mo.setCmd("prize_wheel_info")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", self.userId)
        mo.setResult("act", action)

        prizeConf = self.getPrizeConf(fishPool, fpMultiple)
        info = {}
        # 获取转盘奖励数据
        prizeList = []
        weightList = []
        info["prizeList"] = prizeList
        if self._enable(fishPool, fpMultiple):
            for idx, item in enumerate(prizeConf.get("wheel", [])):
                prizeList.append({"name": item["rewards"]["name"], "count": item["rewards"]["count"]})
                enable = 1 if idx not in pwData[PWValueSlot.TAKEN] else 0
                prizeList[-1].update({"enable": enable})
                weightList.append(item["rate"] if enable else 0)
            if action == 0:# 查询
                code = 0
            elif action == 1 and prizeList and weightList and sum(weightList) \
                    and pwData[PWValueSlot.SPINTIMES] > 0 and pwData[PWValueSlot.STATE] == PWState.NOT_SPIN:    # 抽奖
                code = self.spin(weightList, fpMultiple)
            # 更新数据.
            pwData = self._getData(fishPool, fpMultiple)
            if pwData[PWValueSlot.STATE] in [PWState.NOT_TAKE_REWARD, PWState.FAIL_SPIN]:
                if code == 0:
                    consumeDiamond, rewards = self.getConsumeDiamond(pwData)
                    info["rewards"] = [rewards]
                    info["paidInfo"] = {"name": config.DIAMOND_KINDID, "count": consumeDiamond}
                    info["ratioList"] = pwData[PWValueSlot.RET]
                    # 如果没有设置倍数则直接领取当前奖励.
                    if action == 1 and len(info["ratioList"]) == 1:
                        self.setRewards(fpMultiple, 1, "bet")
                    if pwData[PWValueSlot.STATE] == PWState.FAIL_SPIN:
                        info["betFail"] = pwData[PWValueSlot.BET]
                else:
                    info["rewards"] = []
                    info["ratioList"] = []
        else:
            info["rewards"] = []
            info["ratioList"] = []
        mo.setResult("info", info)
        mo.setResult("code", code)
        mo.setResult("state", pwData[PWValueSlot.STATE])
        mo.setResult("curRemainTimes", pwData[PWValueSlot.SPINTIMES])
        nextRoomId = prizeConf.get("nextRoomId", 0)
        if nextRoomId:
            bigRoomId, _ = util.getBigRoomId(nextRoomId)
            nextFishPool = util.getFishPoolByBigRoomId(bigRoomId)
            mo.setResult("nextRoomId", nextRoomId)
            mo.setResult("nextRoomMultiple", prizeConf.get("nextRoomMultiple", 0))
            mo.setResult("nextProgressPct", self._getEnergyPct(nextFishPool, fpMultiple))
            mo.setResult("nextRemainTimes", self._getData(nextFishPool, fpMultiple)[PWValueSlot.SPINTIMES])
        GameMsg.sendMsg(mo, self.userId)
        if ftlog.is_debug():
            ftlog.debug("prize_wheel, userId =", self.userId,
                        "fishPool =", fishPool, "fpMultiple =", fpMultiple, "msg =", mo)

    def spin(self, weightList, fpMultiple):
        """
        转动轮盘
        """
        fishPool = str(self.fishPool)
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
            ftlog.error("prize_wheel, userId =", self.userId)
            return code
        else:
            code = 0
            _idx = len(pwData[PWValueSlot.TAKEN])
            if _idx >= len(self.pwConf["energy"]):
                _idx = -1
            pwData[PWValueSlot.TAKEN].append(idx)
            # 扣除可用抽奖次数.
            if not self.isEnergyStorageMode:
                pwData[PWValueSlot.SPINTIMES] = 0
            else:
                pwData[PWValueSlot.SPINTIMES] -= 1
                pwData[PWValueSlot.SPINTIMES] = max(0, pwData[PWValueSlot.SPINTIMES])
            pwData[PWValueSlot.STATE] = PWState.NOT_TAKE_REWARD
            self.sendEnergyProgress(self.fishPool, fpMultiple, self.roomId, -1)
            # 给其他渔场充能
            addEnergy = self.pwConf["energy"][_idx].get(fishPool, {}).get("add", {})
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
            consumeDiamond, _rewards = self.getConsumeDiamond(pwData)
            if pwData[PWValueSlot.STATE] == PWState.FAIL_SPIN and betType == "paid":
                diamondCount = userchip.getDiamond(self.userId)
                if diamondCount >= consumeDiamond:
                    code = 0
                    clientId = util.getClientId(self.userId)
                    userchip.incrDiamond(self.userId, config.FISH_GAMEID, -consumeDiamond, self.roomId,
                                         "BI_NFISH_BUY_ITEM_CONSUME", config.DIAMOND_KINDID,
                                         clientId, param01="prize_wheel")
                    datachangenotify.sendDataChangeNotify(FISH_GAMEID, self.userId, ["chip"])
                    ratioList = self._buildRetData(fishPool, fpMultiple, _rewards)
                    pwData[PWValueSlot.RET] = ratioList
                    pwData[PWValueSlot.STATE] = PWState.NOT_TAKE_REWARD
                    self._setData(fishPool, fpMultiple)
                    self.getInfo(fpMultiple)

            elif pwData[PWValueSlot.STATE] == PWState.FAIL_SPIN and betType == "give_up":
                code = 0
                self._resetPrizeWheelState(fishPool, fpMultiple)
                if ftlog.is_debug():
                    ftlog.debug("prize_wheel,  giveup, userId =", self.userId, "fishPool =", self.fishPool,
                                pwData[PWValueSlot.STATE])

            elif pwData[PWValueSlot.STATE] == PWState.NOT_TAKE_REWARD and betType == "bet":
                for item in pwData[PWValueSlot.RET]:
                    if item["ratio"] != bet:
                        continue
                    try:
                        rewards = [item["rewards"][item["ret"]]]
                        code = 0
                        if rewards and rewards[0].get("count", 0) > 0:      # 抽奖成功，获得奖励
                            code = util.addRewards(self.userId, rewards, "BI_NFISH_PRIZE_WHEEL_REWARDS", int(fishPool), self.roomId, fpMultiple)
                            self.addRoomLotteryProfitCoin(rewards)
                            self._resetPrizeWheelState(fishPool, fpMultiple)
                        else:                                               # 抽奖失败，谢谢参与
                            pwData[PWValueSlot.STATE] = PWState.FAIL_SPIN
                            pwData[PWValueSlot.BET] = bet
                            self._setData(fishPool, fpMultiple)
                            self.getInfo(fpMultiple)
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

    def catchFish(self, fId, fishConf, fpMultiple, gunX):
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
        val = fishConf.get("prizeWheelValue", 0) * fpMultiple * gunX
        if ftlog.is_debug():
            ftlog.debug("prize_wheel, userId =", self.userId, "fishPool =", self.fishPool, "rand, rate =", rand, rate, "val =", val, fpMultiple, gunX)
        if ftlog.is_debug():
            rate *= test_trigger_ratio
        if rand <= rate and val:
            if self._addEnergy(self.fishPool, fpMultiple, val):
                self.sendEnergyProgress(self.fishPool, fpMultiple, self.roomId, val, fId)

    def _buildRetData(self, fishPool, fpMultiple, rewards):
        """
        生成单次结果数据
        :param pwData: 转盘数据
        :param fishPool: 渔场号
        :param rewards: 直接领取的奖励
        """
        ratioList = []
        ratioList.append({"ratio": 1, "rewards": [{"name": rewards["name"], "count": rewards["count"], "rate": 100}], "ret": 0})
        prizeConf = self.getPrizeConf(fishPool, fpMultiple)
        pwData = self._getData(fishPool, fpMultiple)
        if rewards.get("name", 0) and rewards.get("count", 0):
            for _bet in prizeConf.get("betList", []):
                _betConfList = self.pwConf["bet"].get(str(_bet), {}).get(fishPool) or self.pwConf["bet"].get(str(_bet), {}).get("0")
                if len(_betConfList) == 0:
                    continue
                _betsWeight = [_ratio["weight"] for _ratio in _betConfList]
                _idx = util.selectIdxByWeight(_betsWeight)
                ratioDict = {}
                ratioDict["ratio"] = _bet
                ratioDict["ret"] = _idx
                if int(fishPool) == 44002 and _bet == 2:    # 10倍场首次2倍竞猜必中双倍
                    if pwData[PWValueSlot.BETCOUNT] == 0:
                        ratioDict["ret"] = 1
                else:
                    ratioDict["ret"] = _idx
                pwData[PWValueSlot.BETCOUNT] += 1
                ratioDict["rewards"] = []
                for _ratio in _betConfList:
                    _betRewards = {
                        "name": rewards["name"], "rate": _ratio["rate"],
                        "count": rewards["count"] * _ratio.get("ratio", 0) + _ratio.get("extra", 0)
                    }
                    ratioDict["rewards"].append(_betRewards)
                ratioList.append(ratioDict)
        return ratioList

    def getConsumeDiamond(self, pwData):
        """
        获取钻石抽奖需要消耗的钻石数量
        """
        for item in pwData[PWValueSlot.RET]:
            if item["ratio"] == 1:
                rewards = item["rewards"][0]
                consumeDiamond = rewards["count"] // 30000  # 抽奖需要消耗的钻石数量
                return max(consumeDiamond, 1), rewards
        return 0, {}

    def _resetPrizeWheelState(self, fishPool, fpMultiple):
        """
        重置转盘状态
        """
        pwData = self._getData(fishPool, fpMultiple)
        prizeConf = self.getPrizeConf(fishPool, fpMultiple)
        pwData[PWValueSlot.STATE] = PWState.NOT_SPIN
        pwData[PWValueSlot.RET] = []
        # 重置轮盘已获取的数据.
        lastIdx = self._getEnergyIdx(fishPool, fpMultiple)
        if len(pwData[PWValueSlot.TAKEN]):
            idx = pwData[PWValueSlot.TAKEN][-1]
            if prizeConf["wheel"][idx]["reset"] == 1 or len(pwData[PWValueSlot.TAKEN]) >= len(prizeConf["wheel"]):
                pwData[PWValueSlot.TAKEN] = []
        # 扣除本场能量
        self._resetEnergy(self.fishPool, fpMultiple, lastIdx)
        self._setData(fishPool, fpMultiple)

    def addRoomLotteryProfitCoin(self, rewards):
        """
        渔场转盘获得的金币计入房间奖池
        """
        profitCoin = config.BULLET_KINDIDS.get(rewards[0]["name"], rewards[0]["count"])
        room = gdata.rooms()[self.roomId]
        _, _, tableId, _ = util.isInFishTable(self.userId)
        if tableId and profitCoin:
            table = room.maptable[tableId]
            player = table.getPlayer(self.userId)
            player.addProfitCoin(profitCoin)
            ftlog.info("setRewards->addProfitCoin =", profitCoin)