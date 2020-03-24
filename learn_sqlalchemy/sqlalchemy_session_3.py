#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# 如何为某个对象获得会话?
# 使用会话时可用的object_session()类方法:
# session = Session.object_session(someobject)

# 更新的运行时检查API系统也可以使用:
# from sqlalchemy import inspect
# session = inspect(someobject).session