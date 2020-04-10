#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from datetime import datetime

bGameValid = True
dAskUserInfo = {}
gAccMode = 0



#============UserSyncResource2.py===================

#============前端资源热更白名单测试功能================
#============去读配置表config.xml==================
#============大于配置标号的热更内容只有白名单可见=======
gWhiteTestResourceVersion = None

#============评审版本热更过滤========================
#============去读配置表config.xml==================
#============等于配置标号的热更内容都不可见=============
gInvalidClientVersion = None    # 非法的客户端版本号