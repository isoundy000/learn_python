#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/9

import freetime.util.log as ftlog
from poker.entity.configure import pokerconf
from poker.entity.dao import userdata
from poker.entity.dao.daoconst import UserSessionSchema
from poker.util import strutil


def getClientId(userId):
    '''
    取得用户的当前的客户端ID
    '''
    datas = userdata.getSessionData(userId)
    return datas[UserSessionSchema.CLIENTID]


def getCityZip(userId):
    """
    最后登录时的城市代码数据
    """
    datas = userdata.getSessionData(userId)
    return datas[UserSessionSchema.CITYCODE][0]


def getCityName(userId):
    """
    获取城市名称
    :param userId:
    :return:
    """
    datas = userdata.getSessionData(userId)
    name = datas[UserSessionSchema.CITYCODE][1]         # 最后登录时的城市代码数据
    if name:
        return name
    else:
        return '全国'


def getClientIp(userId):
    """
    获取ClientIp
    :param userId:
    :return:
    """
    datas = userdata.getSessionData(userId)
    return datas[UserSessionSchema.IPADDRESS]


def getGameId(userId):
    """
    获取游戏Id
    :param userId:
    :return:
    """
    datas = userdata.getSessionData(userId)
    return datas[UserSessionSchema.APPID]


def getDeviceId(userId):
    """
    获取设备ID
    :param userId:
    :return:
    """
    datas = userdata.getSessionData(userId)
    return datas[UserSessionSchema.DEVICEID]


def getConnId(userId):
    """
    获取
    :param userId:
    :return:
    """
    datas = userdata.getSessionData(userId)
    return datas[UserSessionSchema.CONN]                    # 当前接入的CO进程的ID


def getClientIdInfo(userId):
    '''
    取得用户的当前的客户端ID的分解信息
    返回: 客户端的OS, 客户端的版本, 客户端的渠道, 客户端ID
    '''
    clientId = getClientId(userId)
    clientOs, clientVer, clientChannel = strutil.parseClientId(clientId)
    return clientOs, clientVer, clientChannel, clientId


def getClientIdMainChannel(clientId):
    mainChannel = None
    if isinstance(clientId, (str, unicode)):
        fields = clientId.split(".")
        if len(fields) > 2:
            mainChannel = fields[-2]
    return mainChannel


def _parseClientIdNum(clientId):
    """
    解析客户端数字
    :param clientId:
    :return:
    """
    if isinstance(clientId, (str, unicode)):
        return pokerconf.clientIdToNumber(clientId)
    elif isinstance(clientId, (int, float)):
        return int(clientId)
    return 0


def getClientIdNum(userId, clientId=None):
    '''
    取得用户的当前的客户端ID的数字ID
    '''
    if clientId:
        clientNum = _parseClientIdNum(clientId)
        if clientNum:
            return clientId, clientNum
    ci = None
    if userId:
        ci = getClientId(userId)
        if ci:
            clientNum = _parseClientIdNum(ci)
            if clientNum:
                return ci, clientNum
    ftlog.error('getClientIdNum clientId=', clientId, 'ci=', ci, 'userId=', userId, 'UnknownClientId Final')
    return '', 0


def getClientIdSys(userId):
    """客户端的OS, 客户端的版本, 客户端的渠道, 客户端ID"""
    clientOs, _, _, _ = getClientIdInfo(userId)
    return clientOs


def getClientIdVer(userId):
    """客户端的OS, 客户端的版本, 客户端的渠道, 客户端ID"""
    _, clientVer, _, _ = getClientIdInfo(userId)
    return clientVer


def getClientIdChanel(userId):
    """客户端的OS, 客户端的版本, 客户端的渠道, 客户端ID"""
    _, _, clientChannel, _ = getClientIdInfo(userId)
    return clientChannel