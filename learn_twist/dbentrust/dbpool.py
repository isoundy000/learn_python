#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/11/20 11:29
# @version: 0.0.1
# @Author: houguangdong
# @File: dbpool.py
# @Software: PyCharm


from DBUtils.PooledDB import PooledDB
import MySQLdb

DBCS = {'mysql': MySQLdb}


class DBPool(object):

    def initPool(self, **kw):
        self.config = kw
        creator = DBCS.get(kw.get('engine', 'mysql'), MySQLdb)
        self.pool = PooledDB(creator, 5, **kw)

    def connection(self):
        return self.pool.connection()


dbpool = DBPool()