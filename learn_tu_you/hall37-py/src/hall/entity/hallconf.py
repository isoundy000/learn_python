#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6

from poker.entity.configure import configure, pokerconf
from poker.util import strutil
import freetime.util.log as ftlog
from hall.entity import hallmoduledefault
import json

HALL_GAMEID = 9999
SDK_GAMEID = 9998


def getClientRankTemplateName(rankingKey, clientId):
    """获取大厅44的排行榜 rankingKey=fish_44"""
    intClientId = pokerconf.clientIdToNumber(clientId)
    if intClientId == 0:
        return None

    rankingKeys = configure.getGameJson(HALL_GAMEID, 'ranking', {}, intClientId).get('rankingKeys')
    if not rankingKeys:
        return None

    return rankingKeys.get(rankingKey)