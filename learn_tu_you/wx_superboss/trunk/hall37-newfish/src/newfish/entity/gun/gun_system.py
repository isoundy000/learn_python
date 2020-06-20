#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/4

import time
import json
import random

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.entity.dao import daobase, gamedata, userchip
from poker.protocol import router
from poker.util import strutil
from poker.entity.biz import bireport
from hall.entity import hallvip, hallitem
from newfish.entity import config, util, module_tip
from newfish.entity.config import FISH_GAMEID, CLASSIC_MODE, MULTIPLE_MODE
from newfish.entity.redis_keys import GameData, UserData
from newfish.entity import store


INDEX_LEVEL = 0         # 第0位:皮肤炮熟练等级
INDEX_EXP = 1           # 第1位:皮肤炮经验值
INDEX_SKINID = 2        # 第2位:当前默认皮肤

SKIN_NOTOPEN = -1
SKIN_NOTGOT = 0
SKIN_GOT = 1


def _buildUserGunKey(userId, mode):
    """
    炮数据存取key
    """
    if mode == CLASSIC_MODE:
        return UserData.gunskin % (FISH_GAMEID, userId)
    else:
        return UserData.gunskin_m % (FISH_GAMEID, userId)


def initGun(userId):
    """
    初始化炮数据
    """
    clientId = util.getClientId(userId)
    for mode in config.GAME_MODES:
        for gunId in config.getAllGunIds(clientId, mode):
            updateGun(userId, gunId, mode)
            gunData = getGunData(userId, gunId, mode)
            skinId = gunData[INDEX_SKINID]
            skins = config.getGunConf(gunId, clientId, mode=mode).get("skins")      # 配置炮的皮肤
            if skinId not in skins:
                gunData[INDEX_SKINID] = skins[0]
                setGunData(userId, gunId, gunData, mode)


def updateGun(userId, gunId, mode):
    """
    更新新增炮数据
    """
    clientId = util.getClientId(userId)
    assert int(gunId) in config.getAllGunIds(clientId, mode)
    gunConf = config.getGunConf(gunId, clientId, mode=mode)
    gunInfo = [1, 0, gunConf["skins"][0]]                       # 皮肤炮熟练等级 | 经验 | 默认皮肤
    daobase.executeUserCmd(userId, "HSETNX", _buildUserGunKey(userId, mode), str(gunId), json.dumps(gunInfo))


def setGunData(userId, gunId, gunInfo, mode):
    """
    存储单个炮数据
    """
    clientId = util.getClientId(userId)
    assert int(gunId) in config.getAllGunIds(clientId, mode)
    assert isinstance(gunInfo, list) and len(gunInfo) == 3
    # assert gunInfo[INDEX_SKINID] in config.getGunConf(gunId, clientId).get("skins")
    skins = config.getGunConf(gunId, clientId, mode=mode).get("skins")
    if gunInfo[INDEX_SKINID] not in skins:
        ftlog.error("setGunData, not find skin, userId =", userId, "gunId =", gunId, "gunInfo =", gunInfo,
                    "skins =", skins, "mode =", mode, "clientId =", clientId)
        gunInfo[INDEX_SKINID] = skins[0]
    daobase.executeUserCmd(userId, "HSET", _buildUserGunKey(userId, mode), str(gunId), json.dumps(gunInfo))


def getGunData(userId, gunId, mode):
    """
    获得单个皮肤炮数据
    """
    clientId = util.getClientId(userId)
    assert int(gunId) in config.getAllGunIds(clientId, mode)
    gunConf = config.getGunConf(gunId, clientId, mode=mode)
    value = daobase.executeUserCmd(userId, "HGET", _buildUserGunKey(userId, mode), str(gunId))
    if value:
        value = strutil.loads(value, False, True)
        if len(value) <= 2:
            value.append(gunConf["skins"][0])                   # 默认皮肤
        return value
    # 获取初始化的值
    return [1, 0, gunConf["skins"][0]]


def getAllGuns(userId, mode):
    pass


def getGunIds(userId, mode):
    """
    玩家当前拥有的火炮ID
    """
    pass


def refreshGunId(userId, mode):
    """
    当前已装备的皮肤炮过期时，默认装备已拥有的最后一个皮肤炮
    """


def sendExpiredGunMsg(userId, mode):
    """
    返回火炮皮肤过期提示
    """


def sendGunListMsg(userId, mode):
    """
    发送火炮列表消息
    """
    pass


def sendGunInfoMsg(userId, mode):
    """
    发送普通炮信息
    """


def upgradeGun(userId, protect, mode):
    """
    升级普通炮
    """


def changeGun(userId, gunId, mode):
    """
    切换火炮
    """


def changeGunSkin(userId, gunId, skinId, mode):
    """
    切换火炮皮肤
    """

def composeGunSkin(userId, gunId, skinId, mode):
    """
    合成火炮皮肤
    """


def addGunSkin(userId, skinId, mode):
    """
    添加火炮皮肤
    """


def equipGunSkin(userId, gunId, skinId, mode):
    """
    装备火炮皮肤
    """

def isUnlock(userId, gunId, gunConf, mode):
    """
    皮肤炮是否已解锁
    """

def isCanEquip(userId, gunId, mode):
    """
    皮肤炮是否可以装配（条件同解锁,但是只检测当前模式是否可以装备）
    """

def incrGunPool(userId, gunId, coin):
    """
    增减皮肤炮奖池(暂已废弃)
    """


def checkGunUpgrade(userId):
    """
    检查普通炮能否升级
    """

def getUpgradeItemsConf(userId, gunLevel, upgradeGunTestMode="", mode=CLASSIC_MODE):
    """
    获取升级材料配置
    """

def addEquipGunSkinSkin(userId, skinId, clientId, isChangeGun=True):
    """
    获得并装备皮肤炮皮肤
    """


def _triggerGunItemChangeEvent(event):
    """
    普通炮升级所需物品发生改变
    """
    checkGunUpgrade(event.userId)


def _triggerAddGunSkinEvent(event):
    """
    获得皮肤炮道具
    """
    # 添加新得到的皮肤炮，同时从过期提示中移除它
    gunId = event.gunId
    mode = event.mode



def _triggerUserLoginEvent(event):
    """
    用户登录游戏
    """
    initGun(event.userId)               # 初始化炮的信息
    checkGunUpgrade(event.userId)


_inited = False


def initialize():
    ftlog.debug("newfish gun_system initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from poker.entity.events.tyevent import EventUserLogin
        from newfish.game import TGFish
        from newfish.entity.event import AddGunSkinEvent, GunItemCountChangeEvent
        TGFish.getEventBus().subscribe(AddGunSkinEvent, _triggerAddGunSkinEvent)
        TGFish.getEventBus().subscribe(GunItemCountChangeEvent, _triggerGunItemChangeEvent)
        TGFish.getEventBus().subscribe(EventUserLogin, _triggerUserLoginEvent)
    ftlog.debug("newfish gun_system initialize end")