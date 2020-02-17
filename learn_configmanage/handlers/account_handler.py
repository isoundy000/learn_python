#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging

from common.configmanager import ConfigManager
from common.common_function import RequestServer
from basehandler import BaseHandler
import tornado.web
from logic.systemlog import SystemLogObject
import logging
from tornado.escape import json_decode


def notice_acc_agent():
    log_path = ConfigManager.getvalue("ACCSERVER", "logpath")
    acc_path = ConfigManager.getvalue("ACCSERVER", "path")
    port = ConfigManager.getvalue("ACCSERVER", "port")
    ip = ConfigManager.getvalue("ACCSERVER", "host")
    config_path = ConfigManager.getvalue("ACCSERVER", "config_path")
    pay_port = ""
    if "runport2" in ConfigManager._config_dict["ACCSERVER"]:
        pay_port = ConfigManager.getvalue("ACCSERVER", "runport2")
    if "runport3" in ConfigManager._config_dict["ACCSERVER"]:
        acc_port = ConfigManager.getvalue("ACCSERVER", "runport3")
        res_port = ConfigManager.getvalue("ACCSERVER", "runport")
    else:
        acc_port = ConfigManager.getvalue("ACCSERVER", "runport")
        res_port = ""
    global_port = ConfigManager.getvalue("GLOBALSERVER", "port")
    global_log_path = ConfigManager.getvalue("GLOBALSERVER", "logpath")
    global_config_path = ConfigManager.getvalue("GLOBALSERVER", "config_path")
    global_path = ConfigManager.getvalue("GLOBALSERVER", 'path')
    send_data = {
        "data": {
            "acc": {
                "log_path": log_path,
                "config_path": config_path,
                "acc_path": acc_path,
                "res_port": res_port,
                "acc_port": acc_port,
                "pay_port": pay_port,
            },
            "global": {
                "log_path": global_log_path,
                "config_path": global_config_path,
                "port": global_port,
                "global_path": global_path
            }
        }
    }
    logging.info("init...%s" % send_data)
    RequestServer(ip, port, "init", send_data, method='POST')


def get_account_server_status():
    host_ip = ConfigManager.getvalue("ACCSERVER", "host")
    port = ConfigManager.getvalue("ACCSERVER", "port")
    return RequestServer(host_ip, port, "serverstatus")


def refresh_server_list():
    refresh_server_api = "gm/refreshserver"
    return refresh_all_server_by_api(refresh_server_api)


def refresh_all_server_by_api(api, param=None, gmport_list=None):
    ip = ConfigManager.getvalue("ACCSERVER", "host")
    if gmport_list is None:
        recharge_port = ConfigManager.getvalue("ACCSERVER", "configport")
        acc_port = ConfigManager.getvalue("ACCSERVER", "configport2")
        gmport_list = [acc_port, recharge_port]
        if "configport3" in ConfigManager._config_dict["ACCSERVER"]:
            resource_port = ConfigManager.getvalue("ACCSERVER", "configport3")
            gmport_list.append(resource_port)

    tag = 0
    for port in gmport_list:
        if param is None:
            status = RequestServer(ip, port, api)
        else:
            status = RequestServer(ip, port, api, param)
        try:
            status = json_decode(status)
            if status['status'] == 'success':
                tag += 1
        except Exception as e:
            logging.info('refresh_server_list fail: %s' % e)

    return_status = 'success' if tag == len(gmport_list) else 'fail'
    return {'status': return_status}


def set_service(acc_tag, method, user, real_ip):
    host_ip = ConfigManager.getvalue("ACCSERVER", "host")
    port = ConfigManager.getvalue("ACCSERVER", "port")
    if method == 1 or method == 3:
        opt_str = "账号服务"
    elif method == 2:
        opt_str = "资源服务"
    elif method == 4:
        opt_str = "充值服务"
    else:
        opt_str = "账号总服务"

    send_data = {
        "method": method
    }

    if acc_tag == 1:
        str_ope = "startserver"
        opt_str2 = "启动"
    else:
        str_ope = "stopserver"
        opt_str2 = "关闭"
    logging.info(opt_str2 + opt_str)
    SystemLogObject().insert_log(user, 10, opt_str2 + opt_str, real_ip)
    return RequestServer(host_ip, port, str_ope, send_data)