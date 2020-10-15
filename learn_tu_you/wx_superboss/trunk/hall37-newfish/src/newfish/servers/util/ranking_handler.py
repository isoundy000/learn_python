# -*- coding=utf-8 -*-
"""
Created by lichen on 16/12/13.
"""

from freetime.entity.msg import MsgPack
from poker.protocol import router
from freetime.util import log as ftlog
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from hall.servers.common.base_checker import BaseMsgPackChecker
from newfish.entity import config
from newfish.entity.ranking import ranking_system


@markCmdActionHandler
class RankingTcpHandler(BaseMsgPackChecker):
        
    def _check_param_rankType(self, msg, key, params):
        userId = msg.getParam("userId") or config.ROBOT_MAX_USER_ID
        rankType = msg.getParam("rankType")                     # or ranking_system.getAllTabs(userId)[0]["rankType"]
        if isinstance(rankType, int) and rankType >= 0:
            return None, rankType
        return "ERROR of rankType !" + str(rankType), None

    @markCmdActionMethod(cmd="game", action="fish_ranking", scope="game", clientIdVer=0, lockParamName="userId")
    def doGetRankData(self, gameId, userId, clientId, rankType):
        """
        请求排行榜信息
        """
        ftlog.debug("doGetRankData->", userId)
        mo = MsgPack()
        mo.setCmd("fish_ranking")
        mo.setResult("gameId", gameId)
        mo.setResult("userId", userId)
        mo.setResult("tabs", ranking_system.getRankingTabs(userId, clientId, rankType))
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="game", action="fish_all_ranking", scope="game", clientIdVer=0, lockParamName="userId")
    def doGetAllRankConfs(self, gameId, userId, clientId):
        """
        请求所有排行榜信息
        """
        mo = MsgPack()
        mo.setCmd("fish_all_ranking")
        mo.setResult("gameId", gameId)
        mo.setResult("userId", userId)
        mo.setResult("allRank", ranking_system.getAllTabs(userId))
        router.sendToUser(mo, userId)
        ftlog.debug("doGetAllRankConfs, userId =", userId, "mo =", mo)