# -*- coding=utf-8 -*-
"""
Created by lichen on 2017/11/28.
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
from poker.entity.dao import daobase, gamedata
from poker.protocol import router
from poker.util import strutil
from poker.entity.biz import bireport
from hall.entity import hallvip, hallitem
from newfish.entity import config, util, module_tip
from newfish.entity.config import FISH_GAMEID, CLASSIC_MODE, MULTIPLE_MODE
from newfish.entity.redis_keys import GameData, UserData

INDEX_LEVEL = 0         # 第0位:皮肤炮熟练等级
INDEX_EXP = 1           # 第1位:皮肤炮经验值
INDEX_SKINID = 2        # 第2位:当前默认皮肤

SKIN_NOTOPEN = -1       # 皮肤未解锁
SKIN_NOTGOT = 0         # 未获得
SKIN_GOT = 1            # 获得


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
    skins = config.getGunConf(gunId, clientId, mode=mode).get("skins")
    if gunInfo[INDEX_SKINID] not in skins:
        ftlog.error("setGunData, not find skin, userId =", userId, "gunId =", gunId, "gunInfo =", gunInfo, "skins =", skins, "mode =", mode, "clientId =", clientId)
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
    ownGunSkinSkinsKey = GameData.ownGunSkinSkins
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
    ownGunSkinsKey = GameData.ownGunSkins               # 最近一次已拥有的皮肤炮列表
    gunSkinIdKey = GameData.gunSkinId if mode == CLASSIC_MODE else GameData.gunSkinId_m             # 用户当前皮肤炮ID
    promptedGunSkinsKey = GameData.promptedGunSkins     # 已发送了过期提示弹窗的皮肤炮
    ownGuns = gamedata.getGameAttrJson(userId, FISH_GAMEID, ownGunSkinsKey, [])
    currentGunIds = getGunIds(userId, mode)[1:]         # 玩家当前拥有的火炮ID
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
    installedGunId = refreshGunId(userId, mode)                         # 当前已装备的皮肤炮过期时，默认装备已拥有的最后一个皮肤炮
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    allGuns = getAllGuns(userId, mode)                                  # 获得所有皮肤炮数据
    lang = util.getLanguage(userId)
    ownGunSkinSkinsKey = GameData.ownGunSkinSkins
    ownGunSkinSkins = gamedata.getGameAttrJson(userId, FISH_GAMEID, ownGunSkinSkinsKey, [])     # 已拥有的皮肤炮皮肤
    for gunId in config.getAllGunIds(clientId, mode):
        if gunId not in allGuns:
            continue
        gun = {}
        gunLv = allGuns[gunId][INDEX_LEVEL]
        gunExp = allGuns[gunId][INDEX_EXP]
        skinId = allGuns[gunId][INDEX_SKINID]
        gunConf = config.getGunConf(gunId, clientId, gunLv, mode)
        gun["gunId"] = gunId
        gun["name"] = config.getMultiLangTextConf(gunConf["name"], lang=lang)
        gun["unlockDesc"] = gunConf["unlockDesc"]                       # 解锁描述
        if gunConf["unlockDesc"]:
            gun["unlockDesc"] = config.getMultiLangTextConf(gunConf["unlockDesc"], lang=lang) % gunConf.get("unlockValue", 0)
        gun["equipDesc"] = gunConf.get("equipDesc")                     # 装备描述
        if gunConf["equipDesc"]:
            gun["equipDesc"] = config.getMultiLangTextConf(gunConf["equipDesc"], lang=lang) % gunConf.get("equipValue", 0)
        gun["level"] = gunLv
        gun["exp"] = gunExp - (gunConf["totalExp"] - gunConf["exp"])    # 炮经验-上一级的经验
        gun["totalExp"] = gunConf["exp"]                                # 本级所需经验
        gun["expires"] = -1                                             # 有效期
        gun["state"] = 1
        gun["mode"] = 0
        gun["skinId"] = skinId if skinId in gunConf["skins"] else gunConf["skins"][0]   # 皮肤炮皮肤
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
        if gunConf["skins"][0] in ownGunSkinSkins:          # 永久获得
            if installedGunId == gunId:
                gun["state"] = 0
            if not unLock:                                  # 未解锁拥有(试用)
                gun["mode"] = 1
        elif item and not item.isDied(int(time.time())):    # 试用
            gun["expires"] = item.expiresTime               # 用道具购买有效期
            if installedGunId == gunId:
                gun["state"] = 0
            if not unLock:                                  # 未解锁拥有(试用)
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

    mo = MsgPack()
    mo.setCmd("guns_list")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("gameMode", mode)
    mo.setResult("guns", guns)
    router.sendToUser(mo, userId)


def sendGunInfoMsg(userId, mode):
    """
    发送普通炮信息
    """
    gunLevelKey = GameData.gunLevel if mode == CLASSIC_MODE else GameData.gunLevel_m
    gunLevel = gamedata.getGameAttrInt(userId, FISH_GAMEID, gunLevelKey)
    nextGunLevel = config.getNextGunLevel(gunLevel, mode)
    if nextGunLevel == -1:
        return
    nextGunLevelConf = config.getGunLevelConf(nextGunLevel, mode)
    mo = MsgPack()
    mo.setCmd("gun_info")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("gunLevel", gunLevel)                              # 当前火炮等级
    mo.setResult("nextGunLevel", nextGunLevelConf["gunLevel"])      # 下一个等级
    if "levelRewards" in nextGunLevelConf and nextGunLevelConf["levelRewards"] > 0:
        mo.setResult("levelUpRewards", nextGunLevelConf["levelRewards"])      # 金币数量
    mo.setResult("successRate", nextGunLevelConf["successRate"])
    mo.setResult("gameMode", mode)
    upgradeItemsConf = getUpgradeItemsConf(userId, nextGunLevel, mode=mode)
    if upgradeItemsConf:
        upgradeItems = {}
        for kindId, count in upgradeItemsConf.iteritems():
            if int(kindId) == config.PURPLE_CRYSTAL_KINDID:
                upgradeItems[kindId] = [util.balanceItem(userId, kindId) + util.balanceItem(userId, config.BIND_PURPLE_CRYSTAL_KINDID),  count]
            elif int(kindId) == config.YELLOW_CRYSTAL_KINDID:
                upgradeItems[kindId] = [util.balanceItem(userId, kindId) + util.balanceItem(userId, config.BIND_YELLOW_CRYSTAL_KINDID), count]
            else:
                upgradeItems[kindId] = [util.balanceItem(userId, kindId), count]
        mo.setResult("upgradeItems", upgradeItems)
    if nextGunLevelConf.get("protectItems"):
        protectItems = {}
        for kindId, count in nextGunLevelConf.get("protectItems").iteritems():
            protectItems[kindId] = [util.balanceItem(userId, kindId), count]
        mo.setResult("protectItems", protectItems)
    router.sendToUser(mo, userId)


def isEnough(userId, items):
    """
    道具数量是否满足升级所需数量
    """
    for kindId, count in items.iteritems():
        if (int(kindId) == config.PURPLE_CRYSTAL_KINDID and
                bindOrNotBindItem(userId, config.BIND_PURPLE_CRYSTAL_KINDID, config.PURPLE_CRYSTAL_KINDID, count)):
            continue
        elif (int(kindId) == config.YELLOW_CRYSTAL_KINDID and
                bindOrNotBindItem(userId, config.BIND_YELLOW_CRYSTAL_KINDID, config.YELLOW_CRYSTAL_KINDID, count)):
            continue
        if util.balanceItem(userId, kindId) < count:
            return False
    return True


def upgradeGun(userId, protect, mode, byGift=False, upToLevel=0):
    """
    升级普通炮
    """
    def consume(items, level):
        """消耗升级所需道具"""
        _consumeList = []
        for kindId, count in items.iteritems():
            if int(kindId) == config.PURPLE_CRYSTAL_KINDID:
                _consumeList.extend(consumeBindOrNotBindItem(userId, config.BIND_PURPLE_CRYSTAL_KINDID, config.PURPLE_CRYSTAL_KINDID, count))
            elif int(kindId) == config.YELLOW_CRYSTAL_KINDID:
                _consumeList.extend(consumeBindOrNotBindItem(userId, config.BIND_YELLOW_CRYSTAL_KINDID, config.YELLOW_CRYSTAL_KINDID, count))
            else:
                _consume = {"name": int(kindId), "count": count}
                _consumeList.append(_consume)
        util.consumeItems(userId, _consumeList, "ITEM_USE", level)

    gunLevelKey = GameData.gunLevel if mode == CLASSIC_MODE else GameData.gunLevel_m
    gunLevel, level = gamedata.getGameAttrs(userId, FISH_GAMEID, [gunLevelKey, GameData.level])
    if not gunLevel or gunLevel >= config.getMaxGunLevel(mode):
        return False
    nextGunLevel = config.getNextGunLevel(gunLevel, mode)
    if nextGunLevel == -1:
        ftlog.error("gunLevel error! userId =", userId, "gunLevel =", gunLevel, "mode =", mode)
        return False
    nextGunLevelConf = config.getGunLevelConf(nextGunLevel, mode)
    upgradeItemsConf = getUpgradeItemsConf(userId, nextGunLevel, mode=mode)
    returnRewards = None
    levelUpRewards = None
    if not byGift:
        if isEnough(userId, upgradeItemsConf):                              # 判断升级所需物品是否足够
            if nextGunLevelConf["successRate"] >= 10000:                    # 是否100%成功
                consume(upgradeItemsConf, level)                            # 消耗升级所需物品
                code = 0                                                    # 升级成功
            else:
                if protect:                                                 # 是否使用五彩水晶
                    if isEnough(userId, nextGunLevelConf["protectItems"]):  # 判断五彩水晶是否足够
                        consume(upgradeItemsConf, level)                    # 消耗升级所需物品
                        consume(nextGunLevelConf["protectItems"], level)    # 消耗五彩水晶
                        code = 0
                    else:
                        code = 99                                           # 五彩水晶物品不足
                else:
                    consume(upgradeItemsConf, level)                        # 消耗升级所需物品
                    randInt = random.randint(1, 10000)
                    if randInt <= nextGunLevelConf["successRate"]:
                        code = 0
                    else:
                        randInt = random.randint(1, 10000)
                        for item in nextGunLevelConf["returnItems"]:
                            if item["probb"][0] <= randInt <= item["probb"][1]:
                                returnRewards = [{"name": item["kindId"], "count": item["count"]}]
                                break
                        code = 1                                            # 升级失败，返还道具
        else:
            code = 99    # 升级所需物品不足
    else:
        if upToLevel > gunLevel:
            code = 0
        else:
            code = 1
    if code == 0:
        # level += 1
        # gunLevel += 1
        # gamedata.setGameAttrs(userId, FISH_GAMEID, [GameData.level, GameData.gunLevel], [level, gunLevel])
        # gunLevel += 1
        if "levelRewards" in nextGunLevelConf and nextGunLevelConf["levelRewards"] > 0:
            levelUpRewards = [{"name": config.CHIP_KINDID, "count": nextGunLevelConf["levelRewards"]}]
        gunLevel = nextGunLevel if not byGift else upToLevel
        gamedata.setGameAttr(userId, FISH_GAMEID, gunLevelKey, gunLevel)
        from newfish.game import TGFish
        from newfish.entity.event import GunLevelUpEvent
        event = GunLevelUpEvent(userId, FISH_GAMEID, level, gunLevel, mode)
        TGFish.getEventBus().publishEvent(event)
        bireport.reportGameEvent("BI_NFISH_GE_LEVEL_UP", userId, FISH_GAMEID, 0, 0, int(level), mode, 0, 0, [byGift, upToLevel, gunLevel], util.getClientId(userId))

    mo = MsgPack()
    mo.setCmd("gun_up")                                     # 升级普通炮
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("level", level)
    mo.setResult("gunLevel", gunLevel)
    mo.setResult("gameMode", mode)
    mo.setResult("code", code)
    if returnRewards:
        util.addRewards(userId, returnRewards, "ASSEMBLE_ITEM", level)
        mo.setResult("returnRewards", returnRewards)
    if levelUpRewards:
        util.addRewards(userId, levelUpRewards, "ASSEMBLE_ITEM", level)
        mo.setResult("levelUpRewards", levelUpRewards)
    router.sendToUser(mo, userId)
    sendGunInfoMsg(userId, mode)                            # 发送普通炮信息
    return code == 0


def changeGun(userId, gunId, mode):
    """
    切换火炮
    """
    isIn, roomId, tableId, seatId = util.isInFishTable(userId)
    if isIn:
        mo = MsgPack()
        mo.setCmd("fish_table_call")
        mo.setParam("action", "chg_gun")
        mo.setParam("gameId", FISH_GAMEID)
        mo.setParam("clientId", util.getClientId(userId))
        mo.setParam("userId", userId)
        mo.setParam("roomId", roomId)
        mo.setParam("tableId", tableId)
        mo.setParam("seatId", seatId)
        mo.setParam("gunId", gunId)
        mo.setParam("gameMode", mode)
        router.sendTableServer(mo, roomId)
    else:
        userGunIds = getGunIds(userId, mode)
        mo = MsgPack()
        mo.setCmd("chg_gun")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("gameMode", mode)
        if gunId not in userGunIds:
            mo.setResult("reason", 1)
        elif not isCanEquip(userId, gunId, mode):
            mo.setResult("reason", 2)
        else:
            gunSkinIdKey = GameData.gunSkinId if mode == CLASSIC_MODE else GameData.gunSkinId_m
            gamedata.setGameAttr(userId, FISH_GAMEID, gunSkinIdKey, gunId)
            mo.setResult("gunId", gunId)
            mo.setResult("reason", 0)
            sendGunListMsg(userId, mode)
        router.sendToUser(mo, userId)


def changeGunSkin(userId, gunId, skinId, mode):
    """
    切换火炮皮肤
    """
    ftlog.debug("changeGunSkin, userId =", userId, "gunId =", gunId, "skinId =", skinId, "mode =", mode)
    mo = MsgPack()
    mo.setCmd("gun_change_skin")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("gunId", gunId)
    mo.setResult("skinId", skinId)
    mo.setResult("gameMode", mode)
    clientId = util.getClientId(userId)
    skins = config.getGunConf(gunId, clientId, mode=mode).get("skins")
    ownGunSkinSkinsKey = GameData.ownGunSkinSkins
    ownGunSkinSkins = gamedata.getGameAttrJson(userId, FISH_GAMEID, ownGunSkinSkinsKey, [])
    if skinId not in ownGunSkinSkins and skinId != skins[0]:
        mo.setResult("code", 1)  # 未获得
        router.sendToUser(mo, userId)
        return False
    if skinId not in skins:
        mo.setResult("code", 2)  # 皮肤不在该火炮下属的皮肤列表中
        router.sendToUser(mo, userId)
        return False
    equipGunSkin(userId, gunId, skinId, mode)
    mo.setResult("code", 0)
    router.sendToUser(mo, userId)
    return True


def composeGunSkin(userId, gunId, skinId, mode):
    """
    合成火炮皮肤
    """
    clientId = util.getClientId(userId)
    ftlog.debug("composeGunSkin, userId =", userId, "gunId =", gunId, "skinId =", skinId, "clientId =", clientId, "mode =", mode)
    skinConf = config.getGunSkinConf(skinId, clientId, mode)
    mo = MsgPack()
    mo.setCmd("gun_compose_skin")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("gunId", gunId)
    mo.setResult("skinId", skinId)
    mo.setResult("gameMode", mode)
    skins = config.getGunConf(gunId, clientId, mode=mode).get("skins")
    if skinId not in skins:
        mo.setResult("code", 99)  # 数据不对
        router.sendToUser(mo, userId)
        return False
    if not skinConf:
        mo.setResult("code", 99)  # 数据不对
        router.sendToUser(mo, userId)
        return False
    surplusCount = util.balanceItem(userId, skinConf["kindId"])
    ownGunSkinSkinsKey = GameData.ownGunSkinSkins
    ownGunSkinSkins = gamedata.getGameAttrJson(userId, FISH_GAMEID, ownGunSkinSkinsKey, [])
    if surplusCount < skinConf["consumeCount"]:
        mo.setResult("code", 1)  # 资源不足
        return False
    elif skinId in ownGunSkinSkins:
        mo.setResult("code", 2)  # 已经合成
        return False
    else:
        # 合成消耗皮肤碎片
        _consume = [{"name": skinConf["kindId"], "count": abs(skinConf["consumeCount"])}]
        util.consumeItems(userId, _consume, "ITEM_USE", int(gunId), mode)
        addEquipGunSkinSkin(userId, skinId, clientId, False)
        mo.setResult("code", 0)
        router.sendToUser(mo, userId)
    return True


def addGunSkin(userId, skinId, mode):
    """
    添加火炮皮肤
    """
    ownGunSkinSkinsKey = GameData.ownGunSkinSkins
    ownGunSkinSkins = gamedata.getGameAttrJson(userId, FISH_GAMEID, ownGunSkinSkinsKey, [])
    if skinId not in ownGunSkinSkins:
        ownGunSkinSkins.append(skinId)
        gamedata.setGameAttr(userId, FISH_GAMEID, ownGunSkinSkinsKey, json.dumps(ownGunSkinSkins))


def equipGunSkin(userId, gunId, skinId, mode):
    """
    装备火炮皮肤
    """
    gunData = getGunData(userId, gunId, mode)
    gunData[INDEX_SKINID] = skinId
    setGunData(userId, gunId, gunData, mode)


def _isUnlockGun(userId, gunConf, mode):
    from newfish.entity.honor import honor_system
    _isUnlocked = False
    vipLevel = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
    gunLevelVal = util.getGunLevelVal(userId, mode)
    if not gunConf:
        return _isUnlocked
    if gunConf.get("gunId") == 0:
        _isUnlocked = True
    elif gunConf.get("unlockType") == 0:
        _isUnlocked = True
    elif gunConf.get("unlockType") == 1 and vipLevel >= gunConf["unlockValue"]:
        _isUnlocked = True
    elif gunConf.get("unlockType") == 2 and gunConf["unlockValue"] in honor_system.getOwnedHonors(userId):
        _isUnlocked = True
    elif gunConf.get("unlockType") == 3 and gunLevelVal >= gunConf["unlockValue"]:
        _isUnlocked = True
    return _isUnlocked


def isUnlock(userId, gunId, gunConf, mode):
    """
    皮肤炮是否已解锁
    """
    # 先判断当前模式是否解锁
    _isUnlocked = _isUnlockGun(userId, gunConf, mode)
    # 如果当前模式未达到解锁条件则检测另一个模式是否已达到解锁条件.（经典/千炮）
    if not _isUnlocked:
        clientId = util.getClientId(userId)
        _mode = MULTIPLE_MODE if mode == CLASSIC_MODE else CLASSIC_MODE
        _gunConf = config.getGunConf(gunId, clientId, mode=_mode)
        _isUnlocked = _isUnlockGun(userId, _gunConf, _mode)
    return _isUnlocked


def isCanEquip(userId, gunId, mode):
    """
    皮肤炮是否可以装配（条件同解锁,但是只检测当前模式是否可以装备）
    """
    clientId = util.getClientId(userId)
    gunConf = config.getGunConf(gunId, clientId, 1, mode)
    _isCanEquip = False
    if gunConf:
        from newfish.entity.honor import honor_system
        vipLevel = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
        gunLevelVal = util.getGunLevelVal(userId, mode)
        if gunId == 0:
            _isCanEquip = True
        elif gunConf["equipType"] == 0:
            _isCanEquip = True
        elif gunConf["equipType"] == 1 and vipLevel >= gunConf["equipValue"]:
            _isCanEquip = True
        elif gunConf["equipType"] == 2 and gunConf["equipValue"] in honor_system.getOwnedHonors(userId):
            _isCanEquip = True
        elif gunConf["equipType"] == 3 and gunLevelVal >= gunConf["equipValue"]:
            _isCanEquip = True
    return _isCanEquip


# def incrGunPool(userId, gunId, coin):
#     """
#     增减皮肤炮奖池(已废弃)
#     """
#     isIn, roomId, tableId, seatId = util.isInFishTable(userId)
#     if isIn:
#         mo = MsgPack()
#         mo.setCmd("table_call")
#         mo.setParam("action", "guns_pool")
#         mo.setParam("gameId", FISH_GAMEID)
#         mo.setParam("clientId", util.getClientId(userId))
#         mo.setParam("userId", userId)
#         mo.setParam("roomId", roomId)
#         mo.setParam("tableId", tableId)
#         mo.setParam("seatId", seatId)
#         mo.setParam("gunId", gunId)
#         mo.setParam("coin", int(coin))
#         router.sendTableServer(mo, roomId)
#     else:
#         gunPool = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.gunSkinPool, {})
#         gunPool.setdefault(str(gunId), 0)
#         gunPool[str(gunId)] += int(coin)
#         gamedata.setGameAttr(userId, FISH_GAMEID, GameData.gunSkinPool, json.dumps(gunPool))


def checkGunUpgrade(userId):
    """
    检查普通炮能否升级
    """
    for mode in config.GAME_MODES:
        gunLevelKey = GameData.gunLevel if mode == CLASSIC_MODE else GameData.gunLevel_m
        gunLevel = gamedata.getGameAttrInt(userId, FISH_GAMEID, gunLevelKey)
        if gunLevel >= config.getMaxGunLevel(mode):
            continue
        nextGunLevel = config.getNextGunLevel(gunLevel, mode)
        upgradeItemsConf = getUpgradeItemsConf(userId, nextGunLevel, mode=mode)
        if isEnough(userId, upgradeItemsConf):                                                  # 判断升级所需物品是否足够
            module_tip.addModuleTipEvent(userId, "upgun", 0)                                    # 普通炮升级小红点
        else:
            module_tip.resetModuleTipEvent(userId, "upgun")


def bindOrNotBindItem(userId, bindKindId, kindId, count):
    """
    绑定与非绑定是否足够
    """
    if util.balanceItem(userId, bindKindId) >= count:
        return True
    elif util.balanceItem(userId, bindKindId) + util.balanceItem(userId, kindId) >= count:
        return True
    elif util.balanceItem(userId, kindId) >= count:
        return True
    return False


def consumeBindOrNotBindItem(userId, bindKindId, kindId, count):
    """获取消耗的数据"""
    consumeList = []
    if util.balanceItem(userId, bindKindId) >= count:
        consume = {"name": int(bindKindId), "count": count}
    elif util.balanceItem(userId, bindKindId) + util.balanceItem(userId, kindId) >= count:
        bind_count = util.balanceItem(userId, bindKindId)
        count = count - bind_count
        consume1 = {"name": int(bindKindId), "count": bind_count}
        consumeList.append(consume1)
        consume = {"name": int(kindId), "count": count}
    else:
        consume = {"name": int(kindId), "count": count}
    consumeList.append(consume)
    return consumeList


def getUpgradeItemsConf(userId, gunLevel, mode=CLASSIC_MODE):
    """
    获取升级材料配置
    """
    upgradeItems = config.getGunLevelConf(gunLevel, mode).get("upgradeItems", {})
    return upgradeItems


def addEquipGunSkinSkin(userId, skinId, clientId, isChangeGun=True):
    """
    获得并装备皮肤炮皮肤
    """
    ret = False
    modeList = [config.CLASSIC_MODE, config.MULTIPLE_MODE]
    for mode in modeList:
        skinConf = config.getGunSkinConf(skinId, clientId, mode)
        if skinConf:
            ret = True
            # 添加并装备皮肤
            gunId = skinConf["gunId"]
            addGunSkin(userId, skinId, mode)
            equipGunSkin(userId, gunId, skinId, mode)
            # 切换为改皮肤对应的皮肤炮.
            if isChangeGun:
                changeGun(userId, gunId, mode)
    return ret


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
    ownGunSkinsKey = GameData.ownGunSkins
    promptedGunSkinsKey = GameData.promptedGunSkins
    ownGuns = gamedata.getGameAttrJson(event.userId, FISH_GAMEID, ownGunSkinsKey, [])
    if gunId not in ownGuns:
        ownGuns.append(gunId)
        gamedata.setGameAttr(event.userId, FISH_GAMEID, ownGunSkinsKey, json.dumps(ownGuns))
    promptedGuns = gamedata.getGameAttrJson(event.userId, FISH_GAMEID, promptedGunSkinsKey, [])
    if gunId in promptedGuns:
        promptedGuns.remove(gunId)
        gamedata.setGameAttr(event.userId, FISH_GAMEID, promptedGunSkinsKey, json.dumps(promptedGuns))
        # clientId = util.getClientId(event.userId)
        # gunConf = config.getGunConf(gunId, clientId, mode=mode)
        # if gunConf and gunConf.get("effectType", 0) == 2:   # 增加皮肤炮奖池
        #     coin = gunConf.get("unitPrice", 0) * event.count
        #     if event.type == 1:
        #         coin *= 0.5
        #     elif event.type == 2:
        #         coin *= 0.3
        #     else:
        #         coin *= 0.15
        # incrGunPool(event.userId, gunId, coin)


def reportOwnGunsAndGunSkins(event):
    """报告拥有的火炮和火炮皮肤"""
    ownGuns = gamedata.getGameAttrJson(event.userId, FISH_GAMEID, GameData.ownGunSkins, [])
    bireport.reportGameEvent("BI_NFISH_GE_ADD_GUN_ID", event.userId, FISH_GAMEID, 0, 0, 0, 0, 0, 0, ownGuns,
                             util.getClientId(event.userId))
    ownGunSkinSkinsKey = GameData.ownGunSkinSkins
    ownGunSkinSkins = gamedata.getGameAttrJson(event.userId, FISH_GAMEID, ownGunSkinSkinsKey, [])
    bireport.reportGameEvent("BI_NFISH_GE_ADD_GUN_SKIN", event.userId, FISH_GAMEID, 0, 0, 0, 0, 0, 0, ownGunSkinSkins,
                             util.getClientId(event.userId))


def _triggerUserLoginEvent(event):
    """
    用户登录游戏
    """
    initGun(event.userId)                       # 初始化炮的信息
    checkGunUpgrade(event.userId)
    reportOwnGunsAndGunSkins(event)


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
