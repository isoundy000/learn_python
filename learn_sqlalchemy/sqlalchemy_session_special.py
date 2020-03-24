#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# at the module level, the global sessionmaker,
# bound to a specific Engine
Session = sessionmaker(bind=engine)

# later, some unit of code wants to create a
# Session that is bound to a specific Connection
conn = engine.connect()
session = Session(bind=conn)
# 将会话与特定连接关联的典型基本原理是维护外部事务的测试夹具—请参阅将会话连接到外部事务(例如测试套件)中的示例。