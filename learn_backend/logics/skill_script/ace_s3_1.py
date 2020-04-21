#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

"""
三角头2技能
群攻，降攻
"""
from logics.skill_logic import skill_tregger_def
from lib.utils import real_rand
from logics.skill_logic.skill_buff import zcBuff
import random


def ZCRealSkill(battle, selfPositionId, skillLv, effect, attr_effect=1.0):
    enemylist = battle.getMoreEnem(selfPositionId, 5)   # 得到更多的敌人没有重复
    hurtlist = []
    attrhurtlist = []

    earth = 1  # 地属性伤害
    water = 2  # 水属性伤害
    fire = 3  # 火属性伤害
    wind = 4  # 风属性伤害

    tempAtk = battle.getMembers(selfPositionId)

    buffhurt = 0.05
    rand = 50
    if tempAtk['bre'] > 2:
        buffhurt = 0.1
        rand = 100

    def buff_fire(battle, positionid):
        tempDfd = battle.getMembers(positionid)
        tempHurt = tempDfd['hp'] * buffhurt
        if tempHurt > tempAtk['phsc'] * 0.5:
            tempHurt = tempAtk['phsc'] * 0.5
        tempHurt = battle.realHurt(positionid, tempHurt)
        battle.updateMsg('buff_skill', {'name': 'buff_fire_skill', 'src': positionid, 'des': positionid, 'hurt': tempHurt})

    buff = zcBuff('buff_fire', buff_fire, 3, 99, skill_tregger_def.KBUFFATTACK, 1002, 8)

    for target in enemylist:
        tempdfd = battle.getMembers(target)
        if tempdfd != 0:
            dfs = tempdfd['tempDfs']
            atk = tempAtk['tempMgc']
            tempHurt = atk * effect - dfs
            if tempHurt < 1:
                tempHurt = 1
            tempHurt = battle.realHurt(target, tempHurt)

            if tempAtk['tempFire'] > 0:
                attrhurt = tempAtk['tempFire'] * attr_effect - tempdfd['tempFire_dfs']
                if attrhurt < 1:
                    attrhurt = 0
                attrhurt = battle.realattrHurt(target, attrhurt)
                attrhurtlist.append(attrhurt)
            hurtlist.append(tempHurt)
        else:
            hurtlist.append(0)

    if attrhurtlist:
        battle.updateMsg('skill',
                         {'skillid': 930, 'name': 'ace_s3', 'src': selfPositionId, 'des': enemylist, 'hurt': hurtlist,
                          'att_type': fire, 'attr_hurt': attrhurtlist})
    else:
        battle.updateMsg('skill',
                         {'skillid': 930, 'name': 'ace_s3', 'src': selfPositionId, 'des': enemylist, 'hurt': hurtlist})

    for target in enemylist:
        tempdfd = battle.getMembers(target)
        temprand = real_rand.myRand()
        if tempdfd != 0 and temprand <= rand:
            battle.addBuff(buff, target)

    if selfPositionId < 5:
        self = 0
        enemy = 1
    else:
        self = 1
        enemy = 0
    battle.addAnger(self, 10)
    battle.addAnger(enemy, 5)
    return 0