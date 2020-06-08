#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/1
# 每个配置项必须是JSON格式

import freetime.entity.config as tfcon
import freetime.util.log as ftlog
from datetime import datetime
from poker.util import strutil
from freetime.core.lock import FTLock, lock

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

    value = tfcon.getConf(rkey)
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