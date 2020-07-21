#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/8
import time
import json

import freetime.util.log as ftlog
from poker.util import strutil
from poker.entity.configure import gdata
from poker.protocol.rpccore import markRpcCall
from poker.entity.dao import userchip, userdata, gamedata
from poker.protocol import router
from hall.entity import hallvip
from hall.entity import hallpopwnd, hallproductselector
from hall.entity.todotask import TodoTaskHelper
from newfish.entity import config, weakdata, led
from newfish.entity.redis_keys import GameData
from newfish.entity.config import FISH_GAMEID


lastSendTime = time.time()


def sendLed(gameId, msgstr, ismgr=1, scope="44", clientIds=None, isMatch=0, type="old", userId=None, id="", lang="zh"):
    """
    :param gameId: 消息所属游戏
    :param msgstr: 消息内容
    :param ismgr: 是否由系统发送
    :param scope: 接收范围
    :param clientIds: 接收clientIds
    :param isMatch: 是否不受发送间隔限制
    :param type: 消息显示样式
    :param userId: 只发送给特定玩家
    :param id: 消息内容ID
    """
    ftlog.debug("sendLed", gameId, msgstr, ismgr, scope, isMatch, type, userId, id, lang)



    return 0



def sendTodoTaskBuyChip(userId, roomId):
    from newfish.entity import util
    clientId = util.getClientId(userId)


    return 0