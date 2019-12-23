#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/11/22 15:56
# @version: 0.0.1
# @Author: houguangdong
# @File: gate_server.py
# @Software: PyCharm

from learn_twist.apps.gate import initapp
# from gtwisted.core import reactor
# from gfirefly.server.globalobject import GlobalObject

initapp.load_module()
# initapp.init_guild_rank()
# front_ip = GlobalObject().json_config['front_ip']
# front_port = GlobalObject().json_config['front_port']
# name = GlobalObject().json_config['name']

# def tick():
# GlobalObject().remote('login').callRemote('server_sync', name. front_ip, front_port, 'normal')
#     reactor.callLater(60, tick)
#
# reactor.callLater(3, tick)