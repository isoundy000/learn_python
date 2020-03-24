#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import time
from logics import skill_script
from logics.skill_script import all_skill

KHeroSkillMaxCount = 3

KHeroSkillInitFunc = 'ZCInit'
KHeroSkillSubAngerFunc = 'ZCWhenSubAnger'


class zcHeroSkill(object):
    """
    英雄战场技能包裹
    m_tSkill:   英雄技能列表
    m_tLevel:   英雄技能等级列表
    m_tMaxCd:   英雄Cd时间
    m_tCurtCd:  英雄当前Cd
    m_tSubAngerFunc: 英雄技能释放结束后调用
    """
    def __init__(self):
        self.m_tSkill = [0] * KHeroSkillMaxCount
        self.m_tInitFunc = [0] * KHeroSkillMaxCount
        self.m_tSubAngerFunc = [0] * KHeroSkillMaxCount
        self.m_tLevel = [0] * KHeroSkillMaxCount
        self.m_tMaxCd = [0] * KHeroSkillMaxCount
        self.m_tCurtCd = [0] * KHeroSkillMaxCount
        self.m_tName = [0] * KHeroSkillMaxCount

    def subCurtCd(self, name, subCd):
        """
        减少指定名字的技能的Cd时间
        :param name:
        :param subCd:
        :return:
        """
        if name in self.m_tName:
            tempIndex = self.m_tName.index(name)
            self.m_tCurtCd[tempIndex] -= min(self.m_tCurtCd[tempIndex], subCd)


def heroSkillFactory(heroList):
    """
    英雄技能工厂
    heroList:       技能列表
    ［［名字, 等级, cd时间］,
      ［名字, 等级, cd时间］］
    """
    # print '------ghou log hero skill----', heroList
    if heroList is None or len(heroList) <= 0:
        return 0
    tempSkill = zcHeroSkill()
    i = 0
    for skill in heroList:
        # print('---------ghou log hero skill factory--------', skill)
        skill_model = all_skill[skill[0]]
        tempSkill.m_tName[i] = skill[0]
        tempSkill.m_tLevel[i] = skill[1]
        tempSkill.m_tMaxCd[i] = skill[2]
        tempSkill.m_tCurtCd[i] = skill[3]
        # 检查是否有此脚本
        tempSkill.m_tSkill[i] = getattr(skill_model, 'ZCRealSkill')
        temp_func = getattr(skill_model, KHeroSkillInitFunc, None)
        if callable(temp_func):
            tempSkill.m_tInitFunc[i] = temp_func
        temp_func = getattr(skill_model, KHeroSkillSubAngerFunc, None)
        if callable(temp_func):
            tempSkill.m_tSubAngerFunc[i] = temp_func
        i += 1
    return tempSkill


def heroSkillInit(skillObject, battle, positionid):
    """
    英雄技能上场装载函数调用
    """
    for i in range(KHeroSkillMaxCount):
        if skillObject.m_tInitFunc[i] != 0:
            skillObject.m_tInitFunc[i](battle, positionid, skillObject.m_tLevel[i])


def heroSkillEnd(skillObject, battle, positionid):
    """
    英雄技能释放结束后调用
    """
    for i in range(KHeroSkillMaxCount):
        if skillObject.m_tSubAngerFunc[i] != 0:
            skillObject.m_tSubAngerFunc[i](battle, positionid, skillObject.m_tLevel[i])


def heroTregger(skillObject, battle, positionid):
    """
    英雄技能触发器
    skillObject: 技能包
    battle:      战场
    positionid:  位置id
        1:攻方
        2:守方
    :return:
    """
    # tempCurtTime = int(time.time())

    for i in range(KHeroSkillMaxCount):
        if skillObject.m_tSkill[i] != 0:
            if skillObject.m_tCurtCd[i] == 0:
                skillObject.m_tCurtCd[i] = skillObject.m_tMaxCd[i]
                return True, skillObject.m_tSkill[i](battle, positionid, skillObject.m_tLevel[i])

    return False, 0


def heroChangedCd(skillObject):
    """
    记录一次CD
    """
    if skillObject == 0:
        return
    for i in xrange(KHeroSkillMaxCount):
        if skillObject.m_tSkill[i] != 0:
            if skillObject.m_tCurtCd[i] < 0:
                skillObject.m_tCurtCd[i] = 0
            else:
                skillObject.m_tCurtCd[i] -= 1