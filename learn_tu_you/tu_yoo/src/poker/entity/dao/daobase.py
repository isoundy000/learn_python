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
    """初始化redis数据库链接"""
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
        __user_redis_conns_len = len(__user_redis_conns)
        __table_redis_conns = _getRedisCluster('table')
        __table_redis_conns_len = len(__table_redis_conns)
        __mix_redis_conn = ftcon.redis_pool_map.get('mix')                  # 混合
        __forbidden_redis_conn = ftcon.redis_pool_map.get('forbidden')      # 禁止
        __replay_redis_conn = ftcon.redis_pool_map.get('replay')            # 重玩
        __online_redis_conn = ftcon.redis_pool_map.get('online')

        __keymap_redis_conns = ftcon.redis_pool_map.get('keymap')
        if not __keymap_redis_conns:
            __keymap_redis_conns = _getRedisCluster('keymap')
            __keymap_redis_conns_len = len(__keymap_redis_conns)
        else:
            __keymap_redis_conns = [__keymap_redis_conns]
            __keymap_redis_conns_len = 1

        __paydata_redis_conn = ftcon.redis_pool_map.get('paydata')
        __geo_redis_conn = ftcon.redis_pool_map.get('geo')
        __config_redis_conn = ftcon.redis_pool_map.get('config')
        __rank_redis_conn = ftcon.redis_pool_map.get('rank')
        __dizhu_redis_conn = ftcon.redis_pool_map.get('dizhu')
        __bi_redis_conn = ftcon.redis_pool_map.get('bi')
        if __bi_redis_conn == None:
            __bi_redis_conn = ftcon.redis_pool_map.get('mix')

        __wechat_friend_redis_conn = ftcon.redis_config_map.get('friend')


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


def preLoadLuaScript(scriptModule, luaScript):
    """前置加载lua脚本"""
    assert(isinstance(luaScript, (str, unicode)))
    scriptName = None
    for x in dir(scriptModule):
        if luaScript == getattr(scriptModule, x):
            scriptName = x
    assert(isinstance(scriptName, (str, unicode)))
    oldsha = None
    for k in ftcon.redis_pool_map:
        conn = ftcon.redis_pool_map[k]
        shaval = ftred.runCmd(conn, 'script', 'load', luaScript)
        if oldsha == None:
            __luascripts[scriptName] = shaval
            oldsha = shaval
        else:
            assert(oldsha == shaval)
    ftlog.info('LOADSCRIPT->', oldsha, scriptName, luaScript)
    setattr(scriptModule, scriptName, scriptName)
    return oldsha


def loadLuaScripts(luaName, luaScript):
    """加载lua脚本"""
    oldsha = None
    for k in ftcon.redis_pool_map:
        conn = ftcon.redis_pool_map[k]
        shaval = ftred.runCmd(conn, 'script', 'load', luaScript)
        if oldsha == None:
            __luascripts[luaName] = shaval
            oldsha = shaval
        else:
            assert (oldsha == shaval)
    ftlog.info('LOADSCRIPT->', oldsha, luaName, luaScript)
    return oldsha


def getLuaScriptsShaVal(luaName):
    """获取lua脚本ShaVal"""
    return __luascripts[luaName]


def filterValue(attr, value):
    """过滤的值"""
    if attr in daoconst.FILTER_KEYWORD_FIELDS:
        value = unicode(value)
        return keywords.replace(value)
    return value


def filterValues(attrlist, values):
    """过滤多个值"""
    if (not isinstance(attrlist, list) or not isinstance(values, list) or len(attrlist) != len(values)):
        return values
    for i in xrange(len(values)):
        values[i] = filterValue(attrlist[i], values[i])
    return values


def executeUserCmd(uid, *cmds):
    """
    执行玩家的命令
    """
    assert (isinstance(uid, int) and uid > 0)
    cindex = int(uid) % __user_redis_conns_len
    if _REDIS_CMD_PPS_:
        _redisCmdPps('user', cmds)
    ftred.sendCmd(__user_redis_conns[cindex], *cmds)


def sendUserCmd(uid, *cmds):
    """发送玩家cmd"""
    assert (isinstance(uid, int) and uid > 0)
    cindex = int(uid) % __user_redis_conns_len
    if _REDIS_CMD_PPS_:
        _redisCmdPps('user', cmds)
    return ftred.runCmd(__user_redis_conns[cindex], *cmds)


def executeUserLua(uid, luaName, *cmds):
    """执行用户的lua
    Redis Evalsha 命令根据给定的 sha1 校验码，执行缓存在服务器中的脚本。
    将脚本缓存到服务器的操作可以通过 SCRIPT LOAD 命令进行。
    这个命令的其他地方，比如参数的传入方式，都和 EVAL 命令一样。
    """
    assert(isinstance(uid, int) and uid > 0)
    cindex = int(uid) % __user_redis_conns_len
    shaval = getLuaScriptsShaVal(luaName)
    if _REDIS_CMD_PPS_:
        _redisCmdPps('user', ['EVALSHA', luaName])
    return ftred.runCmd(__user_redis_conns[cindex], 'EVALSHA', shaval, *cmds)


def _getUserDbClusterSize():
    """获取数据库客户的大小"""
    return __user_redis_conns_len


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


def executeTableLua(roomId, tableId, luaName, *cmds):
    """
    执行桌子的lua
    """
    assert (isinstance(roomId, int) and roomId > 0)
    assert (isinstance(tableId, int) and tableId >= 0)
    cindex = int(roomId) % __table_redis_conns_len
    shaval = getLuaScriptsShaVal(luaName)
    if _REDIS_CMD_PPS_:
        _redisCmdPps('table', ['EVALSHA', luaName])
    return ftred.runCmd(__table_redis_conns[cindex], 'EVALSHA', shaval, *cmds)


def executeForbiddenCmd(*cmds):
    """执行禁止的cmd"""
    if __forbidden_redis_conn:
        if _REDIS_CMD_PPS_:
            _redisCmdPps('forbidden', cmds)
        return ftred.runCmd(__forbidden_redis_conn, *cmds)


def executeMixCmd(*cmds):
    """执行混合的cmd"""
    if _REDIS_CMD_PPS_:
        _redisCmdPps('mix', cmds)
    return ftred.runCmd(__mix_redis_conn, *cmds)


def executeMixLua(luaName, *cmds):
    """执行lua脚本"""
    if _REDIS_CMD_PPS_:
        _redisCmdPps('mix', ['EVALSHA', luaName])
    shaval = getLuaScriptsShaVal(luaName)
    return ftred.runCmd(__mix_redis_conn, 'EVALSHA', shaval, *cmds)


def executeRePlayCmd(*cmds):
    """执行玩家cmd"""
    if _REDIS_CMD_PPS_:
        _redisCmdPps('replay', cmds)
    return ftred.runCmd(__replay_redis_conn, *cmds)


def executeRePlayLua(luaName, *cmds):
    """执行玩家lua脚本"""
    if _REDIS_CMD_PPS_:
        _redisCmdPps('replay', ['EVALSHA', luaName])
    shaval = getLuaScriptsShaVal(luaName)
    return ftred.runCmd(__replay_redis_conn, 'EVALSHA', shaval, *cmds)


def _executeOnlineCmd(*cmds):
    """执行在线cmd"""
    if _REDIS_CMD_PPS_:
        _redisCmdPps('online', cmds)
    return ftred.runCmd(__online_redis_conn, *cmds)


def _executeOnlineLua(luaName, *cmds):
    """执行在线lua"""
    shaval = getLuaScriptsShaVal(luaName)
    if _REDIS_CMD_PPS_:
        _redisCmdPps('online', ['EVALSHA', luaName])
    return ftred.runCmd(__online_redis_conn, 'EVALSHA', shaval, *cmds)


def _executeBiCmd(*cmds):
    """执行BI cmd"""
    if _REDIS_CMD_PPS_:
        _redisCmdPps('bi', cmds)
    return ftred.runCmd(__bi_redis_conn, *cmds)


def _sendBiCmd(*cmds):
    """发送BI cmd"""
    ftred.sendCmd(__bi_redis_conn, *cmds)


def _executeBiLua(luaName, *cmds):
    """执行Bi lua"""
    shaval = getLuaScriptsShaVal(luaName)
    if _REDIS_CMD_PPS_:
        _redisCmdPps('bi', ['EVALSHA', luaName])
    return ftred.runCmd(__bi_redis_conn, 'EVALSHA', shaval, *cmds)


def _executeKeyMapCmd(*cmds):
    """执行KeyMap的cmd"""
    if _REDIS_CMD_PPS_:
        _redisCmdPps('keymap', cmds)
    if __keymap_redis_conns_len == 1:
        return ftred.runCmd(__keymap_redis_conns[0], *cmds)
    else:
        idx = abs(hash(cmds[1]))
        conn = __keymap_redis_conns[idx % __keymap_redis_conns_len]
        return ftred.runCmd(conn, *cmds)


def _executeKeyMapLua(luaName, *cmds):
    """执行KeyMap的lua脚本"""
    raise Exception('_executeKeyMapLua not implement _executeKeyMapLua !')


def _executePayDataCmd(*cmds):
    """执行支付的cmd"""
    if _REDIS_CMD_PPS_:
        _redisCmdPps('paydata', cmds)
    return ftred.runCmd(__paydata_redis_conn, *cmds)


def _executePayDataLua(luaName, *cmds):
    """执行lua脚本"""
    shaval = getLuaScriptsShaVal(luaName)
    if _REDIS_CMD_PPS_:
        _redisCmdPps('paydata', ['EVALSHA', luaName])
    return ftred.runCmd(__paydata_redis_conn, 'EVALSHA', shaval, *cmds)


def _executeGeoCmd(*cmds):
    """执行geo的cmd"""
    if _REDIS_CMD_PPS_:
        _redisCmdPps('geo', cmds)
    return ftred.runCmd(__geo_redis_conn, *cmds)


def _sendGeoCmd(*cmds):
    """发送geo的cmd"""
    ftred.sendCmd(__geo_redis_conn, *cmds)


def _executeGeoLua(luaName, *cmds):
    """执行geo的lua脚本"""
    shaval = getLuaScriptsShaVal(luaName)
    if _REDIS_CMD_PPS_:
        _redisCmdPps('geo', ['EVALSHA', luaName])
    return ftred.runCmd(__geo_redis_conn, 'EVALSHA', shaval, *cmds)


def sendRankCmd(*cmds):
    """发送rank的cmd"""
    if _REDIS_CMD_PPS_:
        _redisCmdPps('rank', cmds)
    ftred.sendCmd(__rank_redis_conn, *cmds)


def executeRankCmd(*cmds):
    """执行rank的cmd"""
    if _REDIS_CMD_PPS_:
        _redisCmdPps('rank', cmds)
    return ftred.runCmd(__rank_redis_conn, *cmds)


def executeRankLua(luaName, *cmds):
    """执行rank的lua"""
    if _REDIS_CMD_PPS_:
        _redisCmdPps('rank', ['EVALSHA', luaName])
    shaval = getLuaScriptsShaVal(luaName)
    return ftred.runCmd(__rank_redis_conn, 'EVALSHA', shaval, *cmds)


def executeWechatFriendCmd(*cmds):
    """执行微信好友cmd"""
    if _REDIS_CMD_PPS_:
        _redisCmdPps('friend', cmds)
    return ftred.runCmd(__wechat_friend_redis_conn, *cmds)


def executeWecahtFriendLua(luaName, *cmds):
    """执行微信好友lua脚本"""
    if _REDIS_CMD_PPS_:
        _redisCmdPps('friend', ['EVALSHA', luaName])
    shaval = getLuaScriptsShaVal(luaName)
    return ftred.runCmd(__wechat_friend_redis_conn, 'EVALSHA', shaval, *cmds)


def sendDizhuCmd(*cmds):
    """发送地主的cmd"""
    if _REDIS_CMD_PPS_:
        _redisCmdPps('dizhu', cmds)
    ftred.sendCmd(__dizhu_redis_conn, *cmds)


def executeDizhuCmd(*cmds):
    """执行地主cmd"""
    if _REDIS_CMD_PPS_:
        _redisCmdPps('dizhu', cmds)
    return ftred.runCmd(__dizhu_redis_conn, *cmds)


def executeDizhuLua(luaName, *cmds):
    """执行地主lua脚本"""
    if _REDIS_CMD_PPS_:
        _redisCmdPps('dizhu', ['EVALSHA', luaName])
    shaval = getLuaScriptsShaVal(luaName)
    return ftred.runCmd(__dizhu_redis_conn, 'EVALSHA', shaval, *cmds)