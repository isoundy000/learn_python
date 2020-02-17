#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import datetime
import json
import redis
import settings
import cPickle as pickle

from lib.db import make_redis_client

from lib.utils.debug import print_log


import MySQLdb
escape_string = MySQLdb._mysql.escape_string
from lib.utils import md5


def force_str(text, encoding="utf-8", errors='strict'):
    t_type = type(text)
    if t_type == str:
        return text
    elif t_type == unicode:
        return text.encode(encoding, errors)
    return str(text)


def _smart(v):
    t = type(v)
    if t == str:
        return v
    elif t == unicode:
        return force_str(v)
    elif (t == int) or (t == long) or (t == float):
        return str(v)
    elif t == datetime.datetime:
        return v.strftime("%Y-%m-%d %H:%M:%S")
    return str(v)


def sql_value(dict_data):
    return ','.join(map(
        lambda x: """%s='%s'""" % (
            x[0], escape_string(_smart(x[1])) if x[1] is not None else 'null'
        ),
        dict_data.iteritems()
    ))


class MySQLConnect(object):
    """# ModelPayment: 支付记录，mysql"""
    def __init__(self, mysql_host):
        self.mysql_host = mysql_host
        host_config = self.mysql_host
        self.table_prefix = host_config['table_prefix']
        self.conn = MySQLdb.connect(
            host=host_config['host'],
            user=host_config['user'],
            passwd=host_config['passwd'],
            db=host_config['db'],
            charset="utf8",
        )
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, type, value, trace):
        pass
        # self.cursor.close()
        # self.conn.close()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def execute(self, sql, key):
        sid = int(md5(str(key)), 16)
        table = self.table_prefix + '_' + str(sid % 16)
        sql = sql % table + ';'
        self.cursor.execute(sql)
        self.conn.commit()

    def exists_order_id(self, key):
        sid = int(md5(str(key)), 16)
        table = self.table_prefix + '_' + str(sid % 16)
        return self.cursor.execute('select order_id from %s where order_id="%s";' % (table, key))

    def pay(self, data, user):
        """# insert: docstring
        args:
            arg:    ---    arg
        returns:
            0    ---
        """
        key = data['order_id']
        if self.exists_order_id(key):
            return False
        sql = """insert into %s set """ + sql_value(data)
        self.execute(sql, key)
        return True

def payment_insert(key, data):
    """# insert: docstring
    args:
        arg:    ---    arg
    returns:
        0    ---
    """
    with MySQLConnect(settings.PAYLOG_HOST) as c:
        if c.exists_order_id(key):
            return False
        sql = """insert into %s set """ + sql_value(data)
        c.execute(sql, key)
        return True


def spend_data(key, data):
    """# insert: docstring
    args:
        arg:    ---    arg
    returns:
        0    ---
    """
    with MySQLConnect(settings.SPENDLOG_HOST) as c:
        sql = """insert into %s set """ + sql_value(data)
        c.execute(sql, key)