#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/12/3 22:39
# @version: 0.0.1
# @Author: houguangdong
# @File: init_txredisapi.py
# @Software: PyCharm

"""
初始化全局redis pool
"""

from twisted.python import log

from learn_twist.dbentrust.tx_redis import txredisapi
from learn_twist.server.globalobject import GO

log.msg(GO.json_config)

redis_config = GO.json_config['redis']
host = redis_config['host']
port = redis_config['port']
password = redis_config['password']
db = redis_config['db']


rc = txredisapi.lazyConnectionPool(host=host, port=port, dbid=db, password=password if password else None, poolsize=10)