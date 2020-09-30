# -*- coding=utf-8 -*-
"""
Created by lichen on 2019-06-10.
宝藏系统
"""

import json
import time
import math
import random

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from freetime.core.timer import FTLoopTimer
import poker.util.timestamp as pktimestamp
from poker.protocol import router
from poker.util import strutil
from poker.entity.dao import daobase, userchip
from poker.entity.configure import gdata
from hall.entity import hallitem, datachangenotify
from newfish.entity.config import FISH_GAMEID
from newfish.entity import config, item, util, module_tip, mail_system
from newfish.entity.msg import GameMsg
from newfish.entity.redis_keys import UserData
from newfish.entity.event import TreasureLevelUp


INDEX_LEVEL = 0         # 第0位:宝藏等级
INDEX_FINISH_COUNT = 1  # 第1位:宝藏奖励今日触发次数
INDEX_FINISH_TIME = 2   # 第2位:宝藏奖励上一次触发时间


class EffectType:
    """
    宝藏效果类型
    """
    MatchRewardAdd = 1      # 参加回馈赛可额外得金币
    CoinComplement = 2      # 每日首次登录时，金币补足
    ItemComplement = 3      # 每日首次登陆时，锁定、冰冻补足
    ResComplement = 4       # 每日首次登陆时，珍珠、紫水晶、黄水晶补足
    AlmsCoinAdd = 5         # 救济金额度提高
    MatchItemReward = 6     # 完成大奖赛可得红宝石
    SaleItemCoinAdd = 7     # 出售道具获得金币提高
    FreeUseItemAdd = 8      # 使用锁定、冰冻时，有概率不消耗道具卡
    MatchRankRewardAdd = 9  # 回馈赛、大奖赛排名奖励提高
    BossRankRewardAdd = 10  # 任意Boss榜单、招财榜单排名奖励提高


def _getUserTreasureKey(userId):
    """
    宝藏数据存取key
    """
    return UserData.treasure % (FISH_GAMEID, userId)


def initTreasure(userId):
    """
    初始化宝藏数据
    """
    for kindId in config.getTreasureConf().keys():
        updateTreasure(userId, kindId)


def updateTreasure(userId, kindId):
    """
    更新新增宝藏数据
    """
    assert str(kindId) in config.getTreasureConf()
    daobase.executeUserCmd(userId, "HSETNX", _getUserTreasureKey(userId), str(kindId), json.dumps([0, 0, 0]))


def setTreasure(userId, kindId, treasureData):
    """
    存储单个宝藏数据
    """
    assert str(kindId) in config.getTreasureConf()
    assert isinstance(treasureData, list)
    daobase.executeUserCmd(userId, "HSET", _getUserTreasureKey(userId), str(kindId), json.dumps(treasureData))


def getTreasure(userId, kindId):
    """
    获得单个宝藏数据
    """
    assert str(kindId) in config.getTreasureConf()
    value = daobase.executeUserCmd(userId, "HGET", _getUserTreasureKey(userId), str(kindId))
    if value:
        return strutil.loads(value, False, True)
    return [0, 0, 0]


def getTreasureList(userId):
    """
    宝藏列表
    """
    treasures = []
    lang = util.getLanguage(userId)
    for kindId, treasureConf in config.getTreasureConf().iteritems():
        kindId = int(kindId)
        treasure = {}
        level, _ = getTreasureInfo(userId, kindId)
        treasure["kindId"] = kindId
        treasure["sortId"] = treasureConf["sortId"]
        treasure["name"] = config.getMultiLangTextConf(treasureConf["name"], lang=lang)
        treasure["desc"] = config.getMultiLangTextConf(treasureConf.get("desc"), lang=lang)
        treasure["level"] = level
        treasure["convert"] = treasureConf["convert"]
        treasures.append(treasure)

    def cmpSort(x, y):
        if x["level"] > y["level"]:
            return 1
        elif x["level"] < y["level"]:
            return -1
        else:
            if x["sortId"] < y["sortId"]:
                return 1
            else:
                return -1

    treasures.sort(cmp=cmpSort, reverse=True)
    return treasures


def getTreasureInfo(userId, kindId):
    """
    获取宝藏详情
    :param kindId: 宝藏道具ID
    :return: 当前等级, 等级配置
    """
    treasureData = getTreasure(userId, kindId)
    level = treasureData[INDEX_LEVEL]
    levelConf = config.getTreasureConf(kindId, level=level) if level else {}
    return level, levelConf


def upgradeTreasure(userId, kindId):
    """
    升级宝藏
    """
    code = 0
    treasureData = getTreasure(userId, kindId)
    levelConf = config.getTreasureConf(kindId, level=treasureData[INDEX_LEVEL] + 1)
    if treasureData[INDEX_LEVEL] >= len(config.getTreasureConf(kindId).get("levels", {})):
        code = 3
    elif not levelConf or not levelConf.get("cost", 0):
        code = 2
    else:
        consumeItems = [{"name": int(kindId), "count": int(levelConf["cost"])}]
        isOK = consumeUpgradeTreasureItem(userId, consumeItems, treasureData[INDEX_LEVEL] + 1)
        if isOK:
            treasureData[INDEX_LEVEL] += 1
            setTreasure(userId, kindId, treasureData)
            from newfish.game import TGFish
            event = TreasureLevelUp(userId, config.FISH_GAMEID, kindId, treasureData[INDEX_LEVEL])
            TGFish.getEventBus().publishEvent(event)
            checkTreasureUpgrade(userId)
        else:
            code = 1
    return code, treasureData[INDEX_LEVEL]


def convertTreasure(userId, kindId, count):
    """
    兑换宝藏碎片
    """
    code, rewards = 1, None
    treasureConf = config.getTreasureConf(kindId)
    convert = treasureConf.get("convert")
    if convert:
        surplusCount = util.balanceItem(userId, convert["kindId"])
        consumeCount = convert["rate"] * count
        if surplusCount >= consumeCount:
            consume = [{"name": convert["kindId"], "count": -abs(consumeCount)}]
            rewards = [{"name": kindId, "count": count}]
            consume.extend(rewards)
            code = util.addRewards(userId, consume, "BI_NFISH_TREASURE_CONVERT", kindId)
            return code, rewards
    return code, rewards


def checkUpgradeTreasureItemCount(userId, items):
    """
    检查升级所需道具是否足够
    """
    isOK = True
    for item in items:
        kindId = item["name"]
        needCount = item["count"]
        userAssets = hallitem.itemSystem.loadUserAssets(userId)
        surplusCount = userAssets.balance(FISH_GAMEID, util.getAssetKindId(kindId),
                                          pktimestamp.getCurrentTimestamp())
        if surplusCount < needCount:
            isOK = False
            break
    return isOK


def consumeUpgradeTreasureItem(userId, items, intEventParam=0, param01=0, param02=0):
    """
    升级所需道具
    """
    if checkUpgradeTreasureItemCount(userId, items):
        ret = util.consumeItems(userId, items, "BI_NFISH_TREASURE_UPGRADE", intEventParam, param01, param02)
        if len(ret) == len(items):
            return True
    return False


def refreshTreasureState(userId, kindId):
    """
    刷新宝藏状态等数据
    """
    treasureData = getTreasure(userId, kindId)
    lastTimestamp = treasureData[INDEX_FINISH_TIME]
    if util.getDayStartTimestamp(int(time.time())) != util.getDayStartTimestamp(lastTimestamp):
        treasureData[INDEX_FINISH_COUNT] = 0
        setTreasure(userId, kindId, treasureData)


def checkTreasureUpgrade(userId):
    """
    检查宝藏能否升级
    """
    upTreasures = []
    for kindId, _ in config.getTreasureConf().iteritems():
        treasureData = getTreasure(userId, kindId)
        levelConf = config.getTreasureConf(kindId, level=treasureData[INDEX_LEVEL] + 1)
        if treasureData[INDEX_LEVEL] < len(config.getTreasureConf(kindId).get("levels", {})):
            consumeItems = [{"name": int(kindId), "count": int(levelConf["cost"])}]
            if checkUpgradeTreasureItemCount(userId, consumeItems):
                upTreasures.append(int(kindId))
    module_tip.resetModuleTip(userId, "treasure")
    if upTreasures:
        module_tip.addModuleTipEvent(userId, "treasure", upTreasures)
    else:
        module_tip.resetModuleTipEvent(userId, "treasure")


def activeTreasure(userId, kindId, treasureData):
    """
    触发宝藏奖励
    """
    treasureData[INDEX_FINISH_COUNT] += 1
    treasureData[INDEX_FINISH_TIME] = int(time.time())
    setTreasure(userId, kindId, treasureData)


def getAlmsCoin(userId):
    """
    获取救济金额度
    """
    treasureConf = config.getTreasureConf(effectType=EffectType.AlmsCoinAdd)
    if treasureConf:
        kindId = treasureConf["kindId"]
        _, levelConf = getTreasureInfo(userId, kindId)
        return levelConf.get("params", {}).get("value", 0)
    return 0


# def getAlmsCountAdd(userId):
#     """
#     获取救济金加成次数
#     """
#     for treasureConf in config.getTreasureConf(effectType=EffectType.AlmsCountAdd):
#         kindId = treasureConf["kindId"]
#         _, levelConf = getTreasureInfo(userId, kindId)
#         return levelConf.get("params", {}).get("almsCount", 0)
#     return 0


def getCoinComplement(userId, coin=0):
    """
    获得金币补足
    :param userId:
    :param coin: 当处于渔场中时，使用渔场传过来的金币数
    """
    effect = {}
    userCoin = coin if coin > 0 else userchip.getChip(userId)
    treasureConf = config.getTreasureConf(effectType=EffectType.CoinComplement)
    if treasureConf:
        kindId = treasureConf["kindId"]
        level, levelConf = getTreasureInfo(userId, kindId)
        if not levelConf:
            return
        refreshTreasureState(userId, kindId)
        treasureData = getTreasure(userId, kindId)
        if treasureData[INDEX_FINISH_COUNT] >= treasureConf["limitCount"]:
            return
        coinComplement = levelConf.get("params", {}).get("value", 0)
        if coinComplement > userCoin:
            lang = util.getLanguage(userId)
            rewards = [{"name": config.CHIP_KINDID,
                        "count": coinComplement - userCoin,
                        "chgCount": [userCoin, coinComplement]}]
            util.addRewards(userId, rewards, "BI_NFISH_TREASURE_REWARDS", kindId)
            activeTreasure(userId, kindId, treasureData)
            treasureName = config.getMultiLangTextConf(treasureConf["name"], lang=lang)
            coinStr = util.formatScore(coinComplement, lang=lang)
            message = config.getMultiLangTextConf("ID_CONFIG_TREASURE_SUPPLY_101", lang=lang)
            message = message.format(coinStr, treasureName, coinStr)
            GameMsg.sendPrivate(FISH_GAMEID, userId, 0, message)
            effect = {
                "kindId": kindId,
                "level": level,
                "rewards": rewards
            }
    return effect


def getItemComplement(userId, count=0):
    """
    获得锁定、冰冻道具卡补足
    """
    effect = {}
    treasureConf = config.getTreasureConf(effectType=EffectType.ItemComplement)
    if treasureConf:
        kindId = treasureConf["kindId"]
        level, levelConf = getTreasureInfo(userId, kindId)
        if not levelConf:
            return
        refreshTreasureState(userId, kindId)
        treasureData = getTreasure(userId, kindId)
        if treasureData[INDEX_FINISH_COUNT] >= treasureConf["limitCount"]:
            return
        rewards = []
        lang = util.getLanguage(userId)
        for _kindId, _complementCount in levelConf.get("params", {}).iteritems():
            _kindId = int(_kindId)
            _surplusCount = util.balanceItem(userId, _kindId)
            if _complementCount > _surplusCount:
                _rewards = [
                    {"name": _kindId,
                     "count": _complementCount - _surplusCount,
                     "chgCount": [_surplusCount, _complementCount]}
                ]
                rewards.extend(_rewards)
                treasureName = config.getMultiLangTextConf(treasureConf["name"], lang=lang)
                countStr = util.formatScore(_complementCount, lang=lang)
                message = config.getMultiLangTextConf("ID_CONFIG_TREASURE_SUPPLY_%s" % _kindId, lang=lang)
                message = message.format(countStr, treasureName, countStr)
                GameMsg.sendPrivate(FISH_GAMEID, userId, 0, message)
        if rewards:
            util.addRewards(userId, rewards, "BI_NFISH_TREASURE_REWARDS", kindId)
            activeTreasure(userId, kindId, treasureData)
            effect = {
                "kindId": kindId,
                "level": level,
                "rewards": rewards
            }
    return effect


def getResComplement(userId, count=0):
    """
    获得珍珠、紫水晶、黄水晶道具补足
    """
    effect = {}
    treasureConf = config.getTreasureConf(effectType=EffectType.ResComplement)
    if treasureConf:
        kindId = treasureConf["kindId"]
        level, levelConf = getTreasureInfo(userId, kindId)
        if not levelConf:
            return
        refreshTreasureState(userId, kindId)
        treasureData = getTreasure(userId, kindId)
        if treasureData[INDEX_FINISH_COUNT] >= treasureConf["limitCount"]:
            return
        rewards = []
        lang = util.getLanguage(userId)
        for _kindId, _complementCount in levelConf.get("params", {}).iteritems():
            _kindId = int(_kindId)
            _surplusCount = util.balanceItem(userId, _kindId)
            if _complementCount > _surplusCount:
                _reward = {
                    "name": _kindId,
                    "count": _complementCount - _surplusCount,
                    "chgCount": [_surplusCount, _complementCount]
                }
                rewards.append(_reward)
                treasureName = config.getMultiLangTextConf(treasureConf["name"], lang=lang)
                countStr = util.formatScore(_complementCount, lang=lang)
                message = config.getMultiLangTextConf("ID_CONFIG_TREASURE_SUPPLY_%s" % _kindId, lang=lang)
                message = message.format(countStr, treasureName, countStr)
                GameMsg.sendPrivate(FISH_GAMEID, userId, 0, message)
        if rewards:
            util.addRewards(userId, rewards, "BI_NFISH_TREASURE_REWARDS", kindId)
            activeTreasure(userId, kindId, treasureData)
            effect = {
                "kindId": kindId,
                "level": level,
                "rewards": rewards
            }
    return effect


def getSaleItemExtraCoin(userId, coin):
    """
    神秘金币加赠额外金币
    """
    extraCoin = 0
    try:
        treasureConf = config.getTreasureConf(effectType=EffectType.SaleItemCoinAdd)
        if treasureConf:
            kindId = treasureConf["kindId"]
            level, levelConf = getTreasureInfo(userId, kindId)
            if levelConf:
                refreshTreasureState(userId, kindId)
                treasureData = getTreasure(userId, kindId)
                if treasureData[INDEX_FINISH_COUNT] < treasureConf["limitCount"]:
                    extraRate = levelConf.get("params", {}).get("value")
                    if extraRate:
                        extraCoin = int(coin * extraRate)
                        activeTreasure(userId, kindId, treasureData)
    except Exception as e:
        ftlog.error("treasure_system.getSaleItemExtraCoin error", e,
                    "userId=", userId,
                    "chip=", coin)
    if ftlog.is_debug():
        ftlog.debug("treasure_system.getSaleItemExtraCoin OUT",
                    "userId=", userId,
                    "chip=", coin,
                    "extraCoin=", extraCoin)
    return extraCoin


def isUseItemFree(userId, value):
    """
    时间沙漏，判断是否不消耗道具卡
    """
    try:
        treasureConf = config.getTreasureConf(effectType=EffectType.FreeUseItemAdd)
        if treasureConf:
            kindId = treasureConf["kindId"]
            level, levelConf = getTreasureInfo(userId, kindId)
            if levelConf:
                refreshTreasureState(userId, kindId)
                treasureData = getTreasure(userId, kindId)
                if treasureData[INDEX_FINISH_COUNT] < treasureConf["limitCount"]:
                    chance = levelConf.get("params", {}).get("value")
                    randomValue = random.randint(1, 10000)
                    if ftlog.is_debug():
                        ftlog.debug("treasure_system.isUseItemFree get",
                                    "userId=", userId,
                                    "level=", level,
                                    "levelConf=", levelConf,
                                    "chance=", chance,
                                    "randomValue=", randomValue)
                    if randomValue <= chance * 10000:
                        activeTreasure(userId, kindId, treasureData)
                        sendTreasureTriggerMsg(userId, kindId, value)
                        return True
    except Exception as e:
        ftlog.error("treasure_system.isUseItemFree error", e,
                    "userId=", userId)
    return False


def getTreasureRewards(userId, count=0):
    """
    发放宝藏奖励
    """
    try:
        effectList = []
        for func in (getCoinComplement,
                     getItemComplement,
                     getResComplement):
            effect = func(userId, count)
            if ftlog.is_debug():
                ftlog.debug("getTreasureRewards", effect)
            if effect:
                effectList.append(effect)
        if effectList:
            FTLoopTimer(2, 0, sendTreasureRewardsMsg, userId, effectList).start()
    except Exception as e:
        ftlog.error("treasure_system.getTreasureRewards error", e,
                    "userId=", userId)


def sendTreasureRewardsMsg(userId, effectList):
    """
    发送宝藏奖励消息
    """
    msg = MsgPack()
    msg.setCmd("treasure_rewards")
    msg.setResult("gameId", FISH_GAMEID)
    msg.setResult("userId", userId)
    msg.setResult("effect", effectList)
    router.sendToUser(msg, userId)


def sendTreasureTriggerMsg(userId, kindId, value=None):
    """
    发送宝藏触发提示消息
    """
    msg = MsgPack()
    msg.setCmd("treasure_trigger")
    msg.setResult("gameId", FISH_GAMEID)
    msg.setResult("userId", userId)
    msg.setResult("kindId", kindId)
    if value:
        msg.setResult("value", value)
    router.sendToUser(msg, userId)


def provideFinishTimeMatchReward(userId, bigRoomId):
    """
    完成回馈赛发放宝藏奖励到邮件
    """
    treasureConf = config.getTreasureConf(effectType=EffectType.MatchRewardAdd)
    if treasureConf:
        kindId = treasureConf["kindId"]
        level, levelConf = getTreasureInfo(userId, kindId)
        if not levelConf:
            return
        refreshTreasureState(userId, kindId)
        treasureData = getTreasure(userId, kindId)
        if treasureData[INDEX_FINISH_COUNT] >= treasureConf["limitCount"]:
            return
        lang = util.getLanguage(userId)
        if str(bigRoomId) in levelConf.get("params", {}):
            matchName = config.getMultiLangTextConf(gdata.getRoomConfigure(bigRoomId).get("name", ""), lang=lang)
            rewards = [{"name": config.CHIP_KINDID, "count": levelConf["params"][str(bigRoomId)]}]
            treasureName = config.getMultiLangTextConf(treasureConf["name"], lang=lang)
            message = config.getMultiLangTextConf("ID_CONFIG_TREASURE_FINISH_TIME_MATCH", lang=lang)
            message = message.format(matchName, level, treasureName)
            title = config.getMultiLangTextConf("ID_MAIL_TITLE_TREASURE_REWARD", lang=lang)
            mail_system.sendSystemMail(userId, mail_system.MailRewardType.TreasureReward, rewards, message, title)
            activeTreasure(userId, kindId, treasureData)


def provideFinishGrandPrixReward(userId):
    """
    完成大奖赛发放宝藏奖励到邮件
    """
    treasureConf = config.getTreasureConf(effectType=EffectType.MatchItemReward)
    if treasureConf:
        kindId = treasureConf["kindId"]
        level, levelConf = getTreasureInfo(userId, kindId)
        if not levelConf:
            return
        refreshTreasureState(userId, kindId)
        treasureData = getTreasure(userId, kindId)
        if treasureData[INDEX_FINISH_COUNT] >= treasureConf["limitCount"]:
            return
        rewards = []
        lang = util.getLanguage(userId)
        for _kindId, _count in levelConf.get("params", {}).iteritems():
            rewards.append({"name": int(_kindId), "count": _count})
        if rewards:
            treasureName = config.getMultiLangTextConf(treasureConf["name"], lang=lang)
            message = config.getMultiLangTextConf("ID_CONFIG_TREASURE_FINISH_GRAND_PRIX", lang=lang).format(level,
                                                                                                            treasureName)
            title = config.getMultiLangTextConf("ID_MAIL_TITLE_TREASURE_REWARD", lang=lang)
            mail_system.sendSystemMail(userId, mail_system.MailRewardType.TreasureReward, rewards, message, title)
            activeTreasure(userId, kindId, treasureData)


def provideTimeMatchRankReward(userId, roomId, rank, rankRewards):
    """
    回馈赛上榜发放宝藏奖励到邮件
    """
    treasureConf = config.getTreasureConf(effectType=EffectType.MatchRankRewardAdd)
    if treasureConf:
        kindId = treasureConf["kindId"]
        level, levelConf = getTreasureInfo(userId, kindId)
        if not levelConf:
            return
        refreshTreasureState(userId, kindId)
        treasureData = getTreasure(userId, kindId)
        if treasureData[INDEX_FINISH_COUNT] >= treasureConf["limitCount"]:
            return
        rewards = []
        lang = util.getLanguage(userId)
        ratio = levelConf["params"]["time_match"]
        for _reward in rankRewards:
            if _reward["name"] in config.BULLET_VALUE:
                name = config.BRONZE_BULLET_KINDID
                count = int(math.ceil(_reward["count"] * config.BULLET_VALUE[_reward["name"]] * ratio))
            else:
                name = _reward["name"]
                count = int(math.ceil(_reward["count"] * ratio))
            rewards.append({"name": name, "count": count})
        if rewards:
            matchName = config.getMultiLangTextConf(gdata.getRoomConfigure(roomId).get("name", ""), lang=lang)
            treasureName = config.getMultiLangTextConf(treasureConf["name"], lang=lang)
            message = config.getMultiLangTextConf("ID_CONFIG_TREASURE_TIME_MATCH_RANK", lang=lang)
            message = message.format(matchName, rank, level, treasureName)
            title = config.getMultiLangTextConf("ID_MAIL_TITLE_TREASURE_REWARD", lang=lang)
            mail_system.sendSystemMail(userId, mail_system.MailRewardType.TreasureReward, rewards, message, title)
            activeTreasure(userId, kindId, treasureData)


def provideRankReward(userId, rankId, rankType, rank, params):
    """
    特定排行榜上榜发放宝藏奖励到邮件
    """
    from newfish.entity.ranking import ranking_system
    lang = util.getLanguage(userId)
    if rankId == config.RANK_GRAND_PRIX:
        # 大奖赛
        treasureConf = config.getTreasureConf(effectType=EffectType.MatchRankRewardAdd)
        if treasureConf:
            kindId = treasureConf["kindId"]
            level, levelConf = getTreasureInfo(userId, kindId)
            if not levelConf:
                return
            refreshTreasureState(userId, kindId)
            treasureData = getTreasure(userId, kindId)
            if treasureData[INDEX_FINISH_COUNT] >= treasureConf["limitCount"]:
                return
            rewards = []
            ratio = levelConf["params"]["grand_prix"]
            for _reward in params["rewards"]:
                if _reward["name"] in config.BULLET_VALUE:
                    name = config.BRONZE_BULLET_KINDID
                    count = int(math.ceil(_reward["count"] * config.BULLET_VALUE[_reward["name"]] * ratio))
                else:
                    name = _reward["name"]
                    count = int(math.ceil(_reward["count"] * ratio))
                rewards.append({"name": name, "count": count})
            if rewards:
                treasureName = config.getMultiLangTextConf(treasureConf["name"], lang=lang)
                message = config.getMultiLangTextConf("ID_CONFIG_TREASURE_GRAND_PRIX_RANK", lang=lang)
                message = message.format(rank, level, treasureName)
                title = config.getMultiLangTextConf("ID_MAIL_TITLE_TREASURE_REWARD", lang=lang)
                mail_system.sendSystemMail(userId, mail_system.MailRewardType.TreasureReward, rewards, message, title)
                activeTreasure(userId, kindId, treasureData)

    # elif rankType in ranking_system.SbossPointRankTypeDefineIndexDict:
    #     # Boss幸运榜
    #     treasureConf = config.getTreasureConf(effectType=EffectType.BossRankRewardAdd)
    #     if treasureConf:
    #         kindId = treasureConf["kindId"]
    #         level, levelConf = getTreasureInfo(userId, kindId)
    #         if not levelConf:
    #             return
    #         refreshTreasureState(userId, kindId)
    #         treasureData = getTreasure(userId, kindId)
    #         if treasureData[INDEX_FINISH_COUNT] >= treasureConf["limitCount"]:
    #             return
    #         rewards = []
    #         ratio = levelConf["params"]["boss"]
    #         for _reward in params["rewards"]:
    #             if _reward["name"] in config.BULLET_VALUE:
    #                 name = config.BRONZE_BULLET_KINDID
    #                 count = int(math.ceil(_reward["count"] * config.BULLET_VALUE[_reward["name"]] * ratio))
    #             else:
    #                 name = _reward["name"]
    #                 count = int(math.ceil(_reward["count"] * ratio))
    #             rewards.append({"name": name, "count": count})
    #         if rewards:
    #             rankRewardConf = config.getRankRewardConf(rankType)
    #             rankName = config.getMultiLangTextConf(rankRewardConf["rankName"], lang=lang)
    #             treasureName = config.getMultiLangTextConf(treasureConf["name"], lang=lang)
    #             message = config.getMultiLangTextConf("ID_CONFIG_TREASURE_BOSS_RANK", lang=lang).format(rankName, rank, level, treasureName)
    #             title = config.getMultiLangTextConf("ID_MAIL_TITLE_TREASURE_REWARD", lang=lang)
    #             mail_system.sendSystemMail(userId, mail_system.MailRewardType.TreasureReward, rewards, message, title)
    #             activeTreasure(userId, kindId, treasureData)

    elif rankId == config.RANK_ROBBERY_DAY_WIN:
        # 招财赢家榜
        treasureConf = config.getTreasureConf(effectType=EffectType.BossRankRewardAdd)
        if treasureConf:
            kindId = treasureConf["kindId"]
            level, levelConf = getTreasureInfo(userId, kindId)
            if not levelConf:
                return
            refreshTreasureState(userId, kindId)
            treasureData = getTreasure(userId, kindId)
            if treasureData[INDEX_FINISH_COUNT] >= treasureConf["limitCount"]:
                return
            ratio = levelConf["params"]["robbery"]
            count = int(math.ceil(params["originCount"] * ratio))
            rewards = [{"name": config.BRONZE_BULLET_KINDID, "count": count}]
            treasureName = config.getMultiLangTextConf(treasureConf["name"], lang=lang)
            message = config.getMultiLangTextConf("ID_CONFIG_TREASURE_ROBBERY_RANK", lang=lang)
            message = message.format(rank, level, treasureName)
            title = config.getMultiLangTextConf("ID_MAIL_TITLE_TREASURE_REWARD", lang=lang)
            mail_system.sendSystemMail(userId, mail_system.MailRewardType.TreasureReward, rewards, message, title)
            activeTreasure(userId, kindId, treasureData)


def dealTreasureReward(userId, clientId, dayFirst):
    """
    处理宝藏奖励发放
    """
    if ftlog.is_debug():
        ftlog.debug("dealTreasureReward", userId, clientId, dayFirst)
    for kindId, _ in config.getTreasureConf().iteritems():
        refreshTreasureState(userId, kindId)
    if dayFirst:
        isIn, roomId, tableId, seatId = util.isInFishTable(userId)
        if isIn and util.getRoomTypeName(roomId) in config.NORMAL_ROOM_TYPE:
            mo = MsgPack()
            mo.setCmd("table_call")
            mo.setParam("action", "treasure_rewards")
            mo.setParam("gameId", FISH_GAMEID)
            mo.setParam("clientId", clientId)
            mo.setParam("userId", userId)
            mo.setParam("roomId", roomId)
            mo.setParam("tableId", tableId)
            mo.setParam("seatId", seatId)
            router.sendTableServer(mo, roomId)
        else:
            getTreasureRewards(userId)


def _triggerUserLoginEvent(event):
    """
    用户登录事件
    """
    userId = event.userId
    clientId = event.clientId
    dayFirst = event.dayFirst
    dealTreasureReward(userId, clientId, dayFirst)
    checkTreasureUpgrade(userId)


def _triggerMatchOverEvent(event):
    """
    完成回馈赛事件
    """
    provideFinishTimeMatchReward(event.userId, event.bigRoomId)


def _triggerFinishGrandPrixEvent(event):
    """
    完成大奖赛事件
    """
    provideFinishGrandPrixReward(event.userId)


def _triggerMatchRewardEvent(event):
    """
    回馈赛排名结算发奖事件
    """
    provideTimeMatchRankReward(event.userId, event.roomId, event.rank, event.rewards)


def _triggerRankOverEvent(event):
    """
    排行榜结算事件
    """
    provideRankReward(event.userId, event.rankId, event.rankType, event.rank, event.params)


def _triggerTreasureItemCountChangeEvent(event):
    """
    宝藏升级相关物品数量变化事件
    """
    checkTreasureUpgrade(event.userId)


_inited = False


def initialize():
    ftlog.debug("newfish treasure_system initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from poker.entity.events.tyevent import EventUserLogin
        from newfish.game import TGFish
        from newfish.entity.event import MatchOverEvent, RankOverEvent, FinishGrandPrixEvent, \
            MatchRewardEvent, TreasureItemCountChangeEvent
        TGFish.getEventBus().subscribe(EventUserLogin, _triggerUserLoginEvent)
        TGFish.getEventBus().subscribe(MatchOverEvent, _triggerMatchOverEvent)
        TGFish.getEventBus().subscribe(FinishGrandPrixEvent, _triggerFinishGrandPrixEvent)
        TGFish.getEventBus().subscribe(MatchRewardEvent, _triggerMatchRewardEvent)
        TGFish.getEventBus().subscribe(RankOverEvent, _triggerRankOverEvent)
        TGFish.getEventBus().subscribe(TreasureItemCountChangeEvent, _triggerTreasureItemCountChangeEvent)
    ftlog.debug("newfish treasure_system initialize end")