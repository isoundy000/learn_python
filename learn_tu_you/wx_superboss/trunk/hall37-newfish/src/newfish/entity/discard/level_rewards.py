# -*- coding=utf-8 -*-
"""
等级奖励模块
"""
# @Author  : Kangxiaopeng
# @Time    : 2019/6/18

import json

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.dao import userchip, userdata, gamedata, daobase
from newfish.entity import config, util, module_tip
from newfish.entity.chest import chest_system
from newfish.entity.redis_keys import GameData


def getLevelRewardsData(userId):
    """
    获取等级奖励数据
    """
    clientId = util.getClientId(userId)
    userLevel = util.getUserLevel(userId)
    levels = gamedata.getGameAttrJson(userId, config.FISH_GAMEID, GameData.levelRewards, [])
    levelRewards = config.getLevelRewards(clientId)
    _level = userLevel
    _rewards = []
    if util.isFinishAllNewbieTask(userId):
        isIn, roomId, _, _ = util.isInFishTable(userId)
        if isIn and util.getRoomTypeName(roomId) in config.NORMAL_ROOM_TYPE:
            lang = util.getLanguage(userId)
            sortedLevelRewards = sorted(levelRewards.items(), key=lambda v: int(v[0]))
            for item in sortedLevelRewards:
                level, val = item
                level = int(level)
                if val and level not in levels:
                    _level = level
                    for _r in val.get("rewards", []):
                        itemId = _r["name"]
                        desId = _r.get("des")
                        if desId:
                            des = config.getMultiLangTextConf(str(desId), lang=lang)
                        else:
                            des = ""
                        if util.isChestRewardId(itemId):
                            _rewards.append({"name": itemId, "count": _r["count"], "des": des, "info": chest_system.getChestInfo(itemId)})
                        else:
                            _rewards.append({"name": itemId, "count": _r["count"], "des": des, "info": {}})
                    if level <= userLevel:
                        module_tip.addModuleTipEvent(userId, "levelrewards", _level)
                    break

    mo = MsgPack()
    mo.setCmd("levelRewardsData")
    mo.setResult("gameId", config.FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("level", _level)
    mo.setResult("rewards", _rewards)
    router.sendToUser(mo, userId)
    ftlog.debug("level_rewards, userId =", userId, "userLevel =", userLevel, "level =", _level, "rewards =", _rewards)


def getLevelRewards(userId, level):
    """
    领取等级奖励
    """
    clientId = util.getClientId(userId)
    module_tip.cancelModuleTipEvent(userId, "levelrewards", level)
    code = 1
    userLevel = util.getUserLevel(userId)
    levels = gamedata.getGameAttrJson(userId, config.FISH_GAMEID, GameData.levelRewards, [])
    levelRewards = config.getLevelRewards(clientId, level)
    rewards = []
    chestRewards = {}
    if levelRewards and level not in levels and level <= userLevel:
        for val in levelRewards.get("rewards", []):
            itemId = val["name"]
            if util.isChestRewardId(itemId):
                chestRewards["chestId"] = itemId
                chestRewards["rewards"] = chest_system.getChestRewards(userId, itemId)
                code = chest_system.deliveryChestRewards(userId, itemId, chestRewards["rewards"], "BI_NFISH_GET_LEVEL_REWARDS")
            else:
                r = [{"name": val["name"], "count": val["count"]}]
                rewards.extend(r)
                code = util.addRewards(userId, r, "BI_NFISH_GET_LEVEL_REWARDS", level)
        if levelRewards.get("rechargeBonus", 0) > 0:
            util.incrUserRechargeBonus(userId, levelRewards.get("rechargeBonus", 0))
        levels.append(level)
        gamedata.setGameAttr(userId, config.FISH_GAMEID, GameData.levelRewards, json.dumps(levels))

    mo = MsgPack()
    mo.setCmd("levelRewards")
    mo.setResult("gameId", config.FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("code", code)
    mo.setResult("level", level)
    mo.setResult("rewards", rewards)
    mo.setResult("chestRewards", chestRewards)
    router.sendToUser(mo, userId)
    ftlog.debug("level_rewards, userId =", userId, "code =", code, "level =", level, "userLevel =",
                userLevel, "rewards =", rewards, "levels =", levels)

    getLevelRewardsData(userId)


def _triggerLevelUpEvent(event):
    userId = event.userId
    userLevel = event.level
    levels = gamedata.getGameAttrJson(userId, config.FISH_GAMEID, GameData.levelRewards, [])
    clientId = util.getClientId(userId)
    levelRewards = config.getLevelRewards(clientId)
    for level, rewards in levelRewards.iteritems():
        if rewards and level not in levels:
            if level <= userLevel:
                module_tip.addModuleTipEvent(userId, "levelRewards", level)
            break


def _triggerNewSkillEvent(event):
    if event.eventId != "BI_NFISH_GET_LEVEL_REWARDS":
        return
    userId = event.userId
    skillId = event.skillId
    clientId = util.getClientId(userId)
    isIn, roomId, tableId, seatId = util.isInFishTable(userId)
    if not isIn:
        return
    mo = MsgPack()
    mo.setCmd("table_call")
    mo.setParam("action", "skill_install")
    mo.setParam("gameId", config.FISH_GAMEID)
    mo.setParam("clientId", clientId)
    mo.setParam("userId", userId)
    mo.setParam("roomId", roomId)
    mo.setParam("tableId", tableId)
    mo.setParam("seatId", seatId)
    mo.setParam("skillId", skillId)
    mo.setParam("install", 1)
    mo.setParam("ignoreFailMsg", True)
    router.sendTableServer(mo, roomId)
    ftlog.debug("level_rewards, userId =", userId, "skillId =", skillId)


_inited = False


def initialize():
    ftlog.debug("newfish level_rewards initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from newfish.entity.event import GunLevelUpEvent, NewSkillEvent
        from newfish.game import TGFish
        TGFish.getEventBus().subscribe(GunLevelUpEvent, _triggerLevelUpEvent)
        TGFish.getEventBus().subscribe(NewSkillEvent, _triggerNewSkillEvent)
    ftlog.debug("newfish level_rewards initialize end")
