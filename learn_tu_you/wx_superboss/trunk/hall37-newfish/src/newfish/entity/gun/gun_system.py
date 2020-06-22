#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/4
"""
0 默认炮
1288: 飓风 1等级 0经验 1352默认皮肤
1165: 霜冻
1166: 炎龙
1167: 魅影
1289: 光辉
1290: 暮刃
"""
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

SKIN_NOTOPEN = -1       # 皮肤未解锁
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
    """
    获得所有皮肤炮数据
    """
    clientId = util.getClientId(userId)
    assert isinstance(userId, int) and userId > 0
    _key = _buildUserGunKey(userId, mode)
    value = daobase.executeUserCmd(userId, "HGETALL", _key)
    if value:
        gunInfos = {}
        savaData = []
        for index in xrange(0, len(value), 2):
            gunId = value[index]
            if gunId in config.getAllGunIds(clientId, mode):
                gunData = strutil.loads(value[index + 1], False, True)
                if len(gunData) <= 2:
                    gunConfig = config.getGunConf(gunId, clientId, gunData[INDEX_LEVEL], mode)
                    gunData.append(gunConfig["skins"][0])
                    savaData.append(gunId)
                    savaData.append(strutil.dumps(gunData))
                gunInfos[gunId] = gunData

        if savaData:
            daobase.executeUserCmd(userId, "HMSET", _key, *savaData)
        return gunInfos
    return {}


def getGunIds(userId, mode):
    """
    玩家当前拥有的火炮ID
    """
    clientId = util.getClientId(userId)
    gunIds = [0]
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    ownGunSkinSkinsKey = GameData.ownGunSkinSkins  # if mode == CLASSIC_MODE else GameData.ownGunSkinSkins_m
    ownGunSkinSkins = gamedata.getGameAttrJson(userId, FISH_GAMEID, ownGunSkinSkinsKey, [])
    for kindId in config.getAllGunIds(clientId, mode):
        item = userBag.getItemByKindId(kindId)
        gunConf = config.getGunConf(kindId, clientId, mode=mode)
        if gunConf["skins"][0] in ownGunSkinSkins:          # 是否拥有皮肤炮默认永久皮肤
            gunIds.append(kindId)
        elif item and not item.isDied(int(time.time())):    # 皮肤炮是否过期   没过期
            gunIds.append(kindId)
    return gunIds


def refreshGunId(userId, mode):
    """
    当前已装备的皮肤炮过期时，默认装备已拥有的最后一个皮肤炮
    """
    userGunIds = getGunIds(userId, mode)
    gunSkinIdKey = GameData.gunSkinId if mode == CLASSIC_MODE else GameData.gunSkinId_m
    gunId = gamedata.getGameAttr(userId, FISH_GAMEID, gunSkinIdKey)
    if gunId not in userGunIds:
        gunId = userGunIds[-1]
        gamedata.setGameAttr(userId, FISH_GAMEID, gunSkinIdKey, gunId)
    return gunId


def sendExpiredGunMsg(userId, mode):
    """
    返回火炮皮肤过期提示
    """
    ownGunSkinsKey = GameData.ownGunSkins  # if mode == CLASSIC_MODE else GameData.ownGunSkins_m
    gunSkinIdKey = GameData.gunSkinId if mode == CLASSIC_MODE else GameData.gunSkinId_m
    promptedGunSkinsKey = GameData.promptedGunSkins  # if mode == CLASSIC_MODE else GameData.promptedGunSkins_m
    ownGuns = gamedata.getGameAttrJson(userId, FISH_GAMEID, ownGunSkinsKey, [])
    currentGunIds = getGunIds(userId, mode)[1:]
    clientId = util.getClientId(userId)
    allGunIds = config.getAllGunIds(clientId, mode)
    for idx in range(len(ownGuns) - 1, -1, -1):
        if ownGuns[idx] not in allGunIds:
            ownGuns.pop(idx)
    # 当前已过期的皮肤 = 最近一次已拥有皮肤炮 - 当前已拥有皮肤炮
    expiredGuns = list(set(ownGuns) - set(currentGunIds))
    if expiredGuns:
        gunId = gamedata.getGameAttr(userId, FISH_GAMEID, gunSkinIdKey)
        if gunId in expiredGuns:
            expiredGun = gunId
        else:
            expiredGun = expiredGuns[-1]
        gunIds1 = getGunIds(userId, CLASSIC_MODE)[1:]
        gunIds2 = getGunIds(userId, MULTIPLE_MODE)[1:]
        gunIds1.extend(gunIds2)
        gamedata.setGameAttr(userId, FISH_GAMEID, ownGunSkinsKey, json.dumps(list(set(gunIds1))))
        promptedGuns = gamedata.getGameAttrJson(userId, FISH_GAMEID, promptedGunSkinsKey, [])
        if expiredGun not in promptedGuns:
            promptedGuns.append(expiredGun)
            gamedata.setGameAttr(userId, FISH_GAMEID, promptedGunSkinsKey, json.dumps(promptedGuns))
            mo = MsgPack()
            mo.setCmd("expired_gun")
            mo.setResult("gameId", FISH_GAMEID)
            mo.setResult("userId", userId)
            mo.setResult("gunId", expiredGun)
            mo.setResult("gameMode", mode)
            router.sendToUser(mo, userId)


def sendGunListMsg(userId, mode):
    """
    发送火炮列表消息
    """
    clientId = util.getClientId(userId)
    guns = []
    installedGunId = refreshGunId(userId, mode)
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    allGuns = getAllGuns(userId, mode)
    lang = util.getLanguage(userId)
    ownGunSkinSkinsKey = GameData.ownGunSkinSkins  # if mode == CLASSIC_MODE else GameData.ownGunSkinSkins_m
    ownGunSkinSkins = gamedata.getGameAttrJson(userId, FISH_GAMEID, ownGunSkinSkinsKey, [])
    for gunId in config.getAllGunIds(clientId, mode):
        if gunId not in allGuns:
            continue
        gun = {}
        gunLv = allGuns[gunId][INDEX_LEVEL]
        gunExp = allGuns[gunId][INDEX_EXP]
        skinId = allGuns[gunId][INDEX_SKINID]
        gunConf = config.getGunConf(gunId, clientId, gunLv, mode)
        gun["gunId"] = gunId
        # gun["name"] = gunConf["name"]
        gun["name"] = config.getMultiLangTextConf(gunConf["name"], lang=lang)
        gun["unlockDesc"] = gunConf["unlockDesc"]
        if gunConf["unlockDesc"]:
            gun["unlockDesc"] = config.getMultiLangTextConf(gunConf["unlockDesc"], lang=lang) % gunConf.get("unlockValue", 0)
        gun["equipDesc"] = gunConf.get("equipDesc")
        if gunConf["equipDesc"]:
            gun["equipDesc"] = config.getMultiLangTextConf(gunConf["equipDesc"], lang=lang) % gunConf.get("equipValue", 0)
        gun["level"] = gunLv
        gun["exp"] = gunExp - (gunConf["totalExp"] - gunConf["exp"])
        gun["totalExp"] = gunConf["exp"]
        gun["expires"] = -1
        gun["state"] = 1
        gun["mode"] = 0
        gun["skinId"] = skinId if skinId in gunConf["skins"] else gunConf["skins"][0]
        gun["skins"] = []
        for skinId_ in gunConf["skins"]:
            skinState = SKIN_NOTOPEN
            if skinId_ != -1 and config.getGunSkinConf(skinId_, clientId, mode):
                skinState = SKIN_GOT if (skinId_ in ownGunSkinSkins) else SKIN_NOTGOT
            elif skinId_ == 0:
                skinState = SKIN_GOT
            skinData = {"skinId": skinId_, "state": skinState}
            gun["skins"].append(skinData)
        unLock = isUnlock(userId, gunId, gunConf, mode)
        item = userBag.getItemByKindId(gunId)
        if gunConf["skins"][0] in ownGunSkinSkins:  # 永久获得
            if installedGunId == gunId:
                gun["state"] = 0
            if not unLock:  # 未解锁拥有(试用)
                gun["mode"] = 1
        elif item and not item.isDied(int(time.time())):  # 试用
            gun["expires"] = item.expiresTime
            if installedGunId == gunId:
                gun["state"] = 0
            if not unLock:  # 未解锁拥有(试用)
                gun["mode"] = 1
        elif gunId == 0:
            if installedGunId == gunId:
                gun["state"] = 0
        else:
            gun["expires"] = 0
            gun["state"] = 2
            if not unLock:
                gun["state"] = 3
        gun["equipState"] = 1 if isCanEquip(userId, gunId, mode) else 0
        guns.append(gun)


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