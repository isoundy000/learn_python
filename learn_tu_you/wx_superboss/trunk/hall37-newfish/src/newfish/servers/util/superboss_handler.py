# -*- coding=utf-8 -*-
"""
概述模块或脚本
"""
# @Author  : Kangxiaopeng
# @Time    : 2020/4/2

from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from hall.servers.common.base_checker import BaseMsgPackChecker
from newfish.entity.superboss import item_exchange, minigame, gameplay


@markCmdActionHandler
class SuperBossHandler(BaseMsgPackChecker):

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

    def _check_param_count(self, msg, key, params):
        value = msg.getParam(key, 0)
        try:
            value = int(value)
        except:
            value = 0
        if value <= 0:
            return "ERROR of count!" + str(value), None
        return None, value

    def _check_param_idx(self, msg, key, params):
        idx = msg.getParam(key)
        if isinstance(idx, int):
            return None, idx
        return "ERROR of idx !" + str(idx), None

    def _check_param_groupIdx(self, msg, key, params):
        groupIdx = msg.getParam(key, 0)
        if isinstance(groupIdx, int):
            return None, groupIdx
        return "ERROR of idx !" + str(groupIdx), None

    def _check_param_mode(self, msg, key, params):
        mode = msg.getParam(key, 0)
        if isinstance(mode, int):
            return None, mode
        return "ERROR of mode !" + str(mode), None

    def _check_param_mgType(self, msg, key, params):
        mgType = msg.getParam(key, 0)
        if isinstance(mgType, (str, unicode)):
            return None, mgType
        return "ERROR of mgType !" + str(mgType), None

    def _check_param_userIds(self, msg, key, params):
        userIds = msg.getParam(key, [])
        if isinstance(userIds, list):
            return None, userIds
        return "ERROR of userIds !" + str(userIds), None

    @markCmdActionMethod(cmd="game", action="superboss_gameplay_info", clientIdVer=0, scope="game", lockParamName="")
    def doGetSuperbosGamePlayInfo(self, userId, gameId, roomId0, clientId, mode=0):
        """
        发送超级boss玩法数据
        """
        gameplay.sendGameplayInfo(roomId0, userId, clientId, mode)

    @markCmdActionMethod(cmd="game", action="superboss_minigame_info", clientIdVer=0, scope="game", lockParamName="")
    def doGetSuperbossMinigameInfo(self, userId, gameId, roomId0, clientId, mode):
        """
        发送超级boss选箱子数据
        """
        minigame.sendMinigameInfo(roomId0, userId, mode)

    @markCmdActionMethod(cmd="game", action="superboss_minigame_show", clientIdVer=0, scope="game", lockParamName="")
    def doPlayMinigameShow(self, userId, gameId, roomId0, clientId, idx, mode, userIds):
        """
        发送巨龙转盘盘面
        """
        minigame.playMinigameShow(roomId0, userId, idx, mode, userIds)

    @markCmdActionMethod(cmd="game", action="superboss_minigame", clientIdVer=0, scope="game", lockParamName="")
    def doPlayMinigame(self, userId, gameId, roomId0, clientId, idx, mode, userIds, groupIdx):
        """
        发送选箱子请求
        """
        minigame.playMinigame(roomId0, userId, idx, mode, userIds, groupIdx)

    @markCmdActionMethod(cmd="game", action="superboss_convert_info", clientIdVer=0, scope="game", lockParamName="")
    def doGetSuperbossConvertInfo(self, userId, gameId, roomId0, clientId, mode):
        """
        发送兑换数据
        """
        item_exchange.sendConvertInfo(roomId0, userId, mode)

    @markCmdActionMethod(cmd="game", action="superboss_convert", clientIdVer=0, scope="game", lockParamName="")
    def doSuperbossConvertItem(self, userId, gameId, roomId0, clientId, idx, count, mode):
        """
        发送兑换请求
        """
        item_exchange.convertItem(roomId0, idx, count, userId, mode)

    @markCmdActionMethod(cmd="game", action="store_superboss_convert_info", clientIdVer=0, scope="game", lockParamName="")
    def doGetStoreSuperbossConvert(self, userId, gameId, clientId, mgType):
        """
        发送商城中兑换数据
        """
        item_exchange.sendStoreConvertInfo(userId, mgType)

    @markCmdActionMethod(cmd="game", action="store_superboss_convert", clientIdVer=0, scope="game", lockParamName="")
    def doStoreSuperbossConvert(self, userId, gameId, clientId, mgType, mode, idx, count):
        """
        发送商城中兑换请求
        """
        item_exchange.storeConvertItem(userId, mgType, mode, idx, count)