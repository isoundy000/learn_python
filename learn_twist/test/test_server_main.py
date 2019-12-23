#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/11/20 12:01
# @version: 0.0.1
# @Author: houguangdong
# @File: test_server_main.py
# @Software: PyCharm

import json, sys
from learn_twist.server.server import FFServer


if __name__ == '__main__':
    args = sys.argv
    server_name = None
    config = None
    if len(args) > 2:
        server_name = args[1]
        config = json.load(open(args[2], 'r'))
    else:
        raise ValueError

    dbconf = config.get('db')
    memconf = config.get('memcached')
    sersconf = config.get('servers', {})
    masterconf = config.get('master', {})
    serconfig = sersconf.get(server_name)
    ser = FFServer()
    # ser.config(serconfig, dbconfig=dbconf, memconfig=memconf, masterconf=masterconf)
    ser.config(config, server_name)
    ser.start()