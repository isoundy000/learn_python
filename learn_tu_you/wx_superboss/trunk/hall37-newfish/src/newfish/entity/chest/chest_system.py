# -*- coding=utf-8 -*-
"""
Created by lichen on 17/2/8.
"""

import random
import math

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
import poker.util.timestamp as pktimestamp
from poker.entity.biz import bireport
from poker.entity.dao import userchip, gamedata
from hall.entity import hallitem
from hall.entity.hallitem import TYOpenItemEvent
from hall.entity.hallitem import TYChestItem
from newfish.entity import config, util, module_tip
from newfish.entity.msg import GameMsg
from newfish.entity.redis_keys import GameData
from newfish.entity.skill import skill_system
from newfish.entity.config import FISH_GAMEID, PEARL_KINDID, \
     CHIP_KINDID, COUPON_KINDID, STARFISH_KINDID, SKILLCD_KINDID, \
    BRONZE_BULLET_KINDID, SILVER_BULLET_KINDID, GOLD_BULLET_KINDID, RUBY_KINDID


# 宝箱栏最大数量
CHEST_NUMBER_LIMIT = 4

# 宝箱开启倒计时延时
CHEST_OPEN_DELAY_TIME = 0

# 宝箱ID前缀与大厅道具ID对应表
chestKindIdMap = {
    31: 1138,
    32: 1139,
    33: 1140,
    34: 1141,
    35: 1142,
    36: 1143,
    37: 1144
}


class ItemType:
    """
    宝箱物品类型
    """
    Skill = 1       # 技能卡
    Star = 2        # 升星卡
    GunSkin = 3     # 皮肤炮
    Crystal = 4     # (黄/紫)水晶


class ChestState:
    """
    宝箱状态
    """
    WaitOpen = 0    # 等待开启
    Opening = 1     # 开启倒计时中
    Opened = 2      # 可以开启


class ChestAction:
    """
    宝箱执行行为
    """
    NormalOpen = 0  # 普通开启
    AtOnceOpen = 1  # 立即开启
    Discard = 2     # 丢弃


class ChestFromType:
    # 宝箱来源
    Share_Chest_Fish = 0         # 分享宝箱鱼
    Fly_Pig_Chest = 1            # 飞猪宝箱
    Cmptt_Ncmptt_Bonus_Task = 2  # 渔场比赛获得
    Daily_Quest_Week_Chest = 3   # 每日任务周宝箱
    Daily_Quest_Daily_Chest = 4  # 每日任务每日宝箱


def newChestItem(userId, chestId, eventId, intEventParam=0):
    """
    生成一个宝箱
    """
    idleOrder = getChestIdleOrder(userId)
    if idleOrder < 0:
        ftlog.debug("newChestItem-> not idle order", userId)
        return False
    kindId = chestKindIdMap.get(chestId // 1000, 0)
    if not kindId:
        ftlog.error("newChestItem-> chestId error", chestId, userId)
        return False
    itemKind = hallitem.itemSystem.findItemKind(kindId)
    if not itemKind:
        ftlog.error("newChestItem-> kindId error", kindId, userId)
        return False
    chestConf = config.getChestConf(chestId)
    if not chestConf:
        ftlog.error("newChestItem-> chestConf error", chestId, userId)
        return False
    itemData = itemKind.newItemData()
    itemData.createTime = pktimestamp.getCurrentTimestamp()
    itemData.beginTime = itemData.createTime
    itemData.itemKindId = kindId
    itemData.chestId = chestId
    itemData.order = idleOrder
    itemData.totalTime = int(chestConf["unlockTime"])
    itemData.state = 0
    item = hallitem.itemSystem.newItemFromItemData(itemData)
    if not item:
        ftlog.error("newChestItem-> newItem error", chestId, userId)
        return False
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    timestamp = pktimestamp.getCurrentTimestamp()
    userBag.addItem(FISH_GAMEID, item, timestamp, eventId, intEventParam)
    return True


def getChestIdleOrder(userId):
    """
    得到空闲的宝箱栏位置
    """
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    chestItemList = userBag.getAllTypeItem(TYChestItem)
    if len(chestItemList) < CHEST_NUMBER_LIMIT:
        idleOrder = range(CHEST_NUMBER_LIMIT)
        for chestItem in chestItemList:
            idleOrder.remove(chestItem.order)
        idleOrder.sort()
        return idleOrder[0]
    return -1


def sendChestListInfo(userId):
    """
    发送宝箱列表消息
    """
    mo = MsgPack()
    mo.setCmd("chest_list")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("chests", getChestList(userId))
    router.sendToUser(mo, userId)


def getChestList(userId):
    """
    获取宝箱列表
    """
    module_tip.resetModuleTip(userId, "chest")
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    chestItemList = userBag.getAllTypeItem(TYChestItem)
    chestItemList = sorted(chestItemList, key=lambda chestItem: chestItem.order)
    chestList = []
    openedChestList = []
    for chestItem in chestItemList:
        if not chestItem.chestId:
            ftlog.error("chest item error", userId)
            continue
        openingOrder = [chestItemTmp.order for chestItemTmp in chestItemList if chestItemTmp.state == 1]
        chestConf = config.getChestConf(chestItem.chestId)
        chest = {}
        if chestItem.totalTime <= 0:
            chestItem.state = ChestState.Opened
        if chestItem.state == ChestState.WaitOpen and not openingOrder:
            chestItem.state = ChestState.Opening
        if chestItem.state == ChestState.WaitOpen:
            chestTimeLeft = chestItem.totalTime
        elif chestItem.state == ChestState.Opening:
            chestTimeLeft = chestItem.beginTime + chestItem.totalTime - pktimestamp.getCurrentTimestamp() + CHEST_OPEN_DELAY_TIME
        else:
            chestTimeLeft = 0
        if chestItem.state == ChestState.Opening and chestTimeLeft <= 0:
            chestItem.state = ChestState.Opened
            noOpenOrderList = [chestItemTmp.order for chestItemTmp in chestItemList if chestItemTmp.state == 0]
            if noOpenOrderList:
                nextOpeningChestItem = None
                for noOpenOrder in noOpenOrderList:
                    if noOpenOrder > chestItem.order:
                        nextOpeningChestItem = [chestItemImp for chestItemImp in chestItemList if chestItemImp.order == noOpenOrder][0]
                        break
                if not nextOpeningChestItem:
                    nextOpeningChestItem = [chestItemImp for chestItemImp in chestItemList if chestItemImp.order == noOpenOrderList[0]][0]
                if nextOpeningChestItem:
                    nextOpeningChestItem.state = ChestState.Opening
                    nextOpeningChestItem.beginTime = chestItem.beginTime + chestItem.totalTime
                    userBag.updateItem(FISH_GAMEID, nextOpeningChestItem, pktimestamp.getCurrentTimestamp())
                    for chestTmp in chestList:
                        if chestTmp["order"] == nextOpeningChestItem.order:
                            chestTmp["state"] = 1
                            chestTmp["timeLeft"] = nextOpeningChestItem.beginTime + nextOpeningChestItem.totalTime - \
                                                   pktimestamp.getCurrentTimestamp() + CHEST_OPEN_DELAY_TIME
                            break
        chestTimeLeft = max(0, chestTimeLeft)
        chest["order"] = chestItem.order
        chest["state"] = chestItem.state
        chest["chestId"] = chestItem.chestId
        chest["itemId"] = chestItem.itemId
        chest["kindId"] = chestItem.kindId
        chest["desc"] = chestItem.itemKind.desc
        chest["createTime"] = chestItem.createTime
        chest["timeLeft"] = chestTimeLeft
        chest["totalTime"] = chestItem.totalTime
        chest["openCoin"] = chestConf["openCoin"]
        chest["diamond"] = _needCoinAsOpenChest(chestItem.chestId, chestTimeLeft)
        chest["info"] = getChestInfo(chestItem.chestId)
        chestList.append(chest)
        userBag.updateItem(FISH_GAMEID, chestItem, pktimestamp.getCurrentTimestamp())
        if chestItem.state == ChestState.Opened:
            openedChestList.append(chestItem.itemId)
    ftlog.debug("getChestList->", chestList)
    module_tip.addModuleTipEvent(userId, "chest", openedChestList)
    return chestList


def getChestInfo(chestId):
    """
    获取宝箱物品详情
    """
    chestInfo = {}
    try:
        chestConf = config.getChestConf(chestId)
        chestInfo["chestId"] = int(chestId)
        chestInfo["chestStar"] = chestConf["star"]
        chestInfo["chestType"] = chestConf["type"]
        chestInfo["show"] = chestConf["show"]
        # 各稀有度技能卡数量范围
        skillCardMinCount, skillCardMaxCount = 0, 0
        if chestConf["nCardRate"] > 0:
            cardMinCount, cardMaxCount = getChestCardQuantitativeRange(chestConf["nCardRate"],
                                                                       chestConf["nCardRandom"],
                                                                       chestConf["nCardRange"])
            skillCardMinCount += cardMinCount
            skillCardMaxCount += cardMaxCount
        if chestConf["rCardRate"] > 0:
            cardMinCount, cardMaxCount = getChestCardQuantitativeRange(chestConf["rCardRate"],
                                                                       chestConf["rCardRandom"],
                                                                       chestConf["rCardRange"])
            skillCardMinCount += cardMinCount
            skillCardMaxCount += cardMaxCount
        if chestConf["srCardRate"] > 0:
            cardMinCount, cardMaxCount = getChestCardQuantitativeRange(chestConf["srCardRate"],
                                                                       chestConf["srCardRandom"],
                                                                       chestConf["srCardRange"])
            skillCardMinCount += cardMinCount
            skillCardMaxCount += cardMaxCount
        if chestConf["cardCertainNum"] > 0:
            skillCardMinCount = max(skillCardMinCount, chestConf["cardCertainNum"])
        # 各稀有度升星卡数量范围
        starCardMinCount, starCardMaxCount = 0, 0
        if chestConf["nStarCardRate"] > 0:
            cardMinCount, cardMaxCount = getChestCardQuantitativeRange(chestConf["nStarCardRate"],
                                                                       chestConf["nStarCardRandom"],
                                                                       chestConf["nStarCardRange"])
            starCardMinCount += cardMinCount
            starCardMaxCount += cardMaxCount
        if chestConf["rCardRate"] > 0:
            cardMinCount, cardMaxCount = getChestCardQuantitativeRange(chestConf["rStarCardRate"],
                                                                       chestConf["rStarCardRandom"],
                                                                       chestConf["rStarCardRange"])
            starCardMinCount += cardMinCount
            starCardMaxCount += cardMaxCount
        if chestConf["srStarCardRate"] > 0:
            cardMinCount, cardMaxCount = getChestCardQuantitativeRange(chestConf["srStarCardRate"],
                                                                       chestConf["srStarCardRandom"],
                                                                       chestConf["srStarCardRange"])
            starCardMinCount += cardMinCount
            starCardMaxCount += cardMaxCount
        if chestConf["starCardCertainNum"] > 0:
            starCardMinCount = max(starCardMinCount, chestConf["starCardCertainNum"])

        if skillCardMinCount or skillCardMaxCount:
            skillCard = {}
            chestInfo["skillCard"] = skillCard
            skillCard["kinds"] = [kind["kindId"] for kind in getChestDropList(chestConf, ItemType.Skill)]
            skillCard["count"] = [skillCardMinCount, skillCardMaxCount]
        if starCardMinCount or starCardMaxCount:
            starCard = {}
            chestInfo["starCard"] = starCard
            starCard["kinds"] = [kind["kindId"] for kind in getChestDropList(chestConf, ItemType.Star)]
            starCard["count"] = [starCardMinCount, starCardMaxCount]

        chestInfo["items"] = []
        # 水晶数量范围
        if chestConf["crystalRate"] > 0:
            crystalMinCount, crystalMaxCount = getChestCardQuantitativeRange(chestConf["crystalRate"],
                                                                             chestConf["crystalRandom"],
                                                                             chestConf["crystalRange"])
            if crystalMinCount or crystalMaxCount:
                crystalItem = {}
                crystalItem["kinds"] = [kind["kindId"] for kind in getChestDropList(chestConf, ItemType.Crystal)]
                crystalItem["count"] = [crystalMinCount, crystalMaxCount]
                chestInfo["items"].append(crystalItem)

        if chestConf["coinRange"][0]:
            chestInfo["coin"] = [chestConf["coinRange"][0], chestConf["coinRange"][1]]
        if chestConf["pearlRange"][0]:
            chestInfo["pearl"] = [chestConf["pearlRange"][0], chestConf["pearlRange"][1]]
        if chestConf["couponRate"]:
            chestInfo["coupon"] = [chestConf["couponRange"][0], chestConf["couponRange"][1]]
        if chestConf["starfishRate"]:
            chestInfo["starfish"] = [chestConf["starfishRange"][0], chestConf["starfishRange"][1]]
        if chestConf["coolDownRate"]:
            chestInfo["coolDown"] = [chestConf["coolDownRange"][0], chestConf["coolDownRange"][1]]
        if chestConf["bronzeBulletRate"]:
            chestInfo["bronzeBullet"] = [chestConf["bronzeBulletRange"][0], chestConf["bronzeBulletRange"][1]]
        if chestConf["silverBulletRate"]:
            chestInfo["silverBullet"] = [chestConf["silverBulletRange"][0], chestConf["silverBulletRange"][1]]
        if chestConf["goldBulletRate"]:
            chestInfo["goldBullet"] = [chestConf["goldBulletRange"][0], chestConf["goldBulletRange"][1]]
        if chestConf["rubyRate"]:
            chestInfo["ruby"] = [chestConf["rubyRange"][0], chestConf["rubyRange"][1]]
        for _item in chestConf.get("itemsData", []):
            if _item["rate"]:
                val = {}
                val["kinds"] = [_item["kindId"]]
                val["count"] = [_item["min"], _item["max"]]
                chestInfo["items"].append(val)
    except Exception as e:
        ftlog.error("getChestInfo error", chestId, e)
        return chestInfo
    return chestInfo


def adjustChestOrder(userId, oldOrder, newOrder):
    """
    调整宝箱位置
    """
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    chestItemList = userBag.getAllTypeItem(TYChestItem)
    if oldOrder == newOrder or \
       oldOrder > CHEST_NUMBER_LIMIT or \
       newOrder > CHEST_NUMBER_LIMIT or \
       oldOrder < 0 or newOrder < 0:
        return False
    oldChestItem, newChestItem = None, None
    for chestItem in chestItemList:
        if chestItem.order == oldOrder:
            oldChestItem = chestItem
        if chestItem.order == newOrder:
            newChestItem = chestItem
    if not oldChestItem:
        return False
    oldChestItem.order = newOrder
    userBag.updateItem(FISH_GAMEID, oldChestItem, pktimestamp.getCurrentTimestamp())
    if newChestItem:
        newChestItem.order = oldOrder
        userBag.updateItem(FISH_GAMEID, newChestItem, pktimestamp.getCurrentTimestamp())
    return True


def getChestItemDetail(userId, order=-1):
    """
    获取order对应的宝箱、处于开启中状态的宝箱、下个处于开启中状态的宝箱对象
    """
    getChestList(userId)
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    chestItemList = userBag.getAllTypeItem(TYChestItem)
    chestItemList = sorted(chestItemList, key=lambda chestItem: chestItem.order)
    noOpenOrderList = [chestItemImp.order for chestItemImp in chestItemList if chestItemImp.state == 0]
    chestItem, openingChestItem, nextOpeningChestItem = None, None, None
    for chestItemTmp in chestItemList:
        if chestItemTmp.order == order:
            chestItem = chestItemTmp
        if chestItemTmp.state == 1:
            openingChestItem = chestItemTmp
        if openingChestItem and noOpenOrderList:
            for noOpenOrder in noOpenOrderList:
                if noOpenOrder > openingChestItem.order:
                    nextOpeningChestItem = [chestItemImp for chestItemImp in chestItemList if chestItemImp.order == noOpenOrder][0]
                    break
            if not nextOpeningChestItem:
                nextOpeningChestItem = [chestItemImp for chestItemImp in chestItemList if chestItemImp.order == noOpenOrderList[0]][0]
    return userBag, chestItem, openingChestItem, nextOpeningChestItem


def executeChestAction(userId, order, actionType):
    """
    对背包中的宝箱执行行为
    """
    rewards = []
    userBag, chestItem, openingChestItem, nextOpeningChestItem = getChestItemDetail(userId, order)
    if actionType in [ChestAction.NormalOpen, ChestAction.AtOnceOpen]:  # [普通开启, 立即开启]
        if not chestItem:
            ftlog.info("openChest->not chestItem", userId)
            return 1, rewards
        if actionType == ChestAction.NormalOpen and chestItem.state != ChestState.Opened:
            ftlog.error("openChest->state error", userId)
            return 2, rewards
        if actionType == ChestAction.AtOnceOpen:    # 立即开启宝箱，执行扣金币操作
            chestTimeLeft = chestItem.beginTime + chestItem.totalTime - pktimestamp.getCurrentTimestamp()
            if chestTimeLeft > 0:
                needCoin = _needCoinAsOpenChest(chestItem.chestId, chestTimeLeft)
                chip = userchip.getChip(userId)
                if chip < needCoin:
                    ftlog.debug("openChest->chip not enough")
                    return 3, rewards
                util.addRewards(userId, [{"name": config.CHIP_KINDID, "count": -abs(needCoin)}], "BI_NFISH_ATONCE_OPEN_CHEST")
                # 修改下个宝箱的状态及时间
                if chestItem == openingChestItem and nextOpeningChestItem:
                    nextOpeningChestItem.state = ChestState.Opening
                    nextOpeningChestItem.beginTime = pktimestamp.getCurrentTimestamp()
                    userBag.updateItem(FISH_GAMEID, nextOpeningChestItem, pktimestamp.getCurrentTimestamp())
        # 发放宝箱奖励
        rewards = getChestRewards(userId, chestItem.chestId)
        deliveryChestRewards(userId, chestItem.chestId, rewards)
        # 删除已开启宝箱
        userBag.removeItem(FISH_GAMEID, chestItem, pktimestamp.getCurrentTimestamp(), "ITEM_USE", actionType)
        # 打开宝箱事件
        from newfish.game import TGFish
        from newfish.entity.event import OpenChestEvent
        event = OpenChestEvent(userId, FISH_GAMEID, chestItem.chestId, actionType)
        TGFish.getEventBus().publishEvent(event)
    elif actionType == ChestAction.Discard: # 丢弃宝箱
        # 获得宝箱开启倒计时
        chestTimeLeft = chestItem.beginTime + chestItem.totalTime - pktimestamp.getCurrentTimestamp()
        if chestTimeLeft > 0:
            # 修改下个宝箱的状态及时间
            if chestItem == openingChestItem and nextOpeningChestItem:
                nextOpeningChestItem.state = ChestState.Opening
                nextOpeningChestItem.beginTime = pktimestamp.getCurrentTimestamp()
                userBag.updateItem(FISH_GAMEID, nextOpeningChestItem, pktimestamp.getCurrentTimestamp())
        # 删除已丢弃宝箱
        userBag.removeItem(FISH_GAMEID, chestItem, pktimestamp.getCurrentTimestamp(), "ITEM_USE", actionType)
    return 0, rewards


def chestOpeningToOpened(userId):
    """
    使当前处于开启中状态的宝箱变为可以开启状态
    """
    userBag, chestItem, openingChestItem, nextOpeningChestItem = getChestItemDetail(userId)
    if openingChestItem:
        openingChestItem.totalTime = 0
        openingChestItem.state = ChestState.Opened
        userBag.updateItem(FISH_GAMEID, openingChestItem, pktimestamp.getCurrentTimestamp())
        if nextOpeningChestItem:
            nextOpeningChestItem.state = ChestState.Opening
            nextOpeningChestItem.beginTime = pktimestamp.getCurrentTimestamp()
            userBag.updateItem(FISH_GAMEID, nextOpeningChestItem, pktimestamp.getCurrentTimestamp())
        sendChestListInfo(userId)


def getChestRewards(userId, chestId):
    """
    获取宝箱物品
    """
    rewards = []
    chestConf = config.getChestConf(chestId)
    if not chestConf:
        ftlog.error("getChestRewards error", userId, chestId)
        return rewards
    # 计算金币、珍珠个数
    coinCount = random.randint(chestConf["coinRange"][0], chestConf["coinRange"][1])
    pearlCount = random.randint(chestConf["pearlRange"][0], chestConf["pearlRange"][1])
    if coinCount > 0:
        coin = {"name": CHIP_KINDID, "count": coinCount}
        rewards.append(coin)
    if pearlCount > 0:
        pearl = {"name": PEARL_KINDID, "count": pearlCount}
        rewards.append(pearl)

    # 根据宝箱物品等级确定物品范围
    chestDropList = getChestDropList(chestConf)

    # 根据稀有度划分技能卡片、技能升星卡、火炮皮肤、(黄/紫)水晶
    skillCardRareMap = {}
    starCardRareMap = {}
    gunSkinPile = []
    crystalItems = []
    for chestDrop in chestDropList:
        chestDropType = dict(chestDrop)["type"]
        if chestDropType == ItemType.Skill:
            rare = dict(chestDrop)["rare"]
            skillCardRareMap.setdefault(rare, []).append(chestDrop)
        elif chestDropType == ItemType.Star:
            rare = dict(chestDrop)["rare"]
            starCardRareMap.setdefault(rare, []).append(chestDrop)
        elif chestDropType == ItemType.GunSkin:
            gunSkinPile.append(chestDrop)
        elif chestDropType == ItemType.Crystal:
            crystalItems.append(chestDrop)
    if ftlog.is_debug():
        ftlog.debug("getChestRewards->skillCardRareMap =", skillCardRareMap, "starCardRareMap =", starCardRareMap)

    # 确定技能卡片概率、随机次数、最小数、最大数
    nCardRate = 1 if random.randint(1, 10000) <= chestConf["nCardRate"] else 0
    rCardRate = 1 if random.randint(1, 10000) <= chestConf["rCardRate"] else 0
    srCardRate = 1 if random.randint(1, 10000) <= chestConf["srCardRate"] else 0
    skillCardRare = {1: [nCardRate, chestConf["nCardRandom"], chestConf["nCardRange"][0], chestConf["nCardRange"][1]],
                     2: [rCardRate, chestConf["rCardRandom"], chestConf["rCardRange"][0], chestConf["rCardRange"][1]],
                     3: [srCardRate, chestConf["srCardRandom"], chestConf["srCardRange"][0], chestConf["srCardRange"][1]]}
    if ftlog.is_debug():
        ftlog.debug("getChestRewards->skillCardRare =", skillCardRare)

    # 非水晶宝箱第一次开宝箱必定出合金飞弹技能卡片（已废弃2020.09.25）
    # openChestCount = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.openChestCount)
    # if not util.isCrystalChest(chestId) and not openChestCount:
    #     itemList = [{"name": 1145, "count": 1}]
    #     rewards = _mergeItemList(rewards, itemList)
    #     ftlog.debug("getChestRewards->assignCardList =", rewards)

    # 根据权重随机出具体的技能卡片
    for rare, skillCardDropList in skillCardRareMap.iteritems():
        if not skillCardRare[rare][0]:
            continue
        for randomCount in xrange(skillCardRare[rare][1]):
            minSkillCard = skillCardRare[rare][2]
            maxSkillCard = skillCardRare[rare][3]
            skillCardList = _randomItemInWeight(skillCardDropList, minSkillCard, maxSkillCard)
            rewards = _mergeItemList(rewards, skillCardList)
    if ftlog.is_debug():
        ftlog.debug("getChestRewards->skillCardList =", rewards)

    # 判断是否达到保底条件，给予指定稀有度范围且保底数量的随机技能卡片
    if chestConf["cardCertain"]:
        skillCardDropList = []
        for rare in chestConf["cardCertainRateRange"]:
            skillCardDropList.extend(skillCardRareMap.get(rare, []))
        skillCardIdList = [skillCardDrop["kindId"] for skillCardDrop in skillCardDropList if skillCardDrop]
        rewardList = [reward["name"] for reward in rewards if reward]
        if skillCardIdList and not (set(skillCardIdList) & set(rewardList)):
            cardCertainList = [{"name": random.choice(skillCardIdList), "count": chestConf["cardCertainNum"]}]
            rewards = _mergeItemList(rewards, cardCertainList)
            if ftlog.is_debug():
                ftlog.debug("getChestRewards->cardCertainList =", cardCertainList)

    # 确定技能升星卡片概率、随机次数、最小数、最大数
    nStarCardRate = 1 if random.randint(1, 10000) <= chestConf["nStarCardRate"] else 0
    rStarCardRate = 1 if random.randint(1, 10000) <= chestConf["rStarCardRate"] else 0
    srStarCardRate = 1 if random.randint(1, 10000) <= chestConf["srStarCardRate"] else 0
    starCardRare = {1: [nStarCardRate, chestConf["nStarCardRandom"], chestConf["nStarCardRange"][0], chestConf["nStarCardRange"][1]],
                    2: [rStarCardRate, chestConf["rStarCardRandom"], chestConf["rStarCardRange"][0], chestConf["rStarCardRange"][1]],
                    3: [srStarCardRate, chestConf["srStarCardRandom"], chestConf["srStarCardRange"][0], chestConf["srStarCardRange"][1]]}
    if ftlog.is_debug():
        ftlog.debug("getChestRewards->starCardRare =", starCardRare)

    # 根据权重随机出具体的技能升星卡片
    for rare, starCardDropList in starCardRareMap.iteritems():
        if not starCardRare[rare][0]:
            continue
        for randomCount in xrange(starCardRare[rare][1]):
            minStarCard = starCardRare[rare][2]
            maxStarCard = starCardRare[rare][3]
            starCardList = _randomItemInWeight(starCardDropList, minStarCard, maxStarCard)
            rewards = _mergeItemList(rewards, starCardList)
    if ftlog.is_debug():
        ftlog.debug("getChestRewards->starCardList =", rewards)

    # 判断是否达到保底条件，给予指定稀有度范围且保底数量的随机技能升星卡片
    if chestConf["starCardCertain"]:
        starCardDropList = []
        for rare in chestConf["starCardCertainRateRange"]:
            starCardDropList.extend(starCardRareMap.get(rare, []))
        starCardIdList = [starCardDrop["kindId"] for starCardDrop in starCardDropList if starCardDrop]
        rewardList = [reward["name"] for reward in rewards if reward]
        if starCardIdList and not (set(starCardIdList) & set(rewardList)):
            starCardCertainList = [{"name": random.choice(starCardIdList), "count": chestConf["starCardCertainNum"]}]
            rewards = _mergeItemList(rewards, starCardCertainList)
            if ftlog.is_debug():
                ftlog.debug("getChestRewards->starCardCertainList =", starCardCertainList)

    # 确定火炮皮肤概率、随机次数、最小数、最大数
    gunSkinRate = 1 if random.randint(1, 10000) <= chestConf["gunSkinRate"] else 0
    gunSkinRare = [gunSkinRate, chestConf["gunSkinRandom"], chestConf["gunSkinRange"][0], chestConf["gunSkinRange"][1]]
    if ftlog.is_debug():
        ftlog.debug("getChestRewards->gunSkinRare =", gunSkinRare)

    # 根据权重随机出具体的火炮皮肤
    if gunSkinRate:
        for randomCount in xrange(gunSkinRare[1]):
            minGunSkin = starCardRare[2]
            maxGunSkin = starCardRare[3]
            gunSkinList = _randomItemInWeight(gunSkinPile, minGunSkin, maxGunSkin)
            rewards = _mergeItemList(rewards, gunSkinList)
    if ftlog.is_debug():
        ftlog.debug("getChestRewards->gunSkinList =", rewards)

    # 确定(黄/紫)水晶概率，随机次数，最小数，最大数
    crystalRate = 1 if random.randint(1, 10000) <= chestConf["crystalRate"] else 0
    crystalData = [crystalRate, chestConf["crystalRandom"], chestConf["crystalRange"][0], chestConf["crystalRange"][1]]
    if ftlog.is_debug():
        ftlog.debug("getChestRewards->crystalData =", crystalData)
    # 根据权重随机出具体的水晶
    if crystalRate:
        for randomCount in xrange(crystalData[1]):
            minCrystal = crystalData[2]
            maxCrystal = crystalData[3]
            crystals = _randomItemInWeight(crystalItems, minCrystal, maxCrystal)
            rewards = _mergeItemList(rewards, crystals)
    if ftlog.is_debug():
        ftlog.debug("getChestRewards->crystals =", rewards)

    # 计算奖券个数
    couponRate = 1 if random.randint(1, 10000) <= chestConf["couponRate"] else 0
    if couponRate:
        couponCount = random.randint(chestConf["couponRange"][0], chestConf["couponRange"][1])
        if couponCount > 0:
            coupon = {"name": COUPON_KINDID, "count": couponCount}
            rewards.append(coupon)

    # 计算海星个数
    starfishRate = 1 if random.randint(1, 10000) <= chestConf["starfishRate"] else 0
    if starfishRate:
        starfishCount = random.randint(chestConf["starfishRange"][0], chestConf["starfishRange"][1])
        if starfishCount > 0:
            starfish = {"name": STARFISH_KINDID, "count": starfishCount}
            rewards.append(starfish)

    # 计算冷却个数
    coolDownRate = 1 if random.randint(1, 10000) <= chestConf["coolDownRate"] else 0
    if coolDownRate:
        coolDownCount = random.randint(chestConf["coolDownRange"][0], chestConf["coolDownRange"][1])
        if coolDownCount > 0:
            coolDown = {"name": SKILLCD_KINDID, "count": coolDownCount}
            rewards.append(coolDown)

    # 计算青铜招财珠个数
    bronzeBulletRate = 1 if random.randint(1, 10000) <= chestConf["bronzeBulletRate"] else 0
    if bronzeBulletRate:
        bronzeBulletCount = random.randint(chestConf["bronzeBulletRange"][0], chestConf["bronzeBulletRange"][1])
        if bronzeBulletCount > 0:
            bronzeBullet = {"name": BRONZE_BULLET_KINDID, "count": bronzeBulletCount}
            rewards.append(bronzeBullet)
    # 计算白银招财珠个数
    silverBulletRate = 1 if random.randint(1, 10000) <= chestConf["silverBulletRate"] else 0
    if silverBulletRate:
        silverBulletCount = random.randint(chestConf["silverBulletRange"][0], chestConf["silverBulletRange"][1])
        if silverBulletCount > 0:
            silverBullet = {"name": SILVER_BULLET_KINDID, "count": silverBulletCount}
            rewards.append(silverBullet)
    # 计算黄金招财珠个数
    goldBulletRate = 1 if random.randint(1, 10000) <= chestConf["goldBulletRate"] else 0
    if goldBulletRate:
        goldBulletCount = random.randint(chestConf["goldBulletRange"][0], chestConf["goldBulletRange"][1])
        if goldBulletCount > 0:
            goldBullet = {"name": GOLD_BULLET_KINDID, "count": goldBulletCount}
            rewards.append(goldBullet)

    # 计算红宝石个数
    rubyRate = 1 if random.randint(1, 10000) <= chestConf["rubyRate"] else 0
    if rubyRate:
        rubyCount = random.randint(chestConf["rubyRange"][0], chestConf["rubyRange"][1])
        if rubyCount > 0:
            ruby = {"name": RUBY_KINDID, "count": rubyCount}
            rewards.append(ruby)

    # 计算物品个数
    for _item in chestConf.get("itemsData", []):
        rate = 1 if random.randint(1, 10000) <= _item["rate"] else 0
        if rate:
            count = random.randint(_item["min"], _item["max"])
            if count > 0:
                val = {"name": _item["kindId"], "count": count}
                rewards.append(val)
    _convertOverflowCardToCoin(userId, rewards)
    return rewards


def getChestCardQuantitativeRange(cardRate, cardRandom, cardRange):
    """
    获得宝箱可开出某种卡片的数量范围
    """
    cardMinCount = 0 if cardRate < 10000 else cardRandom * cardRange[0]
    cardMaxCount = cardRandom * cardRange[1]
    return cardMinCount, cardMaxCount


def getChestDropList(chestConf, itemType=None):
    """
    根据宝箱物品等级确定可获得物品范围
    """
    chestLevelRange = chestConf["levelRange"]
    chestDropList = []
    for level in chestLevelRange:
        chestLevelList = config.getChestDropConf(level)
        for chestDrop in chestLevelList:
            if itemType:
                if chestDrop["type"] == itemType:
                    chestDropList.append(chestDrop)
            else:
                chestDropList.append(chestDrop)
    def cmpRare(x, y):
        if x["rare"] > y["rare"]:
            return 1
        elif x["rare"] < y["rare"]:
            return -1
        else:
            if x["kindId"] < y["kindId"]:
                return 1
            else:
                return -1
    chestDropList.sort(cmp=cmpRare, reverse=True)
    ftlog.debug("getChestRewards->chestDropList", chestDropList)
    return chestDropList


def deliveryChestRewards(userId, chestId, rewards, eventId=None, fromType=None, param01=0, param02=0):
    """
    发放宝箱物品
    """
    if not rewards:
        ftlog.error("deliveryChestRewards->not rewards", userId, chestId)
        return 4
    if not eventId:
        eventId = "BI_NFISH_OPEN_CHEST_REWARDS"
    code = util.addRewards(userId, rewards, eventId, int(chestId), param01=param01, param02=param02)
    if code != 0:
        ftlog.error("deliveryChestRewards->add gain error", userId, chestId, rewards)
        return code
    gamedata.incrGameAttr(userId, FISH_GAMEID, GameData.openChestCount, 1)
    bireport.reportGameEvent("BI_NFISH_GE_CHEST_OPEN", userId, FISH_GAMEID, 0,
                             0, int(chestId), 0, 0, 0, [], util.getClientId(userId))
    if fromType:
        from newfish.game import TGFish
        from newfish.entity.event import GainChestEvent
        event = GainChestEvent(userId, FISH_GAMEID, chestId, fromType)
        TGFish.getEventBus().publishEvent(event)
    return 0


def _randomItemInWeight(chestDropList, min, max):
    """
    权重随机算法
    """
    itemList = []
    itemTotalWeight = sum([dict(chestDrop)["weight"] for chestDrop in chestDropList if chestDrop])
    if ftlog.is_debug():
        ftlog.debug("_randomItemInWeight->", chestDropList, itemTotalWeight)
    if itemTotalWeight > 0:
        itemWeight = random.randint(1, itemTotalWeight)
        for chestDrop in chestDropList:
            if chestDrop and itemWeight - chestDrop["weight"] <= 0:
                item = {"name": chestDrop["kindId"], "count": random.randint(min, max)}
                itemList.append(item)
                break
            itemWeight -= chestDrop["weight"]
    return itemList


def _mergeItemList(itemList, newItemList):
    """
    合并相同道具
    """
    if ftlog.is_debug():
        ftlog.debug("_mergeItemList->", itemList, newItemList)
    if not newItemList:
        return itemList
    kindIdList = [item["name"] for item in itemList if item]
    newKindIdList = [item["name"] for item in newItemList if item]
    sameKindIdList = set(kindIdList) & set(newKindIdList)
    if sameKindIdList:
        for kindId in sameKindIdList:
            index = kindIdList.index(kindId)
            newIndex = newKindIdList.index(kindId)
            item = itemList[index]
            newItem = newItemList[newIndex]
            if item["name"] == newItem["name"]:
                item["count"] += newItem["count"]
    else:
        itemList.extend(newItemList)
    if ftlog.is_debug():
        ftlog.debug("_mergeItemList->", itemList)
    return itemList


def _needCoinAsOpenChest(chestId, timeLeft):
    """
    开启宝箱所需金币数
    """
    coin = math.ceil(timeLeft / 60.0) * max(config.getChestConf(chestId)["openCoin"], 1)
    return int(max(100, coin))


def _convertOverflowCardToCoin(userId, rewards):
    """
    溢出卡片转换为金币
    """
    for reward in rewards:
        kindId = reward["name"]
        if kindId in config.skillCardKindIdMap:
            skillId = config.skillCardKindIdMap[kindId]
            skill = skill_system.getSkill(userId, skillId)
            level = skill[skill_system.INDEX_ORIGINAL_LEVEL]
            if level >= skill_system.MAX_ORIGINAL_LEVEL:
                _convertCardReward(kindId, reward)
                continue
        elif kindId in config.starCardKindIdMap:
            skillId = config.starCardKindIdMap[kindId]
            skill = skill_system.getSkill(userId, skillId)
            level = skill[skill_system.INDEX_STAR_LEVEL]
            if level >= skill_system.MAX_STAR_LEVEL:
                _convertCardReward(kindId, reward)
                continue


def _convertCardReward(kindId, reward):
    """
    卡片奖励数据转换
    """
    chestDropConf = config.getChestDropConf()
    convertCoin = chestDropConf[str(kindId)]["convertCoin"]
    reward["kindId"] = kindId
    reward["kindCount"] = reward["count"]
    reward["name"] = CHIP_KINDID
    reward["count"] *= convertCoin


def _triggerTYOpenItemEvent(event):
    userId = event.userId
    itemKind = event.item.itemKind
    lang = util.getLanguage(userId)
    for key, value in config.getChestConf().iteritems():
        if value["kindId"] == itemKind.kindId:
            from hall.entity import halluser
            from hall.entity.todotask import TodoTaskShowInfo, TodoTaskHelper
            from newfish.entity import mail_system
            message = config.getMultiLangTextConf("ID_OPEN_ITEM_GET_REWARD_MSG", lang=lang) % value["name"]
            GameMsg.sendPrivate(FISH_GAMEID, userId, 0, message)
            todoTask = TodoTaskShowInfo(message)
            TodoTaskHelper.sendTodoTask(FISH_GAMEID, userId, todoTask)
            halluser.ensureGameDataExists(userId, FISH_GAMEID, util.getClientId(userId))
            message = config.getMultiLangTextConf("ID_USE_ITEM_GET_REWARD_MSG", lang=lang).format(itemKind.displayName, value["name"])
            rewards = [{"name": value["chestId"], "count": 1}]
            mail_system.sendSystemMail(userId, mail_system.MailRewardType.ChestReward, rewards, message)
            break


_inited = False


def initialize():
    ftlog.info("newfish chest_system initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from hall.game import TGHall
        TGHall.getEventBus().subscribe(TYOpenItemEvent, _triggerTYOpenItemEvent)
    ftlog.info("newfish chest_system initialize end")