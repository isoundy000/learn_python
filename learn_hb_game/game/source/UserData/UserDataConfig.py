#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


from Source.DataBase.Common.DBEngine import DBEngine
from Source.DataBase.Table.t_role import t_role
from Source.DataBase.Table.t_equip4 import t_equip4
from Source.DataBase.Table.t_soul2 import t_soul2


UserDataPrepareMap = {
    "equip": t_equip4,      # 装备
    "soul": t_soul2,        # 武魂

}


UserDataNewUserActivity = {
    # "consumegift": (3 * 24 * 3600 * 1000, t_activity_consumegift),       # 消费有礼
    # "daydaygift": (3 * 24 * 3600 * 1000, t_activity_daydaygift),         # 天天有礼
    # "begin7day": (10 * 24 * 3600 * 1000, t_begin7day_role)                # 开服7天乐
}


UserDataMap = {

}