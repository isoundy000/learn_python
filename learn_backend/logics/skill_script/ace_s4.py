#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from logics.skill_logic import skill_tregger_def
from lib.utils import real_rand
from logics.skill_logic.skill_buff import zcBuff
import random


def ZCRealSkill(battle, selfPositionId, skillLv, effect, attr_effect=1.0):

    tempAtk = battle.getMembers(selfPositionId)
    enemyList = battle.getMoreEnem(selfPositionId, 5)

    earth = 1  # 地属性伤害
    water = 2  # 水属性伤害
    fire = 3  # 火属性伤害
    wind = 4  # 风属性伤害

    def buff_dfslow(battle, positionid):
        tempself = battle.getMembers(positionid)
        tempself['tempFire_dfs'] = tempself['tempFire_dfs'] - effect * 100

    buff = zcBuff('buff_dfslow', buff_dfslow, 99, 99, skill_tregger_def.KBUFFATTACK, 213, 3)

    battle.updateMsg('skill', {'skillid': 6450, 'name': 'dasheng_s4', 'src': selfPositionId, 'des': enemyList})

    for i in enemyList:
        battle.addBuff(buff, i)

    if selfPositionId < 5:
        self = 0
        enemy = 1
    else:
        self = 1
        enemy = 0

    battle.addAnger(self, 10)
    battle.addAnger(enemy, 5)

    return 0