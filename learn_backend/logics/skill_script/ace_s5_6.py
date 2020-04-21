#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


from logics.skill_logic import skill_tregger_def
from lib.utils import real_rand
from logics.skill_logic.skill_buff import zcBuff
import random


def ZCRealSkill(battle, selfPositionId, skillLv, effect, attr_effect=1.0):
    tempAtk = battle.getMembers(selfPositionId)
    healthList = []
    friendList = battle.getCampAllLife(selfPositionId)
    tempList = []
    enemyList = battle.getBackRowAll(selfPositionId)    # 获取后排的敌人

    def buff_fire(battle, positionid):
        tempDfd = battle.getMembers(positionid)
        tempHurt = tempDfd['hp'] * 0.05
        if tempHurt > tempAtk['phsc'] * 0.5:
            tempHurt = tempAtk['phsc'] * 0.5
        tempHurt = battle.realHurt(positionid, tempHurt)
        battle.updateMsg('buff_skill',
                         {'name': 'buff_fire_skill', 'src': positionid, 'dec': positionid, 'hurt': tempHurt})

    buff = zcBuff('buff_fire', buff_fire, 99, 1, skill_tregger_def.KBUFFATTACK, 1002, 8)

    def buff_func2(battle, positionid):
        tempSelf = battle.getMembers(positionid)
        tempSelf['tempSpeed'] += tempSelf['speed'] * 0.2

    buff2 = zcBuff('buff_speed', buff_func2, 3, 99, skill_tregger_def.KBUFFKEEP, 3, 104)

    for target in friendList:
        tempdfd = battle.getMembers(target)
        if tempdfd['tempHp'] > 0:
            health = battle.addHp(target, tempAtk['hp'] * effect)       # 治疗
            healthList.append(health)
            tempList.append(target)

    battle.updateMsg('skill',
                     {'skillid': 955, 'name': 'ace_s5', 'src': selfPositionId, 'desh': tempList, 'health': healthList})

    for i in enemyList:
        battle.addBuff(buff, i)

    for target in friendList:
        friend = battle.getMembers(target)
        if friend['animation'] == 'luffy':
            battle.addBuff(buff2, target)

    return 0