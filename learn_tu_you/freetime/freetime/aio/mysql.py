#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/3

import stackless
from freetime.core.timer import FTTimer
from freetime.util import log as ftlog, defertool
_keep_count = 0
_keep_alive_seconds = 60                                    # 60秒存活状态


def query(mysqlconn, sqlstr, sql_arg_list=[]):
    """mysql查询"""
    d = mysqlconn.runQuery(sqlstr, sql_arg_list)
    result = stackless.getcurrent()._fttask.waitDefer(d)
    return result


def _keepAlive():
    """是否存活"""
    mysql_pool_map = stackless.getcurrent()._fttask.run_argl[0]
    keepAlive(mysql_pool_map)


def keepAlive(mysql_pool_map):
    """保持存活"""
    global _keep_count, _keep_alive_seconds
    # ftlog.debug('MYSQL keepAlive', len(mysql_pool_map), _keep_count)
    _keep_count += 1
    if _keep_count == 1:
        if len(mysql_pool_map) > 0:
            FTTimer(_keep_alive_seconds, _keepAlive, mysql_pool_map)
        return

    sqlstr = 'select %d' % (_keep_count)
    for dbkey in mysql_pool_map.keys():
        conn = mysql_pool_map[dbkey]
        try:
            defertool.setDefaultCallback(conn.runQuery(sqlstr), __file__, ftlog.getMethodName(), sqlstr)
        except:
            ftlog.error('ERROR MYSQL of', dbkey, 'has connection error ! close !! ')

    FTTimer(_keep_alive_seconds, _keepAlive, mysql_pool_map)


def closeAllMysql(mysql_pool_map):
    """关闭mysql连接池中所有的链接"""
    for dbkey in mysql_pool_map.keys() :
        conn = mysql_pool_map[dbkey]
        try:
            conn.close()
        except:
            ftlog.error('ERROR CLOSE MYSQL of', dbkey)