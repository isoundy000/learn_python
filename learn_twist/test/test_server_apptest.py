#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/11/20 12:06
# @version: 0.0.1
# @Author: houguangdong
# @File: test_server_apptest.py
# @Software: PyCharm

from learn_twist.server.globalobject import GlobalObject


def netserviceHandle(target):
    GlobalObject().net_factory.service.map_target(target)


@netserviceHandle
def echo_111(_conn, data):
    return data