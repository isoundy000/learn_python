#!/usr/bin/env python
# -*- coding:utf-8 -*-
import traceback
import tornado.gen
import tornado.web
import datetime
from tornado.escape import json_decode
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPClient
import tornado.ioloop
from basehandler import BaseHandler
from common.common_function import *
from common.configmanager import ConfigManager
from common.dbhelper import DBHelperObject


def notice_agent(ip=""):
    # 获取agent服务器的IP地址和端口
    if ip:
        game_list = query_all_server(ip=ip)
    else:
        game_list = query_all_server()
    agent_port = ConfigManager.getvalue("Agent", "port")
    game_dict = {}
    if game_list:
        for ga in game_list:
            if ga["ip"] not in game_dict:
                game_dict[ga["ip"]] = {}
            game_dict[ga["ip"]][ga["gameid"]] = ga
            game_dict[ga["ip"]][ga["gameid"]]["port"] = ga["port"]

        for g in game_dict:
            send_data = {"data": game_dict[g]}
            RequestServer(g, agent_port, "init", send_data, method='POST')


def query_all_server(status='', section=0, ip='', extranet_ip='', filter_info=''):
    sql = "select t1.*, t2.name section_name from t_server t1, t_section t2 where t1.section = t2.id "
    if status:
        sql += " and status='%s'" % status
    if section:
        sql += " and section=%d" % section
    if ip:
        sql += " and ip='%s'" % ip
    if extranet_ip:
        sql += " and extranet_ip='%s'" % extranet_ip
    if filter_info:
        sql += filter_info
    sql += " order by gameid"
    return DBHelperObject.CONFIG_CON.query(sql)