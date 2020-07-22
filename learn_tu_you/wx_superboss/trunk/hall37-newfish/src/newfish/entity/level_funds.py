#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/30
"""
成长基金
"""

import json

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.configure import pokerconf
from poker.entity.dao import daobase, gamedata
from newfish.entity import config, util, vip_system, module_tip
from newfish.entity.config import FISH_GAMEID, BT_DIRECT, BT_VOUCHER, VOUCHER_KINDID, CLASSIC_MODE
from newfish.entity.redis_keys import GameData, UserData
from newfish.entity.msg import GameMsg
from newfish.entity.chest import chest_system


def _getRdKey(userId, mode):
    """
    获取成长基金存档key
    """
    if mode == CLASSIC_MODE:
        return UserData.levelFundsData % (FISH_GAMEID, userId)
    else:
        return UserData.levelFundsData_m % (FISH_GAMEID, userId)


def _getRewardsState(userId, mode):
    """
    获取玩家已领取奖励数据 {"10": [2, 2], "11": [2, 2], "12": [2, 2]}
    """
    lf_rewards = daobase.executeUserCmd(userId, "HGET", _getRdKey(userId, mode), GameData.lf_rewards) or "{}"   # {等级:[免费,付费]}
    lf_rewards = json.loads(lf_rewards)
    return lf_rewards


def _getBoughtFunds(userId, mode):
    """
    获取玩家已购买基金索引数据 [1, 2, 3, 4, 6]
    """
    lf_funds = daobase.executeUserCmd(userId, "HGET", _getRdKey(userId, mode), GameData.lf_funds) or "[]"
    lf_funds = json.loads(lf_funds)
    return lf_funds


def _getFundsList(userId, clientId, mode):
    """
    获取玩家可以使用的成长基金索引列表
    """
    fundsConf = config.getLevelFundsConf(clientId, mode)
    canBuyIdxs = fundsConf.get("canBuyIdx")
    funds = fundsConf.get("funds")
    lf_funds = _getBoughtFunds(userId, mode)
    userIdxs = {}
    for idx in lf_funds + canBuyIdxs:
        if len(funds) >= idx > 0:
            _type = funds[idx - 1].get("type")
            if str(_type) not in userIdxs:
                userIdxs[str(_type)] = idx
    if ftlog.is_debug():
        ftlog.debug("level_funds, userId =", userId, "clientId =", clientId, "mode =", mode, "canBuyIdxs =", canBuyIdxs, "userIdxs =", userIdxs, "lf_funds =", lf_funds)
    return sorted(userIdxs.values())


def _getLevelFundsRewardState(userId, clientId, idx, mode, lf_rewards=None, lf_funds=None):
    """
    获取玩家指定成长基金奖励领取状态
    """
    lf_rewards = lf_rewards or _getRewardsState(userId, mode)
    lf_funds = lf_funds or _getBoughtFunds(userId, mode)
    userLv = util.getGunLevelVal(userId, mode)
    rewardsState = []
    fundsConf = config.getLevelFundsConf(clientId, mode)
    rewardsConf = fundsConf.get("rewards", {})
    levelRewardsConf = rewardsConf.get(str(idx), [])

    hasTip = False
    for lvData in levelRewardsConf:
        lv = lvData["level"]
        rewardsData = lf_rewards.get(str(lv), [0, 0])
        # 0表示未领取，1表示可领取，2表示已领取，数据库存档中只存储0和2两种状态.
        free_state = 1 if rewardsData[0] == 0 and lv <= userLv else rewardsData[0]
        funds_state = 1 if idx in lf_funds and rewardsData[1] == 0 and lv <= userLv else rewardsData[1]
        rewardsState.append({
            "level": lv,
            "free_rewards": lvData["free_rewards"],
            "funds_rewards": lvData["funds_rewards"],
            "free_state": free_state,
            "funds_state": funds_state
        })
        hasTip = hasTip or free_state == 1 or funds_state == 1
    if ftlog.is_debug():
        ftlog.debug("level_funds, userId =", userId, "idx =", idx, "lf_funds =", lf_funds, "lf_rewards =", lf_rewards,
                    "userLv =", userLv, "hasTip =", hasTip, "rewardsState =", rewardsState, "mode =", mode)
    return hasTip, rewardsState


def getLevelFundsData(userId, clientId, mode):
    """
    获取成长基金数据
    """
    module_tip.resetModuleTipEvent(userId, "levelfunds")
    userLv = util.getGunLevelVal(userId, mode)
    message = MsgPack()
    message.setCmd("levelFundsData")
    message.setResult("gameId", config.FISH_GAMEID)
    message.setResult("userId", userId)
    message.setResult("level", userLv)
    fundsList = []
    lang = util.getLanguage(userId)
    fundsConf = config.getLevelFundsConf(clientId, mode)
    funds = fundsConf.get("funds", [])
    userIdxs = _getFundsList(userId, clientId, mode)            # 获取所有可买的基金
    lf_rewards = _getRewardsState(userId, mode)
    lf_funds = _getBoughtFunds(userId, mode)

    if set(userIdxs) == set(lf_funds):
        isAllTaken = True
        rewardsConf = fundsConf.get("rewards")
        for idx in userIdxs:
            if not isAllTaken:
                break
            rewardsData = rewardsConf.get(str(idx), [])
            for lvData in rewardsData:
                lv = lvData["level"]
                # 判断免费和基金奖励的领取状态是否都为2，即均为已领取状态.
                if userLv < lv or sum(lf_rewards.get(str(lv), [0, 0])) != 4:
                    isAllTaken = False
                    break
    else:
        isAllTaken = False
    addTipPIds = []
    isIn, roomId, _, _ = util.isInFishTable(userId)
    canShow = not isIn
    if canShow and not isAllTaken and util.isFinishAllRedTask(userId):
        for idx in userIdxs:
            productConf = funds[idx - 1]
            _funds = {}
            fundsList.append(_funds)
            productId = productConf.get("productId")
            _funds["Id"] = productId
            _funds["state"] = 1 if idx in lf_funds else 0
            _funds["title"] = productConf.get("title")
            _funds["name"] = config.getMultiLangTextConf(productConf.get("name"), lang=lang)
            _funds["price_direct"] = productConf.get("price_direct")
            _funds["price_diamond"] = productConf.get("price_diamond")
            _funds["buyType"] = productConf.get("buyType")
            _funds["otherBuyType"] = productConf.get("otherBuyType")
            from newfish.entity import store
            _funds["otherProductInfo"] = store.getOtherBuyProduct(productConf.get("otherBuyType"), productConf.get("buyType"))
            hasTip, _funds["rewardsState"] = _getLevelFundsRewardState(userId, clientId, idx, mode, lf_rewards, lf_funds)
            if hasTip:
                addTipPIds.append(productId)
    message.setResult("fundsList", fundsList)
    router.sendToUser(message, userId)
    if addTipPIds:
        module_tip.addModuleTipEvent(userId, "levelfunds", addTipPIds)
    if ftlog.is_debug():
        ftlog.debug("level_funds, userId =", userId, "mode =", mode, "message =", message)


def getLevelFundsRewards(userId, clientId, productId, level=0, rewardType=0):
    """
    领取基金奖励
    """
    code = 0
    rewards = []
    rewardsState = []
    isQuickGet = (level == 0)
    # 根据商品Id确定游戏模式.
    mode = config.CLASSIC_MODE
    for _m in [config.CLASSIC_MODE, config.MULTIPLE_MODE]:
        fundsConf = config.getLevelFundsConf(clientId, _m)
        for val in fundsConf.get("funds"):
            if val.get("productId") == productId:
                mode = _m
                break
    lf_rewards = _getRewardsState(userId, mode)
    lf_funds = _getBoughtFunds(userId, mode)
    userLv = util.getGunLevelVal(userId, mode)
    fundsConf = config.getLevelFundsConf(clientId, mode)
    funds = fundsConf.get("funds")
    rewardsConf = fundsConf.get("rewards")
    rewardsTypeStr = ["free_rewards", "funds_rewards"]
    if rewardType in [0, 1]:                                        # 0:免费,1:基金
        for val in funds:
            if val.get("productId") == productId:
                rewardsData = rewardsConf.get(str(val["idx"]))
                isChanged = False
                for lvData in rewardsData:
                    lv = lvData["level"]
                    if (isQuickGet and lv <= userLv) or (not isQuickGet and lv == level):
                        lf_rewards.setdefault(str(lv), [0, 0])
                        # 一键领取时需要检测两种奖励是否可以领取。
                        typeList = [rewardType]
                        if isQuickGet:
                            typeList = [0, 1]
                        for _type in typeList:
                            if lf_rewards[str(lv)][_type] == 0 and (_type == 0 or val["idx"] in lf_funds):
                                isChanged = True
                                lf_rewards[str(lv)][_type] = 2
                                for _reward in lvData[rewardsTypeStr[_type]]:
                                    itemId = _reward["name"]
                                    if util.isChestRewardId(itemId):
                                        chestRewards = {}
                                        chestRewards["chestId"] = itemId
                                        chestRewards["rewards"] = chest_system.getChestRewards(userId, itemId)
                                        chest_system.deliveryChestRewards(userId, itemId, chestRewards["rewards"], "BI_NFISH_GET_LEVEL_FUNDS", param01=lv, param02=_type)
                                        rewards.append(chestRewards)
                                    else:
                                        rewards.append([_reward])
                                        util.addRewards(userId, [_reward], "BI_NFISH_GET_LEVEL_FUNDS", param01=lv, param02=_type)
                                if _type == 0 and lvData.get("rechargeBonus", 0) > 0:
                                    util.incrUserRechargeBonus(userId, lvData["rechargeBonus"])
                if isChanged:
                    daobase.executeUserCmd(userId, "HSET", _getRdKey(userId, mode), GameData.lf_rewards, json.dumps(lf_rewards))
                hasTip, rewardsState = _getLevelFundsRewardState(userId, clientId, val["idx"], mode, lf_funds=lf_funds, lf_rewards=lf_rewards)
                if not hasTip:
                    module_tip.cancelModuleTipEvent(userId, "levelfunds", productId)
                break
        else:
            code = 1
    else:
        code = 2
    message = MsgPack()
    message.setCmd("levelFundsRewards")
    message.setResult("gameId", config.FISH_GAMEID)
    message.setResult("userId", userId)
    message.setResult("productId", productId)
    message.setResult("code", code)
    message.setResult("rewards", rewards)
    message.setResult("rewardType", rewardType)
    message.setResult("rewardsState", rewardsState)
    router.sendToUser(message, userId)
    if ftlog.is_debug():
        ftlog.debug("level_funds, userId =", userId, "mode =", mode, "message =", message)


def doBuyLevelFunds(userId, clientId, buyType, productId):
    """
    购买成长基金
    """
    # 根据商品Id确定游戏模式.
    mode = config.CLASSIC_MODE
    for _m in [config.CLASSIC_MODE, config.MULTIPLE_MODE]:
        fundsConf = config.getLevelFundsConf(clientId, _m)
        for val in fundsConf.get("funds"):
            if val.get("productId") == productId:
                mode = _m
                break
    fundsConf = config.getLevelFundsConf(clientId, mode)
    funds = fundsConf.get("funds")
    productConf = None
    canBuyIdxs = fundsConf.get("canBuyIdx")
    for val in funds:
        if val.get("idx") in canBuyIdxs and val.get("productId") == productId:
            productConf = val
            break
    if not productConf:
        sendBuyLevelFundsRet(userId, clientId, productId, 0, 5, mode)
        return

    buyType = buyType or productConf.get("buyType")
    lf_funds = daobase.executeUserCmd(userId, "HGET", _getRdKey(userId, mode), GameData.lf_funds) or "[]"
    lf_funds = json.loads(lf_funds)
    lf_types = [val.get("type") for val in funds if val.get("idx") in lf_funds]
    if productConf.get("idx") in lf_funds or productConf.get("type") in lf_types:       # 重复购买同一商品或是同一类型的商品.
        sendBuyLevelFundsRet(userId, clientId, productId, 0, 6, mode)
        return
    lang = util.getLanguage(userId, clientId)
    productName = config.getMultiLangTextConf(productConf["name"], lang=lang)
    if buyType == BT_DIRECT or config.isThirdBuyType(buyType):                          # 直充购买或者三方渠道支付
        message = config.getMultiLangTextConf("ID_BUY_GIFT_RET_BY_DRIECT", lang=lang).format(productName, productName)
        GameMsg.sendPrivate(FISH_GAMEID, userId, 0, message)
        code = 0
    else:
        # 使用代购券购买
        if productConf.get("otherBuyType", {}).get(buyType):
            price = productConf.get("otherBuyType", {}).get(buyType)
            if buyType == BT_VOUCHER:
                _consume = [{"name": VOUCHER_KINDID, "count": abs(price)}]
                _ret = util.consumeItems(userId, _consume, "BI_NFISH_BUY_ITEM_CONSUME", param01=productId)
                if not _ret:
                    code = 2
                else:
                    vip_system.addUserVipExp(FISH_GAMEID, userId, abs(price) * 10, "BUY_PRODUCT", pokerconf.productIdToNumber(productId), productId, rmbs=abs(price))
                    message = config.getMultiLangTextConf("ID_BUY_GIFT_RET_BY_VOUCHER", lang=lang).format(price, productName, productName)
                    GameMsg.sendPrivate(FISH_GAMEID, userId, 0, message)
                    code = 0
            else:
                code = 3
        else:
            code = 4
    if code == 0:
        util.addProductBuyEvent(userId, productId, clientId)
        lf_funds.append(productConf.get("idx"))
        daobase.executeUserCmd(userId, "HSET", _getRdKey(userId, mode), GameData.lf_funds, json.dumps(lf_funds))
    sendBuyLevelFundsRet(userId, clientId, productId, productConf.get("idx"), code, mode)


def sendBuyLevelFundsRet(userId, clientId, productId, idx, code, mode):
    """
    返回购买成长基金结果
    """
    message = MsgPack()
    message.setCmd("buyLevelFunds")
    message.setResult("gameId", config.FISH_GAMEID)
    message.setResult("userId", userId)
    message.setResult("productId", productId)
    message.setResult("code", code)
    rewardsState = []
    if code == 0:
        message.setResult("state", 1)
        hasTip, rewardsState = _getLevelFundsRewardState(userId, clientId, idx, mode)
        if hasTip:
            module_tip.addModuleTipEvent(userId, "levelfunds", productId)
        else:
            module_tip.cancelModuleTipEvent(userId, "levelfunds", productId)
    message.setResult("rewardsState", rewardsState)
    router.sendToUser(message, userId)
    if ftlog.is_debug():
        ftlog.debug("level_funds, userId =", userId, "mode =", mode, "message =", message)


def _triggerChargeNotifyEvent(event):
    """
    直充购买商品成功事件
    """
    ftlog.info(
        "level_funds._triggerChargeNotifyEvent->", "userId =", event.userId, "gameId =", event.gameId,
        "rmbs =", event.rmbs, "productId =", event.productId, "clientId =", event.clientId
    )
    userId = event.userId
    productId = event.productId
    fundsConf = config.getLevelFundsConf(event.clientId, config.CLASSIC_MODE)
    fundsConf2 = config.getLevelFundsConf(event.clientId, config.MULTIPLE_MODE)
    funds = fundsConf.get("funds") + fundsConf2.get("funds")
    for val in funds:
        if val.get("productId") == productId:
            doBuyLevelFunds(userId, event.clientId, None, productId)
            break


def _triggerLevelUpEvent(event):
    """
    炮台升级/升倍率事件
    """
    userId = event.userId
    clientId = util.getClientId(userId)
    mode = event.gameMode

    fundsConf = config.getLevelFundsConf(clientId, mode)
    funds = fundsConf.get("funds", [])
    userIdxs = _getFundsList(userId, clientId, mode)
    lf_rewards = _getRewardsState(userId, mode)
    lf_funds = _getBoughtFunds(userId, mode)
    addTipPIds = []
    for idx in userIdxs:
        productId = funds[idx - 1]["productId"]
        hasTip, _ = _getLevelFundsRewardState(userId, clientId, idx, mode, lf_rewards, lf_funds)
        if hasTip:
            addTipPIds.append(productId)
    if addTipPIds:
        module_tip.addModuleTipEvent(userId, "levelfunds", addTipPIds)
    if ftlog.is_debug():
        ftlog.debug("level_funds, userId =", userId, "mode =", mode)


_inited = False


def initialize():
    ftlog.debug("newfish level_funds initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from poker.entity.events.tyevent import ChargeNotifyEvent
        from hall.game import TGHall
        from newfish.game import TGFish
        from newfish.entity.event import NFChargeNotifyEvent, LevelUpEvent
        TGHall.getEventBus().subscribe(ChargeNotifyEvent, _triggerChargeNotifyEvent)
        TGFish.getEventBus().subscribe(NFChargeNotifyEvent, _triggerChargeNotifyEvent)
        TGFish.getEventBus().subscribe(LevelUpEvent, _triggerLevelUpEvent)
    ftlog.debug("newfish level_funds initialize end")
