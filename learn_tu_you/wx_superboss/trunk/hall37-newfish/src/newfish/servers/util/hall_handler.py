#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/5


from distutils.version import StrictVersion

import freetime.util.log as ftlog
from poker.protocol import runcmd, router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from freetime.entity.msg import MsgPack
from poker.entity.dao import gamedata
from poker.entity.configure import gdata
from poker.entity.game import game
from hall.servers.common.base_checker import BaseMsgPackChecker
from newfish.entity.quick_start import FishQuickStartDispatcher, FishQuickStart
from newfish.entity import util, module_tip, config
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData, ABTestData
from newfish.entity.grand_prize_pool import GrandPrizePool


@markCmdActionHandler
class HallTcpHandler(BaseMsgPackChecker):

    def _check_param_sessionIndex(self, msg, key, params):
        sessionIndex = msg.getParam(key)
        if isinstance(sessionIndex, int) and sessionIndex >= 0:
            return None, sessionIndex
        return None, -1

    def _check_param_modules(self, msg, key, params):
        modules = msg.getParam("modules")
        if modules and isinstance(modules, list):
            return None, modules
        return "ERROR of modules !", None

    def _check_param_values(self, msg, key, params):
        values = msg.getParam("values")
        if values and isinstance(values, list):
            return None, values
        return "ERROR of values !", None

    def _check_param_kindId(self, msg, key, params):
        kindId = msg.getParam("kindId") or 0
        try:
            kindId = int(kindId)
            if isinstance(kindId, int) and kindId >= 0:
                return None, kindId
        except:
            return None, 0
        return None, 0

    def isMinClientVersion(self, minClientVersion, clientVersion):
        """是否是最小的客户端版本"""
        if minClientVersion and clientVersion and StrictVersion(str(minClientVersion)) > StrictVersion(str(clientVersion)):
            return True
        return False

    @markCmdActionMethod(cmd="game", action="quick_enter", clientIdVer=0, scope="game", lockParamName="")
    def doGetQuickEnterRoom(self, userId, gameId, roomId0, tableId0, kindId):
        """
        获取快速进入房间信息
        """
        from newfish.entity.quick_start import FishQuickStart
        reason = FishQuickStart.ENTER_ROOM_REASON_OK
        info = u""
        if not util.isUsableClientVersion(userId):
            reason = FishQuickStart.ENTER_ROOM_REASON_VERSION_DISABLE
        elif game.isShutDown():
            reason = FishQuickStart.ENTER_ROOM_REASON_MAINTENANCE
        if reason != FishQuickStart.ENTER_ROOM_REASON_OK:
            info = FishQuickStart.getFailedInfo(reason, userId, roomId0)
            self.sendQuickEnterInfo(gameId, userId, roomId0, tableId0, kindId, reason, info)
            return
        isIn, roomId, tableId, _ = util.isInFishTable(userId)
        if not isIn:
            if roomId0:             # 用户选择了房间，先判断用户自己选的房间能否进入
                try:
                    reason = FishQuickStart.canQuickEnterRoom(userId, gameId, roomId0, kindId)
                    if reason == FishQuickStart.ENTER_ROOM_REASON_OK:
                        roomId = roomId0
                        tableId = tableId0
                    else:           # 用户选择的房间无法进入
                        roomConf = gdata.getRoomConfigure(roomId0)
                        if roomConf and roomConf.get("typeName") in config.QUICK_START_ROOM_TYPE:   # 普通房间系统自动分配
                            roomId, reason = FishQuickStart._chooseRoom(userId, gameId)
                        else:       # 非普通房间无法进入
                            roomId = roomId0
                            tableId = tableId0
                            info = FishQuickStart.getFailedInfo(reason, userId, roomId)
                except Exception as e:
                    roomId, reason = FishQuickStart._chooseRoom(userId, gameId)
                    ftlog.error("doGetQuickEnterRoom error", userId, gameId, roomId0, tableId0, e)
            else:                   # 用户不选择房间，点击快速开始，系统自动分配
                roomId, reason = FishQuickStart._chooseRoom(userId, gameId)

        self.sendQuickEnterInfo(gameId, userId, roomId, tableId, kindId, reason, info)

    def sendQuickEnterInfo(self, gameId, userId, roomId, tableId, kindId, reason, info):
        """发送快速进入信息"""
        message = MsgPack()
        message.setCmd("quick_enter")
        message.setResult("gameId", gameId)
        message.setResult("userId", userId)
        message.setResult("roomId", roomId)
        message.setResult("tableId", tableId)
        message.setResult("kindId", kindId)
        message.setResult("reason", reason)
        message.setResult("info", info)
        router.sendToUser(message, userId)

    @markCmdActionMethod(cmd="game", action="quick_start", clientIdVer=0, scope="game", lockParamName="")
    def doGameQuickStart(self, userId, gameId, clientId, roomId0, tableId0, kindId):
        """
        TCP 发送的至UTIL服务的quick_start暂时不能用lock userid的方式,
        因为,消息流 CO->UT->GR->GT->UT会死锁
        """
        msg = runcmd.getMsgPack()
        ftlog.debug("doGameQuickStart", userId, gameId, clientId, roomId0, tableId0, caller=self)
        FishQuickStartDispatcher.dispatchQuickStart(msg, userId, gameId, roomId0, tableId0, clientId, kindId)
        if router.isQuery():
            mo = runcmd.newOkMsgPack()
            router.responseQurery(mo, "", str(userId))

    @markCmdActionMethod(cmd="game", action="room_list", clientIdVer=0, scope="game", lockParamName="")
    def doGetRoomList(self, userId, gameId):
        """获取所有房间信息"""
        normalRoomInfos, friendRoomInfos, matchRoomInfos, robberyRoomInfos, \
        pointMatchRoomInfos, grandPrixRoomInfos, poseidonRoomInfos = self._fetchAllRoomInfos(userId, gameId)
        message = MsgPack()
        message.setCmd("room_list")
        message.setResult("gameId", gameId)
        message.setResult("normalRooms", normalRoomInfos)           # 普通房间信息
        message.setResult("friendRooms", friendRoomInfos)           # 好友房间信息
        message.setResult("matchRooms", matchRoomInfos)             # 回馈赛房间信息
        message.setResult("pointMatchRooms", pointMatchRoomInfos)   # 定时积分赛
        message.setResult("robberyRooms", robberyRoomInfos)         # 招财
        message.setResult("grandPrixRooms", grandPrixRoomInfos)     # 大奖
        message.setResult("poseidonRooms", poseidonRoomInfos)       # 海皇
        router.sendToUser(message, userId)

    def _fetchAllRoomInfos(self, userId, gameId):
        """
        获取所有房间信息
        """
        lang = util.getLanguage(userId)
        testMode = util.getNewbieABCTestMode(userId)
        recommendRoomId, reason = FishQuickStart._chooseRoom(userId, gameId)
        if reason != FishQuickStart.ENTER_ROOM_REASON_OK:
            recommendRoomId = 0
        re_roomConf = None
        if recommendRoomId != 0:
            re_roomConf = gdata.roomIdDefineMap()[recommendRoomId]
            if re_roomConf:
                re_roomConf = re_roomConf.configure

        ctrlRoomIds = [bigRoomId * 10000 + 1000 for bigRoomId in gdata.gameIdBigRoomidsMap()[gameId]]
        ctrlRoomIds.sort()
        ftlog.debug("_fetchAllRoomInfos", userId, gameId, ctrlRoomIds, recommendRoomId, re_roomConf)
        normalRoomInfos = []
        friendRoomInfos = []
        matchRoomInfos = []
        pointMatchRoomInfos = []
        robberyRoomInfos = []
        grandPrixRoomInfos = []
        poseidonRoomInfos = []

        isLimitedVer = util.isVersionLimit(userId)
        newbieRoomListMode = gamedata.getGameAttr(userId, FISH_GAMEID, ABTestData.newbieRoomListMode)   # 新手房间列表模式
        isFinishAllRedTask = util.isFinishAllRedTask(userId)
        clientVersion = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.clientVersion)
        fpMultipleTestMode = config.getPublic("fpMultipleTestMode") or gamedata.getGameAttr(userId, FISH_GAMEID,
                                                                                            ABTestData.fpMultipleTestMode)  # 渔场倍率AB测试
        for ctlRoomId in ctrlRoomIds:
            pass


        return normalRoomInfos, friendRoomInfos, matchRoomInfos, robberyRoomInfos, \
               pointMatchRoomInfos, grandPrixRoomInfos, poseidonRoomInfos

    @markCmdActionMethod(cmd="module_tip", action="fishUpdate", clientIdVer=0, scope="game", lockParamName="userId")
    def doUpdateModuleTip(self, gameId, userId, modules):
        """更新红点提示"""
        modulesInfo = module_tip.getInfo(userId, modules)
        mo = module_tip.buildInfo(modulesInfo)
        router.sendToUser(mo, userId)
        ftlog.debug("doUpdateModuleTip, userId =", userId, modules, modulesInfo)

    @markCmdActionMethod(cmd="module_tip", action="fishReport", clientIdVer=0, scope="game", lockParamName="userId")
    def doReportModuleTip(self, gameId, userId, modules, values):
        moduleNames = []
        for moduleName in modules:
            module = module_tip.findModuleTip(moduleName)
            if module.needReport:
                moduleNames.append(moduleName)
        modulesInfo = module_tip.delModulesTipValue(userId, moduleNames, values)    # 删除模块tip信息中某个值
        if modulesInfo:
            mo = module_tip.buildInfo(modulesInfo)
            router.sendToUser(mo, userId)