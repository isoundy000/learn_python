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



def sendTodoTaskBuyChip(userId, roomId):
    from newfish.entity import util
    clientId = util.getClientId(userId)


    return 0