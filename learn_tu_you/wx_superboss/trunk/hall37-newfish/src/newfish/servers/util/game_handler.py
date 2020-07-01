#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/14

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from hall.servers.common.base_checker import BaseMsgPackChecker
from newfish.entity import config, gift_system, item, util, daily_gift
from newfish.entity.config import FISH_GAMEID
from newfish.entity.quest import quest_system
from newfish.entity.quest import daily_quest, main_quest
from newfish.entity.chest import chest_system
from newfish.entity.fishactivity import fish_activity_system
from newfish.entity.achievement import achievement_system
from newfish.entity.skill import skill_system
from newfish.entity import fish_notice_system
from newfish.entity.grand_prize_pool import GrandPrizePool          # 巨奖奖池
from newfish.entity import piggy_bank
from newfish.entity import treasure_system
from newfish.entity import level_rewards, level_funds


@markCmdActionHandler
class GameTcpHandler(BaseMsgPackChecker):







    @markCmdActionMethod(cmd="game", action="grand_prix_info", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetGrandPrixInfo(self, userId, gameId, clientId):
        """
        获取大奖赛信息
        """
        ftlog.debug("doGetGrandPrixInfo", userId, gameId, clientId)
        from newfish.entity import grand_prix
        grand_prix.sendGrandPrixInfo(userId)