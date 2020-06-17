#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/1
# 每个配置项必须是JSON格式

import freetime.entity.config as ftcon
import freetime.util.log as ftlog
from datetime import datetime
from poker.util import strutil
from freetime.core.lock import FTLock, lock

UNKNOW_ID = 0               # 未知的或错误的clientId, 未知的或错误的商品定义, 未知的或错误的商品定义
DEFAULT_CLIENT_ID = 0       # 缺省的clientid的数值
CLIENT_ID_TEMPLATE = 'tc'
CLIENT_ID_MATCHER = 'vc'
CLIENTID_RPC = 'Android_3.7_-hall6-RPC'
CLIENTID_SYSCMD = 'Android_3.7_-hall6-SYSCMD'
CLIENTID_ROBOT = 'robot_3.7_-hall6-robot'

_CONFIG_CMD_PPS_ = 0
_CONFIG_CMDS_ = {}
_CONFIG_COUNT_ = 0
_CONFIG_COUNT_TIME_ = datetime.now()


def _configCmdPps(ckey):
    global _CONFIG_CMDS_, _CONFIG_COUNT_, _CONFIG_COUNT_TIME_
    try:
        i = ckey.rfind(':')
        if i > 0:
            ckey = ckey[0:i]

        if not ckey in _CONFIG_CMDS_:
            _CONFIG_CMDS_[ckey] = 1
        else:
            _CONFIG_CMDS_[ckey] += 1

        _CONFIG_COUNT_ += 1
        # if _CONFIG_COUNT_ % _CONFIG_COUNT_BLOCK_ == 0:
        #     ct = datetime.now()
        #     dt = ct - _CONFIG_COUNT_TIME_
        #     dt = dt.seconds + dt.microseconds / 1000000.0
        #     pps = '%0.2f' % (_CONFIG_COUNT_BLOCK_ / dt)
        #     _CONFIG_COUNT_TIME_ = ct
        #     ftlog.info("CONFIG_PPS", pps, 'CMDCOUNT', _CONFIG_COUNT_, 'DT %0.2f' % (dt), 'CMDS', strutil.dumps(_CONFIG_CMDS_))
        #     _CONFIG_CMDS_ = {}
    except:
        ftlog.error()


def ppsCountConfigCmds():
    global _CONFIG_CMDS_, _CONFIG_COUNT_, _CONFIG_COUNT_TIME_
    ct = datetime.now()
    dt = ct - _CONFIG_COUNT_TIME_
    dt = dt.seconds + dt.microseconds / 1000000.0
    pps = '%0.2f' % (_CONFIG_COUNT_ / dt)
    ftlog.hinfo("CONFIG_PPS", pps, 'CMDCOUNT', _CONFIG_COUNT_, 'DT %0.2f' % (dt), 'CMDS', strutil.dumps(_CONFIG_CMDS_))
    _CONFIG_COUNT_TIME_ = ct
    _CONFIG_CMDS_ = {}
    _CONFIG_COUNT_ = 0


def reloadKeys(keylist):
    """
    重载keylist
    """
    if len(keylist) == 1 and keylist[0] == 'all':
        ftcon.getConf.clear()
    else:
        ftcon.getConf.clear_keys(keylist)
    _templatesCache.clear()


def _get(redisfullkey, defaultvalue=None, intClientidNum=None):
    '''
    获取数据
    :param redisfullkey:
    :param defaultvalue:
    :param intClientidNum:
    :return:
    '''
    if intClientidNum == None:
        rkey = redisfullkey
    else:
        rkey = redisfullkey + ':' + str(intClientidNum)

    if _CONFIG_CMD_PPS_:
        _configCmdPps(rkey)

    value = ftcon.getConf(rkey)
    if value == None:
        ftlog.debug('get configer->', rkey, 'is None !!')
        value = defaultvalue
    if value:
        if not isinstance(value, (list, dict)):
            raise Exception('the configer content is not list or dict !' + rkey)
    return value


def getGameJson(gameId, key, defaultVal=None, iniClientidNum=0):
    '''
    取得配置系统的一个游戏相关的键值的json对象值(list或dict类型) gameId: 44, key: pulic
    '''
    return _get('game:' + str(gameId) + ':' + key, defaultVal, iniClientidNum)


def stringIdToNumber(datakey, stringid):
    '''字符串Id转数字'''
    if stringid == 'UNKNOWN':
        return UNKNOW_ID
    if isinstance(stringid, int):
        return stringid
    numDict = _get(datakey, {})
    if not numDict:
        ftlog.warn('configure.stringIdToNumber', datakey, 'NotConfig')
        return UNKNOW_ID
    num = numDict.get(stringid, UNKNOW_ID)
    if num == UNKNOW_ID:
        if stringid.find('robot') >= 0:     # 机器人的clientid忽略
            return UNKNOW_ID
    if num <= 0:
        ftlog.warn('stringIdToNumber Error %s %s "%s"' % (datakey, type(stringid), stringid))
        return UNKNOW_ID
    """
    try:
        assert(num > 0), 'stringIdToNumber Error %s %s "%s"' %(datakey, type(stringid), stringid)
    except:
        ftlog.error()
    """
    return num


def clientIdToNumber(clientId):
    '''
    转换clientID的字符串定义至INTEGER_ID的定义
    '''
    if clientId == CLIENTID_RPC or clientId == CLIENTID_SYSCMD or clientId == CLIENTID_ROBOT:
        return 10000
    return stringIdToNumber('poker:map.clientid', clientId)