#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


from logics.skill_logic import skill_tregger_def
from lib.utils import real_rand
from logics.skill_logic.skill_buff import zcBuff
import random


def ZCRealSkill(battle, selfPositionId, skillLv, effect, attr_effect=1.0):
    if selfPositionId < 5:
        friend1 = 0
        friend2 = 1
        friend3 = 2
        friend4 = 3
        friend5 = 4
    else:
        friend1 = 100
        friend2 = 101
        friend3 = 102
        friend4 = 103
        friend5 = 104

    friendlist = battle.getCampAllLife(friend1)     # 获取攻击方的全队友

    ace = battle.getMembers(selfPositionId)

    tempDid = battle.selectEnim(selfPositionId)

    tempDfd = battle.getMembers(tempDid)

    tempHurt = ace['tempMgc'] - tempDfd['Dfs']

    if tempHurt < 1:
        tempHurt = 1

    tempHurt = battle.realHurt(tempDid, tempHurt)

    earth = 1  # 地属性伤害
    water = 2  # 水属性伤害
    fire = 3  # 火属性伤害
    wind = 4  # 风属性伤害

    if ace['tempFire'] > 0:
        attrhurt = ace['tempFire'] * attr_effect - tempDfd['tempFire_dfs']
        if attrhurt < 1:
            attrhurt = 0
        attrhurt = battle.realattrHurt(tempDid, attrhurt)
        battle.updateMsg('skill',
                         {'skillid': 920, 'name': 'skill1', 'src': selfPositionId, 'des': tempDid, 'hurt': tempHurt,
                          'attr_type': fire, 'attr_hurt': attrhurt})
    else:
        battle.updateMsg('skill',
                         {'skillid': 920, 'name': 'skill1', 'src': selfPositionId, 'des': tempDid, 'hurt': tempHurt})

    def buff_ace(battle, positionid):
        tempSelf = battle.getMembers(positionid)
        tempSelf['tempDfs'] += tempSelf['tempDfs'] * effect

    buff = zcBuff('buff_ace', buff_ace, 3, 99, skill_tregger_def.KBUFFKEEP, 103, 103)   # 3 记录剩余循环数 99 效果释放次数 130 buff类型标记，同样类型的buff不能叠加 103 buff分类

    for target in friendlist:
        tempdfd = battle.getMembers(target)
        if tempdfd != 0:
            battle.addBuff(buff, target)

    if ace['bre'] > 1:
        anger = 30
    else:
        anger = 10

    if selfPositionId < 5:
        self = 0
        enemy = 1
    else:
        self = 1
        enemy = 0

    battle.addAnger(self, anger)
    battle.addAnger(enemy, 5)
    return 0