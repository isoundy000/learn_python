#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/30
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.entity.dao import sessiondata


class BaseMsgPackChecker(object):

    def _check_param_userId(self, msg, key, params):
        userId = msg.getParam(key)
        if userId and isinstance(userId, int):
            return None, userId
        return 'ERROR of userId !' + str(userId), None

    def _check_param_gameId(self, msg, key, params):
        gameId = msg.getParam(key)
        if gameId and isinstance(gameId, int):
            return None, gameId
        appId = msg.getParam('appId')
        if appId and isinstance(appId, int):
            return None, appId
        return 'ERROR of gameId !' + str(gameId), None

    def _check_param_clientId(self, msg, key, params):
        clientId = msg.getKey(key)
        if clientId and isinstance(clientId, (str, unicode)):
            return None, clientId
        clientId = msg.getParam(key)
        if clientId and isinstance(clientId, (str, unicode)):
            return None, clientId
        ftlog.debug('ERROR !! the msg clientId is not found use session clientId !', msg)
        userId = msg.getParam('userId')
        if userId :
            clientId = sessiondata.getClientId(userId)
            if clientId and isinstance(clientId, (str, unicode)):
                return None, clientId
        return 'ERROR of clientId !' + str(clientId), None

