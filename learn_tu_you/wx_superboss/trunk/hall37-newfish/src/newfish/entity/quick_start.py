# -*- coding=utf-8 -*-
"""
Created by lichen on 16/12/13.
"""

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
    ENTER_ROOM_REASON_GRAND_PRIX_LESS_FEES = 15     # 大奖赛门票不足
    ENTER_ROOM_REASON_GRAND_PRIX_NOE_OPEN = 16      # 大奖赛没开期

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
        if ftlog.is_debug():
            ftlog.debug("onCmdQuickStart->", userId, "msg =", msg, "roomId =", roomId, "tableId =", tableId, "clientId =", clientId)
        isRobot = userId < config.ROBOT_MAX_USER_ID
        if not isRobot and not util.isUsableClientVersion(userId):
            cls.onQuickStartFailed(cls.ENTER_ROOM_REASON_VERSION_DISABLE, userId, clientId, roomId)
            return

        # 单开, 无论何时quick_start进入都检查loc
        if not pokerconf.isOpenMoreTable(clientId):
            locList = onlinedata.getOnlineLocList(userId)
            if ftlog.is_debug():
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

        redState = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.redState)
        if isRobot is False and redState == 0:
            ctrlRoomId = config.getCommonValueByKey("newbieRoomId")
            chosenTableId = 0
            shadowRoomId = None
            if gdata.getBigRoomId(roomId) == gdata.getBigRoomId(ctrlRoomId) and tableId:
                chosenTableId = tableId
                shadowRoomId = tableId / 10000
            TYRoomMixin.queryRoomQuickStartReq(msg, ctrlRoomId, chosenTableId, shadowRoomId=shadowRoomId)  # 请求转给GR
            return

        if roomId == 0:                                                                         # 玩家点击快速开始
            chosenRoomId, reason = cls._chooseRoom(userId, gameId)
            ftlog.info("onCmdQuickStart->chosenRoomId", chosenRoomId, "userId =", userId, "reason =", reason)
            if reason == cls.ENTER_ROOM_REASON_OK:
                TYRoomMixin.queryRoomQuickStartReq(msg, chosenRoomId, 0)                        # 请求转给GR
            else:
                cls.onQuickStartFailed(reason, userId, clientId, roomId)
            return
        
        if tableId == 0:                                                                        # 玩家只选择了房间
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
                TYRoomMixin.queryRoomQuickStartReq(msg, ctrlRoomId, 0)                          # 请求转给GR或GT
            else:
                cls.onQuickStartFailed(reason, userId, clientId, roomId)
            return

        if tableId == roomId * 10000:                                                           # 玩家在队列里断线重连
            TYRoomMixin.queryRoomQuickStartReq(msg, roomId, tableId)  # 请求转给GR
            return
        
        onlineSeat = onlinedata.getOnlineLocSeatId(userId, roomId, tableId)
        
        if onlineSeat:
            TYRoomMixin.querySitReq(userId, roomId, tableId, clientId, {"seatId": onlineSeat})  # 玩家断线重连，请求转给GT
        else:  # 玩家选择了桌子
            shadowRoomId = tableId / 10000
            ctrlRoomId = gdata.roomIdDefineMap()[shadowRoomId].parentId
            TYRoomMixin.queryRoomQuickStartReq(msg, ctrlRoomId, tableId, shadowRoomId=shadowRoomId)  # 请求转给GR
    
    @classmethod
    def _chooseRoom(cls, userId, gameId, gameMode=config.MULTIPLE_MODE):
        """
        服务端为玩家选择房间
        """
        candidateRoomIds = cls._getCandidateRoomIds(gameId, "")
        newbieRoomId = config.getCommonValueByKey("newbieRoomId")
        if not util.isFinishAllNewbieTask(userId):
            return newbieRoomId, cls.ENTER_ROOM_REASON_OK
        uLevel = util.getUserLevel(userId)
        gunLevel = util.getGunLevel(userId, gameMode)
        userChip = userchip.getChip(userId)
        candidateRoomId = 0
        for roomId in sorted(candidateRoomIds, reverse=True):
            isOK = cls._matchEnterRoom(roomId, uLevel, gunLevel, userChip, gameMode)
            if isOK:
                candidateRoomId = roomId
                break
        if ftlog.is_debug():
            ftlog.debug("_chooseRoom", userId, gameId, gameMode, candidateRoomId)
        if candidateRoomId > 0:
            return candidateRoomId, cls.ENTER_ROOM_REASON_OK                      
        return 0, cls.ENTER_ROOM_REASON_LESS_LEVEL

    @classmethod
    def getFailedInfo(cls, reason, userId, roomId):
        """
        获取失败提示信息
        """
        lang = util.getLanguage(userId)
        roomConf = {}
        if gdata.roomIdDefineMap().get(roomId):
            roomConf = gdata.roomIdDefineMap()[roomId].configure
        info = config.getMultiLangTextConf("ID_ENTER_ROOM_REASON", lang=lang)
        if reason == cls.ENTER_ROOM_REASON_LESS_LEVEL:
            info = config.getMultiLangTextConf("ID_ENTER_ROOM_REASON_LESS_LEVEL", lang=lang) % roomConf["minLevel"]
        elif reason == cls.ENTER_ROOM_REASON_MAINTENANCE:
            info = config.getMultiLangTextConf("ID_ENTER_ROOM_REASON_MAINTENANCE", lang=lang)
        elif reason == cls.ENTER_ROOM_REASON_VERSION_DISABLE:
            info = config.getMultiLangTextConf("ID_ENTER_ROOM_REASON_VERSION_DISABLE", lang=lang)
        elif reason == cls.ENTER_ROOM_REASON_LESS_FEES:
            info = config.getMultiLangTextConf("ID_ENTER_ROOM_REASON_LESS_FEES", lang=lang)
        elif reason == cls.ENTER_ROOM_REASON_LESS_BULLET:
            info = config.getMultiLangTextConf("ID_ENTER_ROOM_REASON_LESS_BULLET", lang=lang)
        elif reason == cls.ENTER_ROOM_REASON_LESS_COIN:
            info = config.getMultiLangTextConf("ID_ENTER_ROOM_REASON_LESS_COIN", lang=lang) % util.formatScore(roomConf["minCoin"], lang=lang)
        elif reason == cls.ENTER_ROOM_REASON_TIME_LIMIT:
            info = config.getMultiLangTextConf("ID_ENTER_ROOM_REASON_NOT_OPEN", lang=lang)
            if roomConf.get("typeName") == config.FISH_ROBBERY:
                info = config.getMultiLangTextConf("ID_ENTER_ROOM_REASON_TIME_LIMIT", lang=lang)
        elif reason == cls.ENTER_ROOM_REASON_EXCESSIVE_LOSS:
            info = config.getMultiLangTextConf("ID_ENTER_ROOM_REASON_EXCESSIVE_LOSS", lang=lang) % config.getMultiLangTextConf(roomConf["name"], lang=lang)
        elif reason == cls.ENTER_ROOM_REASON_NOT_OPEN:
            info = config.getMultiLangTextConf("ID_ENTER_ROOM_REASON_NOT_OPEN", lang=lang)
        elif reason == cls.ENTER_ROOM_REASON_GRAND_PRIX_LESS_FEES:  # 大奖赛门票不足
            info = config.getMultiLangTextConf("ENTER_ROOM_REASON_GRAND_PRIX_LESS_FEES", lang=lang)
        elif reason == cls.ENTER_ROOM_REASON_GRAND_PRIX_NOE_OPEN:
            info = config.getMultiLangTextConf("ENTER_ROOM_REASON_GRAND_PRIX_NOE_OPEN", lang=lang)
        return info

    @classmethod
    def onQuickStartFailed(cls, reason, userId, clientId, roomId):
        """
        进入房间失败回调函数
        """
        ftlog.warn("onQuickStartFailed", userId, reason, roomId, caller=cls)
        minLevel = util.getRoomMinLevel(roomId)
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
            if util.isFinishAllNewbieTask(userId):
                newbieRoomId = config.getCommonValueByKey("newbieRoomId")
                if gdata.getBigRoomId(roomId) == gdata.getBigRoomId(newbieRoomId):
                    return cls.ENTER_ROOM_REASON_INNER_ERROR
            else:
                newbieRoomId = config.getCommonValueByKey("newbieRoomId")
                if gdata.getBigRoomId(roomId) != gdata.getBigRoomId(newbieRoomId):
                    return cls.ENTER_ROOM_REASON_INNER_ERROR
            gameMode = util.getRoomGameMode(roomId)
            isOldPlayerV2 = util.isOldPlayerV2(userId)
            if gameMode == config.CLASSIC_MODE and not isOldPlayerV2:
                return cls.ENTER_ROOM_REASON_INNER_ERROR
            uLevel = util.getUserLevel(userId)
            gunLevel = util.getGunLevel(userId, gameMode)
            if not uLevel or not gunLevel:
                return cls.ENTER_ROOM_REASON_INNER_ERROR
            userChip = userchip.getUserChipAll(userId)
            vipLevel = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
            if ftlog.is_debug():
                ftlog.debug("canQuickEnterRoom->", gdata.roomIdDefineMap()[roomId].configure)
            roomConf = gdata.roomIdDefineMap()[roomId].configure
            fee = roomConf.get("fee_%s" % kindId, {}) or roomConf.get("fee", {})
            minLevel = roomConf.get("minLevel", 1)
            minGunLevel = roomConf.get("minGunLevel", 1)
            minCoin = roomConf.get("minCoin", 1)
            minVip = roomConf.get("minVip", 0)
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
            if uLevel < minLevel and not kindId:
                if roomConf.get("typeName") == config.FISH_ROBBERY:
                    if vipLevel >= minVip:
                        return cls.ENTER_ROOM_REASON_OK
                return cls.ENTER_ROOM_REASON_LESS_LEVEL
            if gunLevel < minGunLevel and roomConf.get("typeName") != config.FISH_ROBBERY:
                return cls.ENTER_ROOM_REASON_LESS_LEVEL
            if userChip < minCoin:
                return cls.ENTER_ROOM_REASON_LESS_COIN
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
            if config.getVipConf(vipLevel).get("grandPrixFreeTimes", 0) <= \
                    weakdata.getDayFishData(userId, WeakData.grandPrix_freeTimes, 0):  # 用免费次数已经用完
                fee = config.getGrandPrixConf("fee")[0]
                surplusCount = util.balanceItem(userId, fee["name"])
                if surplusCount < fee["count"]:
                    return cls.ENTER_ROOM_REASON_GRAND_PRIX_LESS_FEES
        return cls.ENTER_ROOM_REASON_OK

    @classmethod
    def _matchEnterRoom(cls, roomId, uLevel, gunLevel, userChip, gameMode):
        """匹配进入房间"""
        roomConf = gdata.roomIdDefineMap()[roomId].configure
        minLevel = roomConf.get("minLevel", 1)
        gunLevelVal = config.getGunLevelConf(gunLevel, gameMode).get("levelValue", 1)
        minGunLevelVal = roomConf.get("minGunLevelVal", 0)
        minCoin = roomConf.get("minCoin", 0)
        typeName = roomConf.get("typeName")
        roomType = config.CLASSIC_MODE_ROOM_TYPE
        if gameMode == config.MULTIPLE_MODE:
            roomType = config.MULTIPLE_MODE_ROOM_TYPE
        if typeName in roomType:
            if uLevel >= minLevel and gunLevelVal >= minGunLevelVal and userChip >= minCoin:
                return True
        return False