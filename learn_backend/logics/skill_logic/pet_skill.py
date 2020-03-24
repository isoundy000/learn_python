#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from logics.skill_script import all_skill
from logics.skill_logic.skill_tregger_def import key_to_tregger


KHeroSkillMaxCount = 2

KHeroSkillInitFunc = 'ZCInit'
KHeroSkillSubAngerFunc = 'ZCWhenSubAnger'


class zcPetSkill(object):
    """ 宠物战场技能包裹

    m_tName:    宠物技能名列表
    m_tLevel:   宠物技能等级列表
    m_tMaxCd:   宠物Cd时间
    m_tCurtCd:  宠物当前Cd
    m_tTreggerFlag: 技能触发器列表
    m_tEffect:
    m_tAttrEffect:
    m_tSkill: 宠物技能列表
    """
    def __init__(self):
        self.m_tName = [0] * KHeroSkillMaxCount
        self.m_tLevel = [0] * KHeroSkillMaxCount        # 宠物技能等级列表
        self.m_tMaxCd = [0] * KHeroSkillMaxCount        # 宠物Cd时间
        self.m_tCurtCd = [0] * KHeroSkillMaxCount       # 宠物当前Cd
        self.m_tTreggerFlag = [0] * KHeroSkillMaxCount  # 技能触发器列表
        self.m_tEffect = [0] * KHeroSkillMaxCount
        self.m_tAttrEffect = [0] * KHeroSkillMaxCount
        self.m_tSkill = [0] * KHeroSkillMaxCount


def petSkillFactory(petList):
    """ 宠物技能工厂

    :param petList: 技能列表 [[技能脚本名字, 等级, cd时间, 第几回合放, 技能类型]]
    :return:
    """
    if petList is None or len(petList) <= 0:
        return 0

    tempSkill = zcPetSkill()

    for i, skill in enumerate(petList):
        skill_model = all_skill[skill[0]]
        tempSkill.m_tName[i] = skill[0]
        tempSkill.m_tLevel[i] = skill[1]
        tempSkill.m_tMaxCd[i] = skill[2]
        tempSkill.m_tCurtCd[i] = skill[3]
        tempSkill.m_tTreggerFlag[i] = key_to_tregger[skill[4]]
        tempSkill.m_tEffect[i] = (skill[5] + skill[6] * skill[1]) / 100.0
        tempSkill.m_tAttrEffect[i] = skill[7] / 100.0
        # 检查是否有此脚本
        tempSkill.m_tSkill[i] = getattr(skill_model, 'ZCRealSkill', None)
    return tempSkill


def petTregger(skillObject, treggerFlag, battle, sort):
    """ 宠物技能触发器

    :param skillObject: 技能包
    :param treggerFlag:
    :param battle: 战场
    :param sort: 0攻击方  1防守方
    :return:
    """
    if skillObject == 0:
        return 0

    for i in xrange(KHeroSkillMaxCount):
        if skillObject.m_tSkill[i] != 0 and \
                        skillObject.m_tTreggerFlag[i] == treggerFlag and \
                        skillObject.m_tCurtCd[i] == 0:
            skillObject.m_tCurtCd[i] = skillObject.m_tMaxCd[i]
            return skillObject.m_tSkill[i](battle, sort, skillObject.m_tLevel[i],
                                           skillObject.m_tEffect[i], skillObject.m_tAttrEffect[i])

    return 0


def petSkillCdChange(skillObject):
    """ 记录一次CD

    :param skillObject:
    :return:
    """
    if skillObject != 0:
        for i in xrange(KHeroSkillMaxCount):
            if skillObject.m_tSkill[i] != 0:
                if skillObject.m_tCurtCd[i] < 0:
                    skillObject.m_tCurtCd[i] = 0
                else:
                    skillObject.m_tCurtCd[i] -= 1