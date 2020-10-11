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
    chestConf = config.getChestConf(chestId)
    chestInfo = {}







    return chestInfo


def getChestRewards(userId, chestId):
    """
    获取宝箱物品
    """
    rewards = []
    return rewards


def deliveryChestRewards(userId, chestId, rewards, eventId=None, fromType=None, param01=0, param02=0):
    """
    发放宝箱物品
    """
    return 0



def _triggerTYOpenItemEvent(event):
    """触发开启道具的事件"""
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