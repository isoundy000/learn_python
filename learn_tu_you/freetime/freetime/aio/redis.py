#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/2

import stackless

from freetime.core.exception import FTException
from freetime.util import log as ftlog
from freetime.util import performance
from freetime.util.defertool import setDefaultCallbackSimple

_NOWAITCMDS_ = frozenset(['SET', 'SETEX', 'HSET', 'HMSET', 'LPUSH', 'SREM', 'EXPIRE',
                          'set', 'setex', 'hset', 'hmset', 'lpush', 'srem', 'expire'])
_REDIS_PERFORMANCE = 1


def _runCmdRedisSlow_(fun, argl, argd):
    """执行cmd 慢速查询日志"""
    return "REDIS argl=" + str(argl[1:])[0:64] + ' fun=' + str(fun) + ' conn=' + str(argl[0])


def _runCmdTxRedis(redis_conn, *argl, **argd):
    """执行redis命令"""
    cmd = argl[0]
    if str(cmd).lower().strip() == 'eval':
        ftlog.warn('SCRIPT EVAL', argl[1])

    d = redis_conn.send(*argl)
    if cmd in _NOWAITCMDS_:
        setDefaultCallbackSimple(d, argl)
        return 1
    r = stackless.getcurrent()._fttask.waitDefer(d)
    return r


def _sendCmdTxRedis(redis_conn, *argl, **argd):
    """发送redis命令"""
    cmd = argl[0]
    if str(cmd).lower().strip() == 'eval':
        ftlog.warn('SCRIPT EVAL', argl[1])

    d = redis_conn.send(*argl)
    setDefaultCallbackSimple(d, argl)
    return 1


def _runCmdTxRedis_(redis_conn, *argl, **argd):
    """查看执行redis命令的操作"""
    funArgl = [redis_conn]
    funArgl.extend(argl)
    return performance.watchSlowCall(_runCmdTxRedis, funArgl, argd, performance.SLOW_CALL_TIME, _runCmdRedisSlow_)


sendCmd = _sendCmdTxRedis
if _REDIS_PERFORMANCE:                          # 查看redis性能
    runCmd = _runCmdTxRedis_
else:
    runCmd = _runCmdTxRedis


def closeAllRedis(redis_pool_map):
    """关闭所有redis链接"""
    ftlog.info('closeAllRedis !!', redis_pool_map)
    for dbkey in redis_pool_map.keys():
        conn = redis_pool_map[dbkey]
        try:
            conn.close()
        except:
            ftlog.error('ERROR CLOSE MYSQL of', dbkey)


def doRedis(poolname, *argl, **argd):
    """执行redis命令"""
    import freetime.entity.config as ftcon
    conn = ftcon.redis_pool_map.get(poolname, None)
    if conn == None:
        raise FTException("doRedis:poolname [" + str(poolname) + "] undefined.")
    return runCmd(conn, *argl, **argd)