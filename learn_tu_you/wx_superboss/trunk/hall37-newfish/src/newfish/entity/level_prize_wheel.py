#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: houguangdong
# Time: 2020/5/23

from copy import deepcopy

from hall.entity import datachangenotify
from poker.entity.dao import userchip
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from newfish.entity.msg import GameMsg
from newfish.entity.redis_keys import UserData
from newfish.entity.config import FISH_GAMEID
from newfish.entity import config, util
from newfish.entity.event import PrizeWheelSpinEvent
from newfish.entity.prize_wheel import PrizeWheel, PWState, PWValueSlot
from newfish.entity.redis_keys import GameData
from poker.entity.dao import gamedata


class LevelPrizeWheel(PrizeWheel):

    def __init__(self, userId, fishPool, roomId):
        super(LevelPrizeWheel, self).__init__(userId, fishPool, roomId)
        self.pwConf = config.getLevelPrizeWheelConf()
        self.rdKey = UserData.prizeWheelData_m % (FISH_GAMEID, self.userId)
        self.maxSpinTimes = self.pwConf.get("maxSpinTimes", 1)               # 最大转动次数
        self.isEnergyStorageMode = (self.maxSpinTimes > 1)                   # 是否是储能模式 True储能 False不是

    def getEnergyIdx(self):
        """
        获取当前充能的段位、可转的段位
        """
        level = 1
        spin_level = 1
        energy = {int(k): v for k, v in self.pwConf["energy"].items()}
        for lv, val in sorted(energy.items(), key=lambda d: d[0], reverse=True):
            data = self._getData(lv, 0)
            if int(data[0]) >= val:
                level = lv + 1
                break
        if level > max(energy.keys()):
            level -= 1
        if level > min(energy.keys()) and level < max(energy.keys()):                # 1、2、3、4
            spin_level = level - 1
        if level == max(energy.keys()):
            if self.pwData.get(str(level), [0])[0] >= energy.get(level, 0):
                spin_level = level
            else:
                spin_level = level - 1
        return level, spin_level

    def _getCostEnergy(self, level, fpMultiple):
        """
        当前段位抽奖需要消耗的能量
        :param level: 1、2、3、4、5
        :param fpMultiple: 渔场倍率
        """
        if not self._enable(level, fpMultiple):
            return 0
        total = self.pwConf["energy"][str(level)]      # 指定等级的需要的能量
        return total

    def _addEnergy(self, level, fpMultiple, value):
        """
        增加转盘抽奖点数
        """
        ret = False
        level = str(level)
        pwData = self._getData(level, fpMultiple)
        if pwData[PWValueSlot.SPINTIMES] >= self.maxSpinTimes:
            return ret
        if pwData[PWValueSlot.STATE] == PWState.NOT_SPIN:                            # self.isEnergyStorageMode or
            total = self._getCostEnergy(level, fpMultiple)
            if total > 0 and pwData[PWValueSlot.ENERGY] < total:
                pwData[PWValueSlot.ENERGY] += value                                 # 目标能量
                last_lv = int(level)
                energy = {int(k): v for k, v in self.pwConf["energy"].items()}
                for lv, val in sorted(energy.items(), key=lambda d: d[0]):
                    if lv >= int(level) and pwData[PWValueSlot.ENERGY] >= val:
                        last_lv = lv + 1
                    if last_lv == max(energy.keys()) + 1:
                        last_lv -= 1
                # 本级充能
                if last_lv == int(level):
                    tmp_energy = pwData[PWValueSlot.ENERGY]
                    if tmp_energy < total:
                        self.pwData[level] = pwData
                        self._setData(level, fpMultiple)
                        return True
                    pwData[PWValueSlot.ENERGY] = total
                    pwData[PWValueSlot.SPINTIMES] = 1
                    self.pwData[level] = pwData
                    self._setData(level, fpMultiple)
                    next_level = str(int(level) + 1)
                    if next_level in self.pwConf['energy'].keys():
                        init_data = deepcopy(self.default_val)
                        init_data[PWValueSlot.ENERGY] = int(tmp_energy)
                        self.pwData[next_level] = init_data
                        self._setData(next_level, fpMultiple)
                        return True
                # 跨级充能
                for lv in range(min(energy.keys()), last_lv + 1):
                    init_data = deepcopy(self.default_val)
                    if lv == 1:
                        init_data[PWValueSlot.BETCOUNT] = self._getData(lv, fpMultiple)[PWValueSlot.BETCOUNT]
                    if lv < last_lv:                                                # 重置之前等级数据
                        init_data[PWValueSlot.ENERGY] = energy[lv]
                    else:
                        init_data[PWValueSlot.ENERGY] = min(pwData[PWValueSlot.ENERGY], energy[lv])
                        data = self._getData(last_lv - 1, fpMultiple)
                        if data[PWValueSlot.ENERGY] >= energy[last_lv - 1]:
                            data[PWValueSlot.SPINTIMES] = 1
                            self.pwData[last_lv - 1] = data
                            self._setData(last_lv - 1, fpMultiple)
                    if last_lv == max(energy.keys()) and init_data[PWValueSlot.ENERGY] >= energy[last_lv]:
                        data = self._getData(str(last_lv - 1), fpMultiple)
                        data[PWValueSlot.SPINTIMES] = 0
                        self.pwData[last_lv - 1] = data
                        self._setData(last_lv - 1, fpMultiple)
                        init_data[PWValueSlot.SPINTIMES] = 1
                    self.pwData[str(lv)] = init_data
                    self._setData(lv, fpMultiple)
                ret = True
        return ret

    def _getEnergyPct(self, level, fpMultiple):
        """
        获取渔场轮盘充能进度
        :param level: 1、2、3、4、5 目标等级的能量
        :param fpMultiple: 渔场倍率
        :return:
        """
        level = str(level)
        if not self._enable(level, fpMultiple):
            return 0
        pwData = self._getData(level, fpMultiple)                   # self.getEnergyIdx()[0] 当前等级的能量   2100
        if not self.isEnergyStorageMode and pwData[PWValueSlot.STATE] != PWState.NOT_SPIN:       # 已经抽完奖|抽奖失败
            return 0
        if pwData[PWValueSlot.SPINTIMES] > 0:                       # 可以抽奖
            return 100
        total = self._getCostEnergy(level, fpMultiple)              # 目标等级的需要的能量 4000
        try:
            pct = int(100 * pwData[PWValueSlot.ENERGY] * 1. / total)
            pct = max(0, min(pct, 100))
        except:
            pct = 0
        return pct

    def sendEnergyProgress(self, level, fpMultiple, roomId, changed, fId=0):
        """
        发送轮盘进度
        """
        level = str(level)
        if level not in self.pwConf['energy']:
            level = str(self.getEnergyIdx()[0])
        if not self._enable(level, fpMultiple):
            return
        pwData = self._getData(level, fpMultiple)
        mo = MsgPack()
        mo.setCmd("prize_wheel_progress_m")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", self.userId)
        mo.setResult("roomId", roomId)
        mo.setResult("fId", fId)
        mo.setResult("progressPct", self._getEnergyPct(level, fpMultiple))      # 对应段位等级的进度百分比0-100. 100时可以抽奖.
        mo.setResult("nowLevel", level)                                         # 当前充能的段位
        mo.setResult("state", pwData[PWValueSlot.STATE])
        mo.setResult("progressChanged", changed)                                # 进度变化量，大于0表示增加，小于0表示减少，0表示同步数据
        mo.setResult("curRemainTimes", pwData[PWValueSlot.SPINTIMES])
        mo.setResult("is_can", 0 if self.pwConf['condition'] > gamedata.getGameAttrInt(self.userId, FISH_GAMEID, GameData.levelPrizeWheelCatchFishNumber) else 1)
        GameMsg.sendMsg(mo, self.userId)

    def getPrizeConf(self, level, fpMultiple):
        """
        获取等级转盘奖励配置
        """
        return self.pwConf["prize"].get(str(level), {})

    def getInfo(self, fpMultiple=0, level=0):
        """
        获取轮盘数据
        :param fpMultiple: 渔场倍率
        :param level: 段位1、2、3、4、5查询 0表示默认的转盘、-1表示转动轮盘
        """
        act = level
        if act in [0, -1]:                                                  # 默认进入是上一次达到最大段位的转盘
            level = self.getEnergyIdx()[1]                                  # 现在可抽奖所在的等级

        level = str(level)
        pwData = self._getData(level, fpMultiple)
        code = 1

        mo = MsgPack()
        mo.setCmd("prize_wheel_info_m")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", self.userId)
        mo.setResult("act", int(act))                                      # 动作 1、2、3、4、5查询 0默认等级 -1抽奖

        prizeConf = self.getPrizeConf(level, fpMultiple)
        info = {}
        # 获取转盘奖励数据
        prizeList = []
        weightList = []
        info["prizeList"] = prizeList
        if self._enable(level, fpMultiple):
            for idx, item in enumerate(prizeConf.get("wheel", [])):
                prizeList.append({
                    "name": item["rewards"]["name"],                        # 道具id
                    "count": item["rewards"]["count"]                       # 道具数量
                })
                enable = 1 if idx not in pwData[PWValueSlot.TAKEN] else 0
                prizeList[-1].update({"enable": enable})
                weightList.append(item["rate"] if enable else 0)            # 各种奖励的权重
            if int(act) >= 0:                                               # 查询
                code = 0
            elif int(act) == -1 and prizeList and weightList and sum(weightList) and \
                pwData[PWValueSlot.SPINTIMES] > 0 and \
                pwData[PWValueSlot.STATE] == PWState.NOT_SPIN and \
                self.getEnergyIdx()[1] >= 1:   # 抽奖 只能抽取最高等级的奖励
                code = self.spin(weightList, self.getEnergyIdx()[1])
            # 更新数据.
            pwData = self._getData(level, fpMultiple)
            if pwData[PWValueSlot.STATE] in [PWState.NOT_TAKE_REWARD, PWState.FAIL_SPIN]:
                if code == 0:                                               # 查询抽完奖励之后的领奖、重抽
                    consumeDiamond, rewards = self.getConsumeDiamond(pwData)
                    info["rewards"] = [rewards]                             # 奖励
                    info["paidInfo"] = {
                        "name": config.DIAMOND_KINDID,
                        "count": consumeDiamond
                    }
                    info["ratioList"] = pwData[PWValueSlot.RET]             # 转动转盘的结果
                    # 如果没有设置倍数则直接领取当前奖励.
                    if int(act) == -1 and len(info["ratioList"]) == 1:
                        self.setRewards(self.getEnergyIdx()[1], 1, "bet")   # 直接获取奖励
                    if pwData[PWValueSlot.STATE] == PWState.FAIL_SPIN:
                        info["betFail"] = pwData[PWValueSlot.BET]
                else:
                    info["rewards"] = []
                    info["ratioList"] = []
        else:
            info["rewards"] = []
            info["ratioList"] = []

        mo.setResult("info", info)                                          # 信息
        mo.setResult("code", code)                                          # 操作的码 0表示成功 1失败
        mo.setResult("state", pwData[PWValueSlot.STATE])                    # 当前转盘状态
        mo.setResult("curRemainTimes", pwData[PWValueSlot.SPINTIMES])       # 当前转盘次数
        mo.setResult("level", self.getEnergyIdx()[1])                       # 当前可抽奖的段位等级
        mo.setResult("is_can", [gamedata.getGameAttrInt(self.userId, FISH_GAMEID, GameData.levelPrizeWheelCatchFishNumber), self.pwConf['condition']])  # 捕获的鱼的条数 需要的捕获条数
        mo.setResult('nowProgressPct', self._getEnergyPct(str(level), fpMultiple))  # 当前等级的能量
        # 下一级别等级的转盘进度
        next_level = int(level) + 1
        if next_level <= max([int(k) for k in self.pwConf['energy'].keys()]):
            mo.setResult("nextProgressPct", self._getEnergyPct(str(next_level), fpMultiple))  # 当前转盘的能量/目标轮盘的能量
        GameMsg.sendMsg(mo, self.userId)

    def spin(self, weightList, level):
        """
        转动轮盘
        :param weightList: 奖励权重
        :param level: 段位1、2、3、4、5
        """
        level = str(level)
        fpMultiple = 1
        prizeConf = self.getPrizeConf(level, fpMultiple)
        pwData = self._getData(level, fpMultiple)
        try:
            # 获取轮盘结果
            if pwData[PWValueSlot.BETCOUNT] == 0 and int(level) == 1:
                idx = self.getSecondMaxIdx(weightList, level, fpMultiple)
            else:
                idx = util.selectIdxByWeight(weightList)
            rewards = prizeConf["wheel"][idx]["rewards"]
            ratioList = self._buildRetData(level, fpMultiple, rewards)
            pwData[PWValueSlot.RET] = ratioList
        except:
            code = 1
            self._resetPrizeWheelState(level, fpMultiple)
            ftlog.error("lpw_spin, userId =", self.userId)
            return code
        else:
            code = 0
            if not self.isEnergyStorageMode:
                pwData[PWValueSlot.SPINTIMES] = 0
            else:
                pwData[PWValueSlot.SPINTIMES] -= 1
                pwData[PWValueSlot.SPINTIMES] = max(0, pwData[PWValueSlot.SPINTIMES])
            pwData[PWValueSlot.STATE] = PWState.NOT_TAKE_REWARD
            self.sendEnergyProgress(level, fpMultiple, self.roomId, -1)         # 此段位的转盘能量为0
            self._setData(level, fpMultiple)
            from newfish.game import TGFish
            event = PrizeWheelSpinEvent(self.userId, config.FISH_GAMEID, self.roomId)
            TGFish.getEventBus().publishEvent(event)
            return code

    def getSecondMaxIdx(self, weightList, level, fpMultiple):
        """
        获取第二大的奖励索引
        """
        secondRateTmp = sorted(weightList)[1]
        prizeConf = self.getPrizeConf(level, fpMultiple)
        for idx, item in enumerate(prizeConf.get("wheel", [])):
            if item["rate"] == secondRateTmp:
                return idx
        return 0

    def setRewards(self, level, bet, betType=None):
        """
        确定转盘奖励结果
        :param level: 段位1、2、3、4、5
        :param bet: 倍率1、2、3、4
        :param betType: 'paid' 重新抽奖 'give_up': 放弃 'bet' 直接领取
        """
        rewards = []
        level = str(self.getEnergyIdx()[1])                                                     # 可领奖的等级
        fpMultiple = 1
        pwData = self._getData(level, fpMultiple)
        prizeConf = self.getPrizeConf(level, fpMultiple)
        weightList = []
        if self._enable(level, fpMultiple):
            for idx, item in enumerate(prizeConf.get("wheel", [])):
                enable = 1 if idx not in pwData[PWValueSlot.TAKEN] else 0
                weightList.append(item["rate"] if enable else 0)                                # 奖励概率

        code = 1
        if pwData[PWValueSlot.STATE] in [PWState.NOT_TAKE_REWARD, PWState.FAIL_SPIN] and len(pwData[PWValueSlot.RET]) > 0:
            consumeDiamond, _rewards = self.getConsumeDiamond(pwData)
            if pwData[PWValueSlot.STATE] == PWState.FAIL_SPIN and betType == "paid":            # 重新抽奖
                diamondCount = userchip.getDiamond(self.userId)
                if diamondCount >= consumeDiamond:
                    code = 0
                    clientId = util.getClientId(self.userId)
                    userchip.incrDiamond(self.userId, config.FISH_GAMEID, -consumeDiamond, self.roomId,
                                         "BI_NFISH_BUY_ITEM_CONSUME", config.DIAMOND_KINDID,
                                         clientId, param01="level_prize_wheel")
                    datachangenotify.sendDataChangeNotify(FISH_GAMEID, self.userId, ["chip"])
                    ratioList = self._buildRetData(level, fpMultiple, _rewards)
                    pwData[PWValueSlot.RET] = ratioList
                    pwData[PWValueSlot.STATE] = PWState.NOT_TAKE_REWARD
                    self._setData(level, fpMultiple)
                    self.getInfo(fpMultiple)

            elif pwData[PWValueSlot.STATE] == PWState.FAIL_SPIN and betType == "give_up":       # 放弃
                code = 0
                self._resetPrizeWheelState(level, fpMultiple)
                if ftlog.is_debug():
                    ftlog.debug("lpw_give_up,  giveup, userId =", self.userId, "level =", level, pwData[PWValueSlot.STATE])

            elif pwData[PWValueSlot.STATE] == PWState.NOT_TAKE_REWARD and betType == "bet":     # 抽奖
                for item in pwData[PWValueSlot.RET]:
                    if item["ratio"] != bet:
                        continue
                    try:
                        rewards = [item["rewards"][item["ret"]]]
                        if rewards[0].get("name") == 0 and rewards[0].get("count") == 0:        # 转盘转到谢谢参与的奖励
                            code = 0
                            self._resetPrizeWheelState(level, fpMultiple)
                        else:
                            if rewards and rewards[0].get("count", 0) > 0:                      # 抽奖成功，获得奖励
                                code = util.addRewards(self.userId, rewards, "BI_NFISH_LEVEL_PRIZE_WHEEL_REWARDS",
                                                       int(level), self.roomId, fpMultiple)
                                self._resetPrizeWheelState(level, fpMultiple)
                            else:                                                               # 抽奖失败，谢谢参与
                                code = 0
                                pwData[PWValueSlot.STATE] = PWState.FAIL_SPIN
                                pwData[PWValueSlot.BET] = bet
                                self._setData(level, fpMultiple)
                                self.getInfo(fpMultiple)
                    except:
                        ftlog.error("lpw_bet_m, userId =", self.userId, "level =", level,
                                    "bet =", bet, code, "data =", pwData[PWValueSlot.RET])
                    break

        self._setData(level, fpMultiple)
        mo = MsgPack()
        mo.setCmd("prize_wheel_bet_m")
        mo.setResult("betType", betType)
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", self.userId)
        mo.setResult("code", code)
        mo.setResult("bet", bet)
        mo.setResult("rewards", rewards)
        GameMsg.sendMsg(mo, self.userId)
        lv = self.getEnergyIdx()[0]                               # 重新计算当前转盘的段位
        self.sendEnergyProgress(lv, fpMultiple, self.roomId, 0)

    def catchFish(self, fId, fishConf, fpMultiple, gunX):
        """
        判断是否给轮盘充能
        :param fId: 鱼的id
        :param fishConf: 鱼的配置
        :param fpMultiple: 1、2、3、4、5
        :param gunX: 炮倍
        """
        level = str(self.getEnergyIdx()[0])
        if not self._enable(level, fpMultiple):
            return
        pwData = self._getData(level, fpMultiple)
        if pwData[PWValueSlot.STATE] != PWState.NOT_SPIN and not self.isEnergyStorageMode:
            return
        if pwData[PWValueSlot.SPINTIMES] >= self.maxSpinTimes:
            return
        val = fishConf.get("prizeWheelValue", 0) * fpMultiple * gunX
        if ftlog.is_debug():
            ftlog.debug("lpw_catch_fish, userId =", self.userId, "level =", level, "val =", val, fpMultiple, gunX)
        if val and self._addEnergy(level, fpMultiple, int(val)):
            number = gamedata.getGameAttrInt(self.userId, FISH_GAMEID, GameData.levelPrizeWheelCatchFishNumber)
            number += 1
            gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.levelPrizeWheelCatchFishNumber, number)
            self.sendEnergyProgress(0, fpMultiple, self.roomId, val, fId)       # 传0表示刷新当前最大的段位，因为会越级

    def _resetPrizeWheelState(self, level, fpMultiple):
        """
        重置转盘状态
        """
        for lv in self.pwConf["energy"].keys():                                 # 重置所有数据
            default_val = deepcopy(self.default_val)
            if int(lv) == 1:
                default_val[PWValueSlot.BETCOUNT] = self._getData(lv, fpMultiple)[PWValueSlot.BETCOUNT]
            self.pwData[lv] = default_val
            self._setData(lv, fpMultiple)
        gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.levelPrizeWheelCatchFishNumber, 0)

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
                if int(fishPool) == 1 and _bet == 2:                            # 青铜等级首次2倍竞猜必中双倍
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