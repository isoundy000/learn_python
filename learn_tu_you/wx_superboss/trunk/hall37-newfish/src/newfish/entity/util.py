#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/3

from poker.entity.dao import sessiondata, userchip, onlinedata
from newfish.entity import config, weakdata, keywords


def getClientId(userId):
    """
    获得客户端标识
    """
    if userId < 10000:
        clientId = config.CLIENTID_ROBOT
    else:
        clientId = sessiondata.getClientId(userId)
    return clientId


def getLanguage(userId, clientId=None):
    """
    获取玩家手机语言
    """
    clientId = clientId or getClientId(userId)
    if clientId and config.getPublic("multipleLangClientIds", []):
        lang = userdata.getAttr(userId, "lang")
        if lang and not str(lang).startswith("zh"):
            return "en"
    return "zh"