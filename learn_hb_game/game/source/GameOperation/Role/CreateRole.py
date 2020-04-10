#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


from Source.GameConfig.GameConfigManager2 import GameConfigManager
from Source.DataBase.Table.t_server_nextrid import t_server_nextrid


def CreateRole(role, server=None):
    '''
    创建角色
    :param role:
    :param server:
    :return:
    '''
    gameConfig = GameConfigManager.Data()
    roleExpConfig = gameConfig["role_exp"]
    vipConfig = gameConfig["vip"]["0"]
    level1Config = roleExpConfig[str(1)]
    role.name = unicode("", "utf-8")
    role.vip = 1
    role.exp = 0
    role.coin = 0
    role.gold = 0
    role.maxstamina = level1Config["maxstamina"]
    role.stamina = role.maxstamina
    role.maxenergy = level1Config["maxenergy"]
    role.energy = role.maxenergy
    role.maxslot = 1
    role.athletics = vipConfig["athletics"]         # 竞技场剩余的次数

    if server:
        role.id = t_server_nextrid.NextServerRid(server)