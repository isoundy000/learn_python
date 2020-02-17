#!/usr/bin/env python
# -*- coding:utf-8 -*-

from common.dbhelper import DBHelperObject
import os
import shutil
from common.configmanager import ConfigManager
import urllib
from tornado.httpclient import HTTPClient
from tornado.httpclient import HTTPRequest
from tornado.escape import json_encode
import json
import logging
from common.cjsonencoder import CJsonEncoder


def database_get_where_condition(condition=None):
    temp = ""
    if condition:
        for c in condition:
            if type(c[-1]) == int or type(c[-1]) == long:
                temp += " and %s%s%d" % (c[0], c[1], c[-1])
            else:
                temp += " and %s%s'%s'" % (c[0], c[1], c[-1])
    return temp


# 数据库通用get  query  支持where条件
def database_all_query_get(table, condition, con=None, get_query=True):
    sql = "select * from %s where 1=1 " % table
    temp = database_get_where_condition(condition)
    sql = "%s%s" % (sql, temp)

    if con:
        common_con = con
    else:
        common_con = DBHelperObject.CONFIG_CON
    if get_query:
        data = common_con.query(sql)
    else:
        data = common_con.get(sql)
    return data


# 数据库执行execute方法
def database_execute(sql, con=None):
    if con:
        count = con.execute(sql)
    else:
        count = DBHelperObject.CONFIG_CON.execute(sql)
    data = {"status": "fail"}
    if count >= 0:
        data["status"] = "success"
    return data


# 数据库通用删除
def database_delete(table, condition, con=None):
    sql = "delete from %s where 1=1" % table

    temp = database_get_where_condition(condition)
    sql = "%s%s" % (sql, temp)
    return database_execute(sql, con)


# 数据库通用获取行数
def database_get_total(table, condition, con=None):
    sql = "select count(*) as total from %s where 1=1" % table

    temp = database_get_where_condition(condition)
    sql = "%s%s" % (sql, temp)
    if con:
        data = con.get(sql)
    else:
        data = DBHelperObject.CONFIG_CON.get(sql)
    total = 0
    if data and data["total"]:
        total = data["total"]
    return total


# 数据库通用获取最大
def database_get_max(table, max_str, condition, con=None, isadd=False):
    sql = "select max(%s) as max_s from %s where 1=1" % (max_str, table)
    temp = database_get_where_condition(condition)
    sql = "%s%s" % (sql, temp)
    if con:
        data = con.get(sql)
    else:
        data = DBHelperObject.CONFIG_CON.get(sql)
    max_id = 0
    if data and data["max_s"]:
        max_id = data["max_s"]
    if isadd:
        max_id += 1
    return max_id


def RequestServer(ip, port, rtype, data=None, method='GET', time_out=60.0):
    left_url = ip if 'http' in ip else 'http://%s' % ip
    port_str = '' if port == '80' else ':%s' % port
    tmp_str = '%s%s' % (port_str, rtype) if rtype.startswith("/") else '%s/%s' % (port_str, rtype)
    url = left_url + tmp_str

    if rtype.startswith("/"):
        url = "http://%s:%s%s" % (ip, port, rtype)
    else:
        url = "http://%s:%s/%s" % (ip, port, rtype)
    if method == 'GET':
        try:
            if data is not None:
                url = "%s?%s" % (url, urllib.urlencode(data))
                http_client = HTTPClient()
                req = HTTPRequest(url, request_timeout=time_out,validate_cert=False)
                response = http_client.fetch(req)
                return response.body
        except Exception as e:
            return json_encode({"status": "fail", "errmsg": str(e)})
    else:
        try:
            http_client = HTTPClient()
            headers = {"Content-Type": "application/json", "charset": "utf-8"}
            json_dump = json.dumps(data, cls=CJsonEncoder)
            req = HTTPRequest(url, headers=headers, method=method, request_timeout=time_out, body=json_dump, validate_cert=False)
            response = http_client.fetch(req)
            return response.body
        except Exception as e:
            import traceback
            print traceback.print_exc()
            return json_encode({"status": "fail", "errmsg": str(e)})