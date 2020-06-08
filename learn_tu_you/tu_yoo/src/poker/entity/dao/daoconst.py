#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/2
from poker.entity.dao import dataschema
from poker.util import city_locator

OFFLINE = 0     # 用户不在线
ONLINE = 1      # 用户在线

ATT_CHIP = 'chip'               # 金币
ATT_COIN = 'coin'
ATT_DIAMOND = 'diamond'         # 钻石

HKEY_GAMEDATA = 'gamedata:'     # 游戏数据




###############################################################################
# USER 数据库数据键值定义
###############################################################################
