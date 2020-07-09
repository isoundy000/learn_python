#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6

import time

from freetime.util import log as ftlog
from freetime.util.log import getMethodName
from poker.entity.game.quick_start import BaseQuickStart
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.dao import onlinedata, userchip, gamedata
from poker.entity.configure import gdata, pokerconf
from poker.entity.game.rooms.room_mixin import TYRoomMixin
from poker.util import strutil
from newfish.entity import config, util, weakdata
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData, WeakData
from hall.entity import hallvip
from newfish.entity import grand_prix


class FishQuickStartDispatcher(object):
    """
    按clientId分发快速开始请求
    """
    @classmethod
    def dispatchQuickStart(cls, msg, userId, gameId, roomId, tableId, clientId, kindId):
        return FishQuickStart.onCmdQuickStart(msg, userId, gameId, roomId, tableId, clientId, kindId)


class FishQuickStart(BaseQuickStart):

    ENTER_ROOM_REASON_OK = 0
    ENTER_ROOM_REASON_LESS_LEVEL = 1        # 等级过低
    ENTER_ROOM_REASON_INNER_ERROR = 2       # 内部错误
    ENTER_ROOM_REASON_MAINTENANCE = 3       # 系统维护
    ENTER_ROOM_REASON_ROOM_ID_ERROR = 4     # 房间错误
    ENTER_ROOM_REASON_VERSION_DISABLE = 5   # 版本过低
    ENTER_ROOM_REASON_TIME_LIMIT = 6        # 未到开放时间
    ENTER_ROOM_REASON_LESS_FEES = 7         # 钥匙不够
    ENTER_ROOM_REASON_STATE_ERROR = 8       # 在线状态错误
    ENTER_ROOM_REASON_LESS_BULLET = 9       # 招财珠不够
    ENTER_ROOM_REASON_SEAT_FULL = 10        # 座位已满
    ENTER_ROOM_REASON_LESS_VIP = 11         # VIP等级不够
    ENTER_ROOM_REASON_LESS_COIN = 12        # 金币不足
    ENTER_ROOM_REASON_EXCESSIVE_LOSS = 13   # 亏损过多
    ENTER_ROOM_REASON_NOT_OPEN = 14         # 房间暂未开放
    ENTER_ROOM_REASON_GRAND_PRIX_LESS_FEES = 15 # 大奖赛门票不足
    ENTER_ROOM_REASON_GRAND_PRIX_NOE_OPEN = 16  # 大奖赛没开期

    @classmethod
    def onCmdQuickStart(cls, msg, userId, gameId, roomId, tableId, clientId, kindId):
        """UT server中处理来自客户端的quick_start请求
        Args:
            msg
                cmd : quick_start
                if roomId == 0:
                    表示快速开始，服务器为玩家选择房间，然后将请求转给GR

                if roomId > 0 and tableId == 0 :
                    表示玩家选择了房间，将请求转给GR

                if roomId > 0 and tableId == roomId * 10000 :
                    表示玩家在队列里断线重连，将请求转给GR

                if roomId > 0 and tableId > 0:
                    if onlineSeatId > 0:
                        表示玩家在牌桌里断线重连，将请求转给GT
                    else:
                        表示玩家选择了桌子，将请求转给GR
        """
        assert isinstance(userId, int) and userId > 0
        assert isinstance(roomId, int) and roomId >= 0
        assert isinstance(tableId, int) and tableId >= 0

        ftlog.debug("onCmdQuickStart->", userId, "msg =", msg, "roomId =", roomId, "tableId =", tableId, "clientId =", clientId)
        isRobot = userId < config.ROBOT_MAX_USER_ID
        if not isRobot and not util.isUsableClientVersion(userId):
            cls.onQuickStartFailed(cls.ENTER_ROOM_REASON_VERSION_DISABLE, userId, clientId, roomId)
            return

        # 单开, 无论何时quick_start进入都检查loc
        if not pokerconf.isOpenMoreTable(clientId):
            locList = onlinedata.getOnlineLocList(userId)
            ftlog.debug("onCmdQuickStart->getOnlineLocList->", userId, locList)
            try:
                for lRoomId, lTableId, lSeatId in locList:
                    roomGameId = strutil.getGameIdFromInstanceRoomId(lRoomId)
                    if roomGameId == FISH_GAMEID:
                        roomId = lRoomId
                        tableId = lTableId
                        ftlog.info("onCmdQuickStart->reconnect roomId, tableId->", userId, roomId, tableId)
                    else:
                        cls.onQuickStartFailed(cls.ENTER_ROOM_REASON_STATE_ERROR, userId, clientId, roomId)
                        return
                    break
            except:
                ftlog.warn("onCmdQuickStart->error", userId, roomId, tableId)

        redState = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.redState)      # 新手任务状态
        if isRobot is False and redState == 0:
            ctrlRoomId = config.getCommonValueByKey("newbieRoomId")
            chosenTableId = 0
            shadowRoomId = None
            if gdata.getBigRoomId(roomId) == gdata.getBigRoomId(ctrlRoomId) and tableId:
                chosenTableId = tableId
                shadowRoomId = tableId / 10000
            TYRoomMixin.queryRoomQuickStartReq(msg, ctrlRoomId, chosenTableId, shadowRoomId=shadowRoomId)  # 请求转给GR
            return

        if roomId == 0:                                                                 # 玩家点击快速开始
            chosenRoomId, reason = cls._chooseRoom(userId, gameId)
            ftlog.info("onCmdQuickStart->chosenRoomId", chosenRoomId, "userId =", userId, "reason =", reason)
            if reason == cls.ENTER_ROOM_REASON_OK:
                TYRoomMixin.queryRoomQuickStartReq(msg, chosenRoomId, 0)  # 请求转给GR
            else:
                cls.onQuickStartFailed(reason, userId, clientId, roomId)
            return

        if tableId == 0:                                                                # 玩家只选择了房间
            bigRoomId = gdata.getBigRoomId(roomId)
            if bigRoomId == 0:
                cls.onQuickStartFailed(cls.ENTER_ROOM_REASON_ROOM_ID_ERROR, userId, clientId, roomId)
                return
            ctrlRoomIds = gdata.bigRoomidsMap()[bigRoomId]
            ctrlRoomId = ctrlRoomIds[userId % len(ctrlRoomIds)]
            reason = cls.canQuickEnterRoom(userId, gameId, ctrlRoomId, kindId)
            if reason == cls.ENTER_ROOM_REASON_OK:
                roomConf = gdata.roomIdDefineMap()[roomId].configure
                fee = roomConf.get("fee_%s" % kindId, {}) or roomConf.get("fee", {})
                rewards = fee.get("rewards", [])
                if fee:
                    _consume = [{"name": fee["kindId"], "count": fee["count"]}]
                    ret = util.consumeItems(userId, _consume, "ROOM_GAME_FEE")
                    if ret and rewards:
                        util.addRewards(userId, rewards, "BI_NFISH_VOUCHER_REWARDS", kindId)
                TYRoomMixin.queryRoomQuickStartReq(msg, ctrlRoomId, 0)  # 请求转给GR或GT
            else:
                cls.onQuickStartFailed(reason, userId, clientId, roomId)
            return

        if tableId == roomId * 10000:                                                   # 玩家在队列里断线重连
            TYRoomMixin.queryRoomQuickStartReq(msg, roomId, tableId)                    # 请求转给GR
            return

        onlineSeat = onlinedata.getOnlineLocSeatId(userId, roomId, tableId)

        if onlineSeat:
            TYRoomMixin.querySitReq(userId, roomId, tableId, clientId, {"seatId": onlineSeat})  # 玩家断线重连，请求转给GT
        else:                                                                                   # 玩家选择了桌子
            shadowRoomId = tableId / 10000
            ctrlRoomId = gdata.roomIdDefineMap()[shadowRoomId].parentId
            TYRoomMixin.queryRoomQuickStartReq(msg, ctrlRoomId, tableId, shadowRoomId=shadowRoomId)  # 请求转给GR

    @classmethod
    def _chooseRoom(cls, userId, gameId):
        """
        服务端为玩家选择房间
        """
        candidateRoomIds = cls._getCandidateRoomIds(gameId, "")
        ftlog.debug("_chooseRoom->candidateRoomIds =", candidateRoomIds)
        newbieRoomId = config.getCommonValueByKey("newbieRoomId")
        if not util.isFinishAllRedTask(userId):
            return newbieRoomId, cls.ENTER_ROOM_REASON_OK
        uLevel = util.getLevelByGunLevel(userId)
        userChip = userchip.getChip(userId)
        candidateRoomId = 0
        testMode = util.getNewbieABCTestMode(userId)
        for roomId in sorted(candidateRoomIds, reverse=True):
            isOK, minCoin, minLevel = cls._matchEnterRoom(userChip, uLevel, roomId, abcTestMode=testMode)
            if isOK:
                candidateRoomId = roomId
                break
        if candidateRoomId > 0:
            return candidateRoomId, cls.ENTER_ROOM_REASON_OK
        else:
            return 0, cls.ENTER_ROOM_REASON_LESS_LEVEL

    @classmethod
    def getFailedInfo(cls, reason, userId, roomId):
        """
        获取失败提示信息
        """
        lang = util.getLanguage(userId)
        testMode = util.getNewbieABCTestMode(userId)
        roomConf = {}
        if gdata.roomIdDefineMap().get(roomId):
            roomConf = gdata.roomIdDefineMap()[roomId].configure
        info = config.getMultiLangTextConf("ID_ENTER_ROOM_REASON", lang=lang)
        if reason == cls.ENTER_ROOM_REASON_LESS_LEVEL:              # 等级过低
            info = config.getMultiLangTextConf("ID_ENTER_ROOM_REASON_LESS_LEVE", lang=lang) % util.getRoomMinLevel(roomId, testMode)    # roomConf["minLevel"]
        elif reason == cls.ENTER_ROOM_REASON_MAINTENANCE:           # 系统维护
            info = config.getMultiLangTextConf("ID_ENTER_ROOM_REASON_MAINTENANCE", lang=lang)
        elif reason == cls.ENTER_ROOM_REASON_VERSION_DISABLE:       # 版本过低
            info = config.getMultiLangTextConf("ID_ENTER_ROOM_REASON_VERSION_DISABLE", lang=lang)
        elif reason == cls.ENTER_ROOM_REASON_LESS_FEES:             # 钥匙不够
            info = config.getMultiLangTextConf("ID_ENTER_ROOM_REASON_LESS_FEES", lang=lang)
        elif reason == cls.ENTER_ROOM_REASON_LESS_BULLET:           # 招财珠不够
            info = config.getMultiLangTextConf("ID_ENTER_ROOM_REASON_LESS_BULLET", lang=lang)
        elif reason == cls.ENTER_ROOM_REASON_LESS_COIN:             # 金币不足
            info = config.getMultiLangTextConf("ID_ENTER_ROOM_REASON_LESS_COIN", lang=lang) % util.formatScore(util.getRoomMinCoin(roomId, testMode), lang=lang)
        elif reason == cls.ENTER_ROOM_REASON_TIME_LIMIT:            # 未到开放时间
            info = config.getMultiLangTextConf("ID_ENTER_ROOM_REASON_NOT_OPEN", lang=lang)
            if roomConf.get("typeName") == config.FISH_ROBBERY:     # 招财模式渔场
                info = config.getMultiLangTextConf("ID_ENTER_ROOM_REASON_TIME_LIMIT", lang=lang)
        elif reason == cls.ENTER_ROOM_REASON_EXCESSIVE_LOSS:        # 亏损过多
            info = config.getMultiLangTextConf("ID_ENTER_ROOM_REASON_EXCESSIVE_LOSS", lang=lang) % config.getMultiLangTextConf(roomConf["name"], lang=lang)
        elif reason == cls.ENTER_ROOM_REASON_NOT_OPEN:              # 房间暂未开放
            info = config.getMultiLangTextConf("ID_ENTER_ROOM_REASON_NOT_OPEN", lang=lang)
        elif reason == cls.ENTER_ROOM_REASON_GRAND_PRIX_LESS_FEES:  # 大奖赛门票不足
            info = config.getMultiLangTextConf("ENTER_ROOM_REASON_GRAND_PRIX_LESS_FEES", lang=lang)
        return info

    @classmethod
    def onQuickStartFailed(cls, reason, userId, clientId, roomId):
        """
        进入房间失败回调函数
        """
        ftlog.warn("onQuickStartFailed", userId, reason, roomId, caller=cls)
        roomConf = {}
        if gdata.roomIdDefineMap().get(roomId):
            roomConf = gdata.roomIdDefineMap()[roomId].configure
        testMode = util.getNewbieABCTestMode(userId)
        minLevel = util.getRoomMinLevel(roomId, testMode)               # roomConf.get("minLevel", 1)
        info = cls.getFailedInfo(reason, userId, roomId)
        mo = MsgPack()
        mo.setCmd("quick_start")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("minLevel", minLevel)
        mo.setResult("info", info)
        mo.setResult("reason", reason)
        router.sendToUser(mo, userId)

    @classmethod
    def canQuickEnterRoom(cls, userId, gameId, roomId, kindId):
        """
        判断能否进入房间
        """
        try:
            if not util.isFinishAllRedTask(userId):
                newbieRoomId = config.getCommonValueByKey("newbieRoomId")
                if gdata.getBigRoomId(roomId) != gdata.getBigRoomId(newbieRoomId):
                    return cls.ENTER_ROOM_REASON_INNER_ERROR
            uLevel = util.getLevelByGunLevel(userId)
            if not uLevel:
                return cls.ENTER_ROOM_REASON_INNER_ERROR
            userChip = userchip.getUserChipAll(userId)
            if ftlog.is_debug():
                ftlog.debug(gdata.roomIdDefineMap()[roomId].configure)
            roomConf = gdata.roomIdDefineMap()[roomId].configure
            testMode = util.getNewbieABCTestMode(userId)
            fee = roomConf.get("fee_%s" % kindId, {}) or roomConf.get("fee", {})
            minCoin = util.getRoomMinCoin(roomId, testMode)  # roomConf.get("minCoin", 1)
            minLevel = util.getRoomMinLevel(roomId, testMode)  # roomConf.get("minLevel", 1)
            timeLimit = roomConf.get("timeLimit", [])
            bulletLimit = roomConf.get("bulletLimit", {})
            protectionLimit = roomConf.get("protectionLimit", {})
            if fee:
                surplusCount = util.balanceItem(userId, fee["kindId"])
                if surplusCount < fee["count"]:
                    return cls.ENTER_ROOM_REASON_LESS_FEES
            if bulletLimit and not kindId:
                isCan = False
                for kindId in bulletLimit:
                    surplusCount = util.balanceItem(userId, kindId)
                    if surplusCount >= bulletLimit[kindId]:
                        isCan = True
                        break
                if not isCan:
                    return cls.ENTER_ROOM_REASON_LESS_BULLET
            if timeLimit:
                isCan = False
                currentTime = int(time.time())
                for timeRange in timeLimit:
                    startTime = util.getTodayTimestampFromStr(timeRange[0])
                    endTime = util.getTodayTimestampFromStr(timeRange[1])
                    if startTime <= currentTime <= endTime:
                        isCan = True
                        break
                if not isCan:
                    return cls.ENTER_ROOM_REASON_TIME_LIMIT
            if userChip < minCoin:
                return cls.ENTER_ROOM_REASON_LESS_COIN
            if int(uLevel) < minLevel and not kindId:
                return cls.ENTER_ROOM_REASON_LESS_LEVEL
            if protectionLimit:
                dailyProfitCoin, monthlyProfitCoin = 0, 0
                if roomConf.get("typeName") == config.FISH_ROBBERY:
                    dailyProfitCoin, monthlyProfitCoin = util.getRobberyProfitCoin(userId)
                elif roomConf.get("typeName") == config.FISH_POSEIDON:
                    dailyProfitCoin, monthlyProfitCoin = util.getPoseidonProfitCoin(userId)
                if (dailyProfitCoin <= protectionLimit["dailyLoss"] or
                    monthlyProfitCoin <= protectionLimit["monthlyLoss"]):
                    return cls.ENTER_ROOM_REASON_EXCESSIVE_LOSS
            # 检测大奖赛开放时间
            if roomConf.get("typeName") in [config.FISH_GRAND_PRIX]:
                state = cls.grandPrixEnterRoom(userId)
                if state != cls.ENTER_ROOM_REASON_OK:
                    return state
            return cls.ENTER_ROOM_REASON_OK

        except Exception as e:
            ftlog.error("canQuickEnterRoom error", userId, e)
            return cls.ENTER_ROOM_REASON_INNER_ERROR

    @classmethod
    def grandPrixEnterRoom(cls, userId):
        """
        大奖赛房间能否进入
        """
        startDay = config.getGrandPrixConf("info").get("startDay")
        currentTime = int(time.time())
        if startDay and currentTime < util.getTimestampFromStr(startDay):
            return cls.ENTER_ROOM_REASON_NOT_OPEN
        if weakdata.getDayFishData(userId, WeakData.grandPrix_startTS, 0) == 0:
            dayStartTimestamp = util.getDayStartTimestamp(currentTime)
            remainGrandPrixTimeSeconds = util.timeStrToInt(config.getGrandPrixConf("openTimeRange")[1]) - (
                currentTime - dayStartTimestamp)  # 大奖赛剩余时间
            if not grand_prix.isGrandPrixOpenTime() or remainGrandPrixTimeSeconds < 10:
                return cls.ENTER_ROOM_REASON_GRAND_PRIX_NOE_OPEN
            vipLevel = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
            if config.getVipConf(vipLevel).get("grandPrixFreeTimes", 0) <= weakdata.getDayFishData(userId,
                                                                                                   WeakData.grandPrix_freeTimes,
                                                                                                   0):  # 用免费次数已经用完
                fee = config.getGrandPrixConf("fee")
                surplusCount = util.balanceItem(userId, fee["name"])
                if surplusCount < fee["count"]:
                    return cls.ENTER_ROOM_REASON_GRAND_PRIX_LESS_FEES
                util.consumeItems(userId, [{"name": fee["name"], "count": fee["count"]}], "ROOM_GRAND_PRIX_FEE")
        return cls.ENTER_ROOM_REASON_OK

    @classmethod
    def _matchEnterRoom(cls, userChip, uLevel, roomId, lastRoomType=None, abcTestMode=None):
        """匹配进入房间"""
        roomConf = gdata.roomIdDefineMap()[roomId].configure
        minCoin = util.getRoomMinCoin(roomId, abcTestMode)                          # roomConf.get("minCoin", 0)
        minLevel = util.getRoomMinLevel(roomId, abcTestMode)                        # roomConf.get("minLevel", 1)
        typeName = roomConf.get("typeName")
        if not lastRoomType:
            lastRoomType = config.FISH_FRIEND
        if typeName == lastRoomType:
            if userChip >= minCoin and uLevel >= minLevel:
                return True, minCoin, minLevel
            else:
                return False, 0, 0
        return False, 0, 0