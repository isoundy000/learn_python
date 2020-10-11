#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/23
"""
# 0 默认炮
# 1288: 飓风 1等级 0经验 1352默认皮肤
# 1165: 霜冻
1166: 炎龙
1167: 魅影
1289: 光辉
1290: 暮刃
"""
import json
import time
from copy import deepcopy
from newfish.entity import config, util
from newfish.entity.redis_keys import UserData
from newfish.entity.msg import GameMsg
from poker.entity.dao import daobase
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer


class State(object):

    NOT_EFFECT = -1     # 没有效果的炮
    NOT_USE = 0         # 不能使用
    CAN_USE = 1         # 可用
    PREPARE = 5         # 准备
    USING = 2           # 使用中
    PAUSE = 3           # 暂停
    END = 4             # 结束


class GunEffect(object):
    """
    千炮模式下皮肤炮的效果
    """
    defaultVal = [0, 0]                                # 能量值, 开火次数

    def __init__(self, table, player, mode):
        self.table = table
        self.player = player
        self.userId = player.userId
        self.clientId = player.clientId
        self.mode = mode
        self.rdKey = UserData.gunEffect_m % (config.FISH_GAMEID, player.userId)
        self.gunEffectData = {}                         # {gunId: [energy, fireCount], ...}
        self.updateFireEnergyTimer = None               # 同步能量和开火次数的定时器
        self._interval = 3                              # 循环间隔
        self.setFireEnergyTimer()                       # 启动定时器
        self.useEffectTimer = None                      # 使用狂暴技能的定时器
        self.useGunEffect = {}                          # 使用狂暴炮的效果

    def clearTimer(self):
        """清理定时器"""
        self.clearFnTimer()
        self.clearUeTimer()

    def clearFnTimer(self):
        """清理同步开火和能量的定时器"""
        if self.updateFireEnergyTimer:
            self.updateFireEnergyTimer.cancel()
            self.updateFireEnergyTimer = None

    def clearUeTimer(self):
        """清理狂暴效果的定时器"""
        if self.useEffectTimer:
            self.useEffectTimer.cancel()
            self.useEffectTimer = None

    def setFireEnergyTimer(self):
        """启动同步状态和能量值的定时器"""
        self.clearFnTimer()
        self.updateFireEnergyTimer = FTLoopTimer(self._interval, -1, self.sendProgress)
        self.updateFireEnergyTimer.start()

    def setUseEffectTimer(self, duration=6):
        """设置使用狂暴效果的定时器"""
        if duration <= 0:
            return
        self.clearUeTimer()
        self.useEffectTimer = FTLoopTimer(duration, 0, self.sendUseEffectState)
        self.useEffectTimer.start()

    def _getData(self, gunId):
        """
        获取狂暴皮肤炮的效果
        """
        conf = config.getGunConf(gunId, self.clientId, 1, self.mode)
        if "fire_count" not in conf:
            return []
        if conf["fire_count"] > 0 and gunId not in self.gunEffectData:
            val = daobase.executeUserCmd(self.userId, "HGET", self.rdKey, gunId)
            val = json.loads(val) if val else deepcopy(self.defaultVal)
            self.gunEffectData[gunId] = val
            self._setData(gunId)
        return self.gunEffectData.get(gunId, [])

    def _setData(self, gunId):
        """
        设置皮肤炮效果
        """
        val = self.gunEffectData.get(gunId, [])
        if not val:
            return
        daobase.executeUserCmd(self.userId, "HSET", self.rdKey, gunId, json.dumps(val))

    def dumpData(self, gunId=None):
        """
        保存数据
        """
        gunId = self.player.gunId if gunId is None else gunId
        if gunId in self.gunEffectData:
            self._setData(gunId)

    def addGunEffectPower(self, gunId, power, gunX):
        """
        使用狂暴弹增加威力
        """
        if gunId not in self.useGunEffect:
            return power, False
        data = self.useGunEffect[gunId]
        if data["state"] != State.USING:
            return power, False
        if float('%.2f' % time.time()) - data["start_time"] + data["progress"][0] >= data["progress"][1]:
            return power, False
        if gunId not in self.gunEffectData:
            return power, False
        data = self.gunEffectData[gunId]
        if not data:
            return power, False
        conf = config.getGunConf(gunId, self.clientId, 1, self.mode)
        if data[0] >= int(power * gunX * conf["power_rate"] / 100.0):
            val = int(power * gunX * (conf["power_rate"] / 100.0 - 1))
            self.updateFireOrEnergy(self, gunId, 0, val, add=False)                     # 消耗能量
            newPower = power * conf["power_rate"] / 100.0                               # 最大威力
        else:
            self.updateFireOrEnergy(self, gunId, 0, absValue=1)
            newPower = power * (float(data[0]) / (power * gunX * conf["power_rate"] / 100.0) + 1)
        if ftlog.is_debug():
            ftlog.debug("addGunEffectPower", newPower)
        return newPower, True

    def addGunEffectFire(self, gunId, count):
        """
        增加开火次数
        :param gunId: 武器ID
        :param count: 次数
        """
        if gunId in self.useGunEffect and self.useGunEffect[gunId]["state"] in [State.USING, State.PAUSE]:
            return
        count = self.updateFireOrEnergy(gunId, 1, count)
        conf = config.getGunConf(gunId, self.clientId, 1, self.mode)
        if count >= conf["fire_count"]:                                                 # 达到了临界值把内存的数据保存到数据库
            self.sendProgress(gunId)
            self._setData(gunId)
        return count

    def firstFireEffect(self, gunId):
        """开火第一颗子弹触发狂暴效果"""
        if gunId in self.useGunEffect and self.useGunEffect[gunId]["state"] == State.PREPARE:
            conf = config.getGunConf(gunId, self.clientId, 1, self.mode)
            self.useGunEffect[gunId] = {
                "state": State.USING,
                "start_time": float('%.2f' % time.time()),
                "progress": [0, conf["duration"]]
            }
            self.updateFireOrEnergy(gunId, idx=1, absValue=1)
            self._setData(gunId)
            data = self.gunEffectData[gunId]
            self.setUseEffectTimer(conf["duration"])  # 启动结束的定时器
            if data:
                dataTmp = deepcopy(data)
                dataTmp.pop(0)
                dataTmp.append(conf["fire_count"])
                data = dataTmp
            msg = MsgPack()
            msg.setCmd("use_gun_effect")
            msg.setResult("userId", self.userId)
            msg.setResult("gunId", gunId)
            msg.setResult("code", 0)
            msg.setResult("progressData", data)
            msg.setResult("data", self.useGunEffect[gunId])
            GameMsg.sendMsg(msg, self.table.getBroadcastUids())
            return

    def addGunEffectEnergy(self, gunId, coin):
        """
        添加能量
        """
        if gunId in self.useGunEffect and self.useGunEffect[gunId]["state"] in [State.PREPARE, State.USING, State.PAUSE]:
            return
        conf = config.getGunConf(gunId, self.clientId, 1, self.mode)
        add_energy = coin * conf["percent"] / 100
        self.updateFireOrEnergy(gunId, 0, add_energy)
        return coin - add_energy

    def updateFireOrEnergy(self, gunId, idx=0, val=0, absValue=0, add=True):
        """
        更新开火次数
        :param gunId: 皮肤炮
        :param idx: 更新位置
        :param val: 更新的值
        :param abs_value: 赋值 0不赋值 1赋值
        :param add: 增加|减少
        """
        if gunId not in self.gunEffectData:
            listVal = self._getData(gunId)
        else:
            listVal = self.gunEffectData[gunId]
        if not listVal and ftlog.is_debug():
            ftlog.debug("updateFireOrEnergy", gunId, idx, val, absValue, add)
            return 0
        conf = config.getGunConf(gunId, self.clientId, 1, self.mode)
        if add:
            listVal[idx] += val
        else:
            listVal[idx] -= val
        if idx == 1:
            listVal[idx] = min(listVal[idx], conf["fire_count"])
        if absValue:
            listVal[idx] = val
        if ftlog.is_debug():
            ftlog.debug("updateFireOrEnergy", gunId, idx, val, absValue, listVal)
        self.gunEffectData[gunId] = listVal
        return listVal[idx]

    def useEffect(self, gunId=None):
        """
        使用狂暴
        """
        code = 0
        gunId = self.player.gunId if gunId is None else gunId
        if gunId not in self.gunEffectData:
            data = self._getData(gunId)
        else:
            data = self.gunEffectData[gunId]
        if not data:
            code = 1                                            # 此炮不存在狂暴效果
        conf = config.getGunConf(gunId, self.clientId, 1, self.mode)
        if data and data[1] < conf["fire_count"]:               # 开火次数没有达到要求
            code = 2
        if self.useGunEffect[gunId]["state"] != State.CAN_USE:
            code = 3
        if len(self.player.usingSkill) > 0:                     # 使用技能期间, 不能使用狂暴
            code = 4
        if code == 0:
            self.useGunEffect[gunId] = {
                "state": State.PREPARE,                         # 准备
                "start_time": 0,                                # float('%.2f' % time.time())
                "progress": [0, conf["duration"]]
            }
        if data:
            dataTmp = deepcopy(data)
            dataTmp.pop(0)
            dataTmp.append(conf["fire_count"])
            data = dataTmp

        msg = MsgPack()
        msg.setCmd("use_gun_effect")
        msg.setResult("userId", self.userId)
        msg.setResult("gunId", gunId)
        msg.setResult("code", code)
        msg.setResult("progressData", data)
        msg.setResult("data", self.useGunEffect[gunId])
        GameMsg.sendMsg(msg, self.table.getBroadcastUids())

    def getGunEffectInfo(self, gunId):
        """
        获取狂暴效果
        :param gunId:
        """
        if gunId not in self.useGunEffect:
            data_dict = {
                "state": State.NOT_EFFECT,
                "start_time": 0,
                "progress": [0, 0]
            }
        else:
            data_dict = self.useGunEffect[gunId]
        return data_dict

    def sendProgress(self, gunId=None, isSend=1):
        """
        发送是否开启狂暴技能效果|使用狂暴的数据
        """
        gunId = self.player.gunId if gunId is None else gunId
        if gunId not in self.gunEffectData:
            data = self._getData(gunId)
        else:
            data = self.gunEffectData[gunId]
        if not data:
            return
        conf = config.getGunConf(gunId, self.clientId, 1, self.mode)
        temp_data = deepcopy(data)
        temp_data.pop(0)
        temp_data.append(conf["fire_count"])
        msg = MsgPack()
        msg.setCmd("gun_effect_process")
        msg.setResult("userId", self.userId)
        msg.setResult("gunId", gunId)
        msg.setResult("progressData", temp_data)
        GameMsg.sendMsg(msg, [self.player.userId])
        if data[1] >= conf["fire_count"] and isSend:
            self.sendUseEffectState(gunId)

    def usingOrPause(self, gunId=None):
        """
        使用或者暂停
        """
        gunId = self.player.gunId if gunId is None else gunId
        if gunId not in self.useGunEffect:
            return
        data = self.useGunEffect[gunId]
        if data["state"] == State.PREPARE:
            data["state"] = State.CAN_USE
        elif data["state"] == State.CAN_USE:
            data["state"] = State.PREPARE
        if data["state"] == State.USING:
            data["state"] = State.PAUSE
            self.clearUeTimer()                                                         # 取消定时器
        else:
            if data["state"] == State.PAUSE:
                data["state"] = State.USING
                if float('%.2f' % time.time()) - data["start_time"] + data["progress"][0] < data["progress"][1]:
                    data["progress"][0] += float('%.2f' % time.time()) - data["start_time"]
                    data["progress"][0] = min(data["progress"][0], data["progress"][1])
                    self.setUseEffectTimer(data["progress"][1] - data["progress"][0])   # 设置结束的定时器
                data["start_time"] = float('%.2f' % time.time())
        self.sendUseEffectState(gunId)

    def sendUseEffectState(self, gunId=None):
        """
        发送是否开启狂暴技能效果|使用狂暴的数据
        """
        gunId = self.player.gunId if gunId is None else gunId
        if gunId not in self.gunEffectData:
            data_list = self._getData(gunId)
        else:
            data_list = self.gunEffectData[gunId]
        msg = MsgPack()
        msg.setCmd("gun_use_effect_state")
        msg.setResult("userId", self.userId)
        msg.setResult("gunId", gunId)
        if not data_list:
            msg.setResult("data", {"state": State.NOT_EFFECT, "start_time": 0, "progress": [0, 0]})
            GameMsg.sendMsg(msg, self.table.getBroadcastUids())
            return
        conf = config.getGunConf(gunId, self.clientId, 1, self.mode)
        if conf["fire_count"] <= 0:
            return
        if gunId not in self.useGunEffect:
            if data_list[1] >= conf["fire_count"]:
                self.useGunEffect[gunId] = {
                    "state": State.CAN_USE,
                    "start_time": 0,
                    "progress": [0, conf["duration"]]
                }
            else:
                self.useGunEffect[gunId] = {
                    "state": State.NOT_USE,
                    "start_time": 0,
                    "progress": [0, conf["duration"]]
                }
        else:
            data = self.useGunEffect[gunId]
            if data["state"] == State.NOT_USE and data_list[1] >= conf["fire_count"]:
                data["state"] = State.CAN_USE
            if data["state"] == State.USING or data["state"] == State.PAUSE:
                if float('%.2f' % time.time()) - data["start_time"] + data["progress"][0] < data["progress"][1]:
                    data["progress"][0] += float('%.2f' % time.time()) - data["start_time"]
                    data["progress"][0] = min(data["progress"][0], data["progress"][1])
                    data["start_time"] = float('%.2f' % time.time())
                else:
                    data["state"] = State.END
            if data["state"] == State.END:
                self.useGunEffect[gunId].update({
                    "state": State.END,
                    "start_time": 0,
                    "progress": [conf["duration"], conf["duration"]]
                })
        msg.setResult("data", self.useGunEffect[gunId])
        GameMsg.sendMsg(msg, self.table.getBroadcastUids())
        if self.useGunEffect[gunId]["state"] == State.END:
            self.clearUeTimer()
            del self.useGunEffect[gunId]