#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/22

import json

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.util import webpage
from poker.entity.dao import userchip, gamedata
from poker.entity.configure import gdata
from hall.entity import hallvip
from newfish.entity import config, util
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData
from newfish.entity.event import UserVipExpChangeEvent


def sendFishVipInfo(userId):
    """
    发送VIP特权信息
    """
    userVip = hallvip.userVipSystem.getUserVip(userId)
    vipLevelObj = userVip.vipLevel
    vipGiftBought = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.vipGiftBought, [])
    lang = util.getLanguage(userId)
    levels = []
    for level in sorted(map(int, config.getVipConf().keys())):
        if level == 0 or (vipLevelObj.level <= 6 and level > 8):
            continue
        vipConf = config.getVipConf(level)
        vip = {}
        vip["level"] = vipConf["vipLv"]
        # vip["desc"] = vipConf["vipDesc"]
        vip["desc"] = config.getMultiLangTextConf(vipConf["vipDesc"], lang=lang)
        vip["originalPrice"] = vipConf["originalPrice"]
        vip["price"] = vipConf["price"]
        vip["bought"] = 1 if vipConf["vipLv"] in vipGiftBought else 0
        vip["gift"] = vipConf["vipGift"]
        vip["canSetVipShow"] = vipConf.get("setVipShow", 0)
        levels.append(vip)
    totalExp = vipLevelObj.nextVipLevel.vipExp if vipLevelObj.nextVipLevel else vipLevelObj.vipExp
    mo = MsgPack()
    mo.setCmd("fish_vip_info")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("vipLevel", vipLevelObj.level)
    mo.setResult("exp", [userVip.vipExp, totalExp])
    mo.setResult("levels", levels)
    mo.setResult("showVip", util.isVipShow(userId))
    vipConf = config.getVipConf(vipLevelObj.level)
    mo.setResult("convert1137ToDRate", vipConf.get("convert1137ToDRate", 1))
    mo.setResult("convert1429ToDRate", vipConf.get("convert1429ToDRate", 0))
    mo.setResult("convert1430ToDRate", vipConf.get("convert1430ToDRate", 0))
    mo.setResult("convert1431ToDRate", vipConf.get("convert1431ToDRate", 0))
    router.sendToUser(mo, userId)


def buyFishVipGift(userId, level):
    """
    购买特定VIP等级的礼包
    """
    mo = MsgPack()
    mo.setCmd("buy_fish_vip_gift")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("level", level)
    vipLevel = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
    code = 1
    if vipLevel >= level:
        vipConf = config.getVipConf(level)
        if vipConf:
            price = vipConf["price"]
            rewards = vipConf["vipGift"]
            if userchip.getChip(userId) >= price:
                vipGiftBought = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.vipGiftBought, [])
                # 服务器限制购买次数.
                if level not in vipGiftBought:
                    util.addRewards(userId, [{"name": config.CHIP_KINDID, "count": -abs(price)}],
                                    "BI_NFISH_BUY_ITEM_CONSUME", level)
                    code = util.addRewards(userId, rewards, "BI_NFISH_BUY_ITEM_GAIN", level)
                    vipGiftBought.append(level)
                    gamedata.setGameAttr(userId, FISH_GAMEID, GameData.vipGiftBought, json.dumps(vipGiftBought))
                else:
                    return
            if code == 0:
                mo.setResult("rewards", rewards)
    mo.setResult("code", code)
    router.sendToUser(mo, userId)


def getMatchVipAddition(userId, vipLevel=None):
    """
    获取回馈赛VIP积分加成
    """
    vipConf = config.getVipConf()
    vipLevel = vipLevel or hallvip.userVipSystem.getUserVip(userId).vipLevel.level
    if vipLevel > len(vipConf.keys()) - 1:
        vipLevel = len(vipConf.keys()) - 1
    matchAddition = vipConf.get(str(vipLevel), {}).get("matchAddition", 0)
    return matchAddition


def addUserVipExp(gameId, userId, toAddExp, eventId, intEventParam, productId, rmbs=-1, isAddVipExp=True):
    """
    增加VIP经验值
    """
    rmbs = int(rmbs)
    if rmbs == -1 and toAddExp >= 10:
        rmbs = toAddExp / 10
    if isAddVipExp:
        hallvip.userVipSystem.addUserVipExp(gameId, userId, toAddExp, eventId, intEventParam)
    else:# 自己处理vip升级事件.
        from hall.game import TGHall
        from hall.entity.hallvip import TYUserVipLevelUpEvent
        vipExp = hallvip.userVipSystem.getUserVip(userId).vipExp
        oldVipLevel = hallvip.vipSystem.findVipLevelByVipExp(vipExp - toAddExp)
        userVip = hallvip.userVipSystem.getUserVip(userId)
        ftlog.debug("check vip level change", userId, vipExp, toAddExp, oldVipLevel.level,
                    userVip.vipLevel.level)
        if oldVipLevel.level != userVip.vipLevel.level:
            lv_event = TYUserVipLevelUpEvent(FISH_GAMEID, userId, oldVipLevel, userVip, [], 0, 0)
            TGHall.getEventBus().publishEvent(lv_event)
    # vip经验发生变化.
    from newfish.game import TGFish
    event = UserVipExpChangeEvent(userId, gameId, toAddExp)
    TGFish.getEventBus().publishEvent(event)
    ftlog.debug("addUserVipExp----->event", gameId, userId, toAddExp, eventId, intEventParam, rmbs, isAddVipExp)
    # 上报购买商品事件.
    loginDays = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.loginDays)
    userLevel = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.level)
    isIn, roomId, tableId, _ = util.isInFishTable(userId)
    if isIn:
        from newfish.servers.table.rpc import table_remote
        table_remote.buyProduct(roomId, tableId, userId, intEventParam, userLevel, loginDays)
    else:
        from poker.entity.biz import bireport
        userChip = userchip.getUserChipAll(userId)
        bireport.reportGameEvent("BI_NFISH_BUY_PRODUCT", userId, FISH_GAMEID, roomId,
                                intEventParam, userLevel, 0, 0, 0, [], util.getClientId(userId), loginDays, userChip)
        # ftlog.debug("BI_NFISH_BUY_PRODUCT", userId, roomId, intEventParam, userLevel, util.getClientId(userId), userChip)
    updateUserDataByRecharge(userId, productId, rmbs)


def updateUserDataByRecharge(userId, productId, rmbs):
    """
    充值后更新用户数据
    """
    if rmbs > 0:
        from newfish.entity.fishactivity import fish_activity_system
        fish_activity_system.accumulateRecharge(userId, productId, rmbs)
        from newfish.entity.quest import quest_system
        quest_system.incrRecharge(userId, rmbs)
        addUserLuckyValue(userId, productId, rmbs)
        addUserCredit(userId, productId, rmbs)


def addUserLuckyValue(userId, productId, rmbs):
    """
    增加用户比赛场幸运值
    """
    # 玩家每充值1元，所有比赛场的幸运值加0.5
    from newfish.entity.match_record import MatchRecord
    vip = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
    for roomId in [44101, 44102, 44103, 44104]:
        key = "initLuckyValue:%d" % int(roomId)
        initVal = config.getVipConf(vip).get(key, 10000)
        record = MatchRecord.loadRecord(FISH_GAMEID, userId, roomId)
        record.luckyValue = min(record.luckyValue + int(0.5 * rmbs), initVal)
        MatchRecord.saveRecord(FISH_GAMEID, userId, roomId, record)


def addUserCredit(userId, productId, rmbs):
    """
    增加用户微信公众号积分商城积分
    """
    # 玩家每充值1元，增加10积分
    if gdata.mode() == gdata.RUN_MODE_ONLINE:
        requestUrl = "http://wx.dnale4.cn/"
    else:
        requestUrl = "http://wxtest.tuyoo.com/"
    response = None
    try:
        params = {
            "act": "xxfishpoint.xxfishHandel",
            "type": 1,
            "typename": u"游戏充值",
            "account_num": rmbs * 10,
            "user_id": userId
        }
        params["code"] = util.httpParamsSign(params)
        response, _ = webpage.webget(requestUrl, querys=params, method_="GET")
        response = json.loads(response)
        if response.get("code") != 0:
            ftlog.error("addUserCredit->error", "userId=", userId, "productId=", productId, "rmbs=", rmbs, "response=", response)
        else:
            ftlog.info("addUserCredit->success", "userId=", userId, "productId=", productId, "rmbs=", rmbs, "response=", response)
    except:
        ftlog.error("addUserCredit->error", "userId=", userId, "productId=", productId, "rmbs=", rmbs, "response=", response)


def sendVipCirculateInfo(userId):
    """
    道具流通数量限制信息
    """
    levels = {}
    for level in sorted(map(int, config.getVipConf().keys())):
        levelDict = {}
        vipConf = config.getVipConf(level)
        levelDict["present:1408"] = vipConf.get("vipPresentCount:1408", 0)
        levelDict["present:1429"] = vipConf.get("vipPresentCount:1429", 0)
        levelDict["present:1430"] = vipConf.get("vipPresentCount:1430", 0)
        levelDict["present:1431"] = vipConf.get("vipPresentCount:1431", 0)
        levelDict["present:1193"] = vipConf.get("vipPresentCount:1193", 0)
        levelDict["present:1194"] = vipConf.get("vipPresentCount:1194", 0)
        levelDict["receive:1193"] = vipConf.get("vipReceiveCount:1193", 0)
        levelDict["receive:1194"] = vipConf.get("vipReceiveCount:1194", 0)
        levels[level] = levelDict
    mo = MsgPack()
    mo.setCmd("fish_circulate_info")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    mo.setResult("levels", levels)
    router.sendToUser(mo, userId)