#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6

import json
import traceback

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.entity.dao import daobase, userdata
from poker.entity.configure import gdata
from poker.protocol.rpccore import markRpcCall
from poker.entity.biz.exceptions import TYBizException
from newfish.entity.config import FISH_GAMEID
from newfish.entity import util
from newfish.entity import config
from newfish.entity.msg import GameMsg
from newfish.servers.util.rpc import user_rpc


@markRpcCall(groupName="roomId", lockName="", syncCall=1)
def ftBind(roomId, tableId, ftTable):
    """
    绑定桌子
    :param roomId: 房间Id
    :param tableId: 桌子Id
    :param ftTable:
    :return:
    """
    try:
        room = gdata.rooms()[roomId]
        table = room.maptable[tableId]
        return table.doFTBind(ftTable)
    except TYBizException, e:
        return {"errorCode": e.errorCode, "message": e.message}


@markRpcCall(groupName="roomId", lockName="", syncCall=1)
def ftEnter(roomId, tableId, userId, ftId, seatId):
    """进入桌子"""
    try:
        room = gdata.rooms()[roomId]
        table = room.maptable[tableId]
        return table.doFTEnter(ftId, userId, seatId)
    except TYBizException, e:
        return {"errorCode": e.errorCode, "message": e.message}


@markRpcCall(groupName="roomId", lockName="", syncCall=1)
def quickStart(roomId, tableId, userId, clientId, extParams):
    """快速进入GT进程"""
    ftlog.debug("quickStart", userId, roomId, tableId, clientId)
    try:
        room = gdata.rooms()[roomId]
        room.quickStartInGT(roomId, tableId, userId, clientId, extParams)
    except Exception, e:
        ftlog.error("quickStart error", roomId, tableId, userId, clientId, extParams, traceback.format_exc())
    return 0


@markRpcCall(groupName="roomId", lockName="", syncCall=1)
def buyProduct(roomId, tableId, userId, productId, level, loginDays):
    """购买商品"""
    try:
        room = gdata.rooms()[roomId]
        table = room.maptable[tableId]
        player = table.getPlayer(userId)
        if player:
            from poker.entity.biz import bireport
            bireport.reportGameEvent("BI_NFISH_BUY_PRODUCT", userId, FISH_GAMEID, roomId,
                                    productId, level, 0, 0, 0, [], util.getClientId(userId), loginDays, player.allChip)
            # ftlog.debug("BI_NFISH_BUY_PRODUCT", userId, roomId, productId, level, player.chip, player.allChip, player.tableChip)
    except Exception, e:
        ftlog.error("buyProduct error", roomId, tableId, userId, productId, level, loginDays, traceback.format_exc())
    return 0


@markRpcCall(groupName="roomId", lockName="", syncCall=1)
def sendGrandPrizeReward(roomId, tableId, userId, fId, coinCount, level, seatId, fpMultiple):
    """
    发放巨奖奖励
    """
    try:
        rewards = [{"name": config.CHIP_KINDID, "count": coinCount}]
        room = gdata.rooms()[roomId]
        table = room.maptable[tableId]
        player = table.getPlayer(userId)

        msg = MsgPack()
        msg.setCmd("getGrandPrizeRewards")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", userId)
        msg.setResult("fId", fId)
        msg.setResult("rewards", rewards)
        msg.setResult("level", level)
        msg.setResult("seatId", seatId)
        msg.setResult("fpMultiple", fpMultiple)
        GameMsg.sendMsg(msg, table.getBroadcastUids())

        if player:
            for bigRoomId in config.getGrandPrizeConf().get("roomIds", []):
                player.fireCost[str(bigRoomId)] = 0
            name = player.name
            player.addTableChip(coinCount, "BI_NFISH_GRAND_PRIZE")
            player.totalGainChip += coinCount
            # 深海巨奖触发幸运降临
            table.checkBigPrize(player, coinCount // fpMultiple, coinCount, fpMultiple, isGrandPriz=True)
        else:
            from poker.entity.dao import gamedata
            from newfish.entity.redis_keys import GameData
            fireCost = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.fireCost, {})
            for bigRoomId in config.getGrandPrizeConf().get("roomIds", []):
                fireCost[str(bigRoomId)] = 0
            gamedata.setGameAttr(userId, FISH_GAMEID, GameData.fireCost, json.dumps(fireCost))
            name = util.getNickname(userId)
            util.addRewards(userId, rewards, "BI_NFISH_GRAND_PRIZE", roomId)

        leds = ["ID_LED_GRAND_PRIZE_1", "ID_LED_GRAND_PRIZE_2", "ID_LED_GRAND_PRIZE_3"]
        if len(leds) > level >= 0:
            lang = util.getLanguage(userId)
            msg = config.getMultiLangTextConf(leds[level], lang=lang) % \
                  (name, config.getMultiLangTextConf(table.runConfig.title, lang=lang), util.formatScore(coinCount, lang=lang))
            user_rpc.sendLed(FISH_GAMEID, msg, id=leds[level], lang=lang)
    except Exception, e:
        ftlog.error("sendGrandPrizeReward", roomId, tableId, userId, fId, coinCount, traceback.format_exc())
    return 0


@markRpcCall(groupName="roomId", lockName="", syncCall=1)
def startTowerTotalBetsTimer(roomId):
    """启动魔塔累计充能金币刷新定时器"""
    ftlog.debug("startTowerTotalBetsTimer", roomId)
    try:
        room = gdata.rooms()[roomId]
        room.startTowerTotalBetsTimer()
    except Exception, e:
        ftlog.error("startTowerTotalBetsTimer", roomId, traceback.format_exc())
    return 0


@markRpcCall(groupName="roomId", lockName="", syncCall=1)
def stopTowerTotalBetsTimer(roomId):
    """停止魔塔累计充能金币刷新定时器"""
    ftlog.debug("stopTowerTotalBetsTimer", roomId)
    try:
        room = gdata.rooms()[roomId]
        room.stopTowerTotalBetsTimer()
    except Exception, e:
        ftlog.error("stopTowerTotalBetsTimer", roomId, traceback.format_exc())
    return 0


@markRpcCall(groupName="roomId", lockName="", syncCall=1)
def notifyInspireInfo(roomId, teamId, ratio, remainTime, purchaserUid, interval, lv):
    """渔场内鼓舞礼包通知"""
    room = gdata.rooms()[roomId]
    ftlog.debug("notifyInspireInfo, ", roomId, teamId, ratio, remainTime, room.maptable.keys() if room else [])
    # for table in room.maptable.values():
    #     if table.playersNum:
    #         table.notifyInspireInfo(teamId, ratio, remainTime)
    name = util.getNickname(purchaserUid)
    avatar = userdata.getAttr(purchaserUid, "purl")
    ledTxt = {}
    from newfish.entity.fishactivity import competition_activity
    mo = MsgPack()
    mo.setCmd("comp_act_notify")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("teamId", teamId)
    mo.setResult("teamInspireBuf", (ratio, remainTime, lv))
    actState, actStateRemainTime = competition_activity._getCompStateAndRemainTime()
    mo.setResult("actState", actState)
    mo.setResult("actStateRemainTime", actStateRemainTime)
    mo.setResult("avatar", avatar)
    mo.setResult("name", name)
    mo.setResult("interval", interval)
    for lang in util.getAllLanguage():
        teamName = config.getMultiLangTextConf("ID_COMPACT_TEAM_%d" % (teamId + 1), lang=lang)
        led = config.getMultiLangTextConf("ID_COMPACT_LED", lang=lang).format(name, teamName, interval)
        ledTxt[lang] = led
    for _uid in room._allPlayerDict.keys():
        if competition_activity._getCompTeamId(_uid) == teamId:
            lang = util.getLanguage(_uid)
            mo.setResult("led", ledTxt.get(lang, ""))
            GameMsg.sendMsg(mo, _uid)
            ftlog.debug("notifyInspireInfo, userId =", _uid, "teamId =", teamId, "mo =", mo)
    return 1