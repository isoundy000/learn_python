#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


from logics.skill_logic import skill_tregger_def
from lib.utils import real_rand
from logics.skill_logic.skill_buff import zcBuff
import random


def ZCRealSkill(battle, selfPositionId, skillLv, effect, attr_effect=1.0):

    tempAtk = battle.getMembers(selfPositionId)     # 获得触发者数据   获得攻击者数据
    tempDid = battle.selectEnim(selfPositionId)     # 获得默认攻击目标id

    tempDfd = battle.getMembers(tempDid)
    if battle.isHaveBuffTerm(tempDid, 8):           # 8是组的id
        effect += 1                                 # 效果
    if tempAtk['bre'] > 0:
        effect += 0.3

    tempHurt = tempAtk['tempMgc'] * effect - tempAtk['tempDfs']

    if tempHurt < 1:
        tempHurt = 1

    tempHurt = battle.realHurt(tempDid, tempHurt)

    earth = 1  # 地属性伤害
    water = 2  # 水属性伤害
    fire = 3  # 火属性伤害
    wind = 4  # 风属性伤害

    if tempAtk['tempFire'] > 0:
        attrhurt = tempAtk['tempFire'] * attr_effect - tempDfd['tempFire_dfs']
        if attrhurt < 1:
            attrhurt = 0

        attrhurt = battle.realattrHurt(tempDid, attrhurt)
        battle.updateMsg('skill', {'skillid': 910, 'name': 'ace_s1', 'src': selfPositionId, 'des': tempDid, 'hurt': tempHurt, 'attr_type': fire, 'attr_hurt': attrhurt})
    else:
        battle.updateMsg('skill', {'skillid': 910, 'name': 'ace_s1', 'src': selfPositionId, 'des': tempDid, 'hurt': tempHurt})


    if selfPositionId < 5:
        self = 0
        enemy = 1
    else:
        self = 1
        enemy = 0

    battle.addAnger(self, 10)
    battle.addAnger(enemy, 5)

    return 0