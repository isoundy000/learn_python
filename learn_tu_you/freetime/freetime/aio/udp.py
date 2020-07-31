#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/3

import stackless


def sendQuery(query_protocol, data, timeout=1):
    """发送查询"""
    d = query_protocol.query(data, timeout)
    return stackless.getcurrent()._fttask.waitDefer(d)