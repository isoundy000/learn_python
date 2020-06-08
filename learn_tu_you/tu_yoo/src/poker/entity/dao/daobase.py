#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/2

from datetime import datetime
import json

import freetime.aio.redis as ftred
import freetime.entity.config as ftcon
import freetime.util.log as ftlog
from poker.entity.dao import daoconst
from poker.entity.dao.lua_scripts import room_scripts
from poker.util import keywords
from poker.util import reflection


__luascripts = {}           # luaName: lua实例
__user_redis_conns = []     # 用户数据的REDIS链接, 按userid取模进行数据的存储
__user_redis_conns_len = 0
__table_redis_conns = []    # 桌子数据的REDIS链接, 按userid取模进行数据的存储
__table_redis_conns_len = 0
__mix_redis_conn = None     # MIX库REDIS链接
__forbidden_redis_conn = None
__keymap_redis_conns = []
__keymap_redis_conns_len = 0
__paydata_redis_conn = None
__geo_redis_conn = None
__config_redis_conn = None
__online_redis_conn = None
__replay_redis_conn = None
__rank_redis_conn = None
__dizhu_redis_conn = None
__bi_redis_conn = None
__wechat_friend_redis_conn = None   # 微信好友库的REDIS链接

_REDIS_CMD_PPS_ = 0
_REDIS_CMDS_ = {}
_REDIS_COUNT_ = 0
_REDIS_COUNT_TIME_ = datetime.now()


def _redisCmdPps(group, cmds):
    global _REDIS_CMDS_, _REDIS_COUNT_, _REDIS_COUNT_TIME_
    try:
        if not group is _REDIS_CMDS_:
            _REDIS_CMDS_[group] = {}
        rgroup = _REDIS_CMDS_[group]

        rcmd = str(cmds[0]).upper()
        if len(cmds) > 1:
            rkey = str(cmds[1]).split(':', 1)[0]
            if rkey not in rgroup:
                rgroup[rkey] = {}
            rcmds = rgroup[rkey]
            if rcmd in rcmds:
                rcmds[rcmd] += 1
            else:
                rcmds[rcmd] = 1

        _REDIS_COUNT_ += 1
        # if _REDIS_COUNT_ % _REDIS_COUNT_BLOCK_ == 0:
        #     ct = datetime.now()
        #     dt = ct - _REDIS_COUNT_TIME_
        #     dt = dt.seconds + dt.microseconds / 1000000.0
        #     pps = '%0.2f' % (_REDIS_COUNT_BLOCK_ / dt)
        #     _REDIS_COUNT_TIME_ = ct
        #     ftlog.info("REDIS_PPS", pps, 'CMDCOUNT', _REDIS_COUNT_, 'DT %0.2f' % (dt), 'CMDS', json.dumps(_REDIS_CMDS_))
        #     _REDIS_CMDS_ = {}
    except:
         ftlog.error()


def ppsCountRedisCmd():
    global _REDIS_CMDS_, _REDIS_COUNT_, _REDIS_COUNT_TIME_
    ct = datetime.now()
    dt = ct - _REDIS_COUNT_TIME_
    dt = dt.seconds + dt.microseconds / 1000000.0
    pps = '%0.2f' % (_REDIS_COUNT_ / dt)
    ftlog.hinfo("REDIS_PPS", pps, 'CMDCOUNT', _REDIS_COUNT_, 'DT %0.2f' % (dt), 'CMDS', json.dumps(_REDIS_CMDS_))
    _REDIS_COUNT_TIME_ = ct
    _REDIS_CMDS_ = {}
    _REDIS_COUNT_ = 0


def _initialize():
    global __user_redis_conns, __user_redis_conns_len, __table_redis_conns, __table_redis_conns_len
    global __mix_redis_conn, __keymap_redis_conns, __paydata_redis_conn, __geo_redis_conn
    global __config_redis_conn, __online_redis_conn, __replay_redis_conn, __forbidden_redis_conn
    global __rank_redis_conn, __dizhu_redis_conn, __bi_redis_conn, __keymap_redis_conns_len
    global __wechat_friend_redis_conn

    if __user_redis_conns_len == 0:
        ftlog.debug('_initialize begin->', __name__)
        mlist = reflection.findMethodUnderModule('poker.servers.util.rpc._private', '_initialize')
        for method in mlist:
            method()
        ftlog.debug('_initialize finis->', __name__)

        # loadLuaScripts(room_scripts.)
        __user_redis_conns = _getRedisCluster('user')


def _getRedisCluster(dbnamehead):
    '''
    获取redis组
    :param dbnamehead:
    '''
    rconns = []
    for k, conn in ftcon.redis_pool_map.items():
        if k.startswith(dbnamehead):
            modid = int(k[len(dbnamehead):])
            rconns.append([modid, conn])
    rconns.sort(key=lambda x: x[0])
    if rconns:
        assert (rconns[0][0] == 0)
        assert (rconns[-1][0] == len(rconns) - 1)
        connlist = []
        for x in rconns:
            connlist.append(x[1])
        return connlist
    return []


def loadLuaScripts(luaName, luaScript):
    oldsha = None
    for k in ftcon.redis_pool_map:
        conn = ftcon.redis_pool_map[k]
        shaval = ftred.runCmd(conn, 'script', 'load', luaScript)
        if oldsha == None:
            __luascripts[luaName] = shaval
            oldsha = shaval
        else:
            assert (oldsha == shaval)


def executeUserCmd(uid, *cmds):
    """
    执行玩家的命令
    """
    assert (isinstance(uid, int) and uid > 0)
    cindex = int(uid) % __user_redis_conns_len
    if _REDIS_CMD_PPS_:
        _redisCmdPps('user', cmds)
    ftred.sendCmd(__user_redis_conns[cindex], *cmds)


def filterValues(attrlist, values):
    if (not isinstance(attrlist, list)
        or not isinstance(values, list)
            or len(attrlist) != len(values)):
        return values
    for i in xrange(len(values)):
        values[i] = filterValue(attrlist[i], values[i])
    return values


def executeTableCmd(roomId, tableId, *cmds):
    """
    执行桌子的命令
    """
    assert (isinstance(roomId, int) and roomId > 0)
    assert (isinstance(tableId, int) and tableId >= 0)
    cindex = int(roomId) % __table_redis_conns_len
    if _REDIS_CMD_PPS_:
        _redisCmdPps('table', cmds)
    return ftred.runCmd(__table_redis_conns[cindex], *cmds)