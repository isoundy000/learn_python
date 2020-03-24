#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


import os
import sys
import imp

from lib.utils.debug import print_log
import game_config

from lib.utils import real_rand as realRand

from logics.skill_script import all_skill
from logics.skill_logic.skill_tregger_def import key_to_tregger

KMAXSKILLNUMBER = 5



class zcSkill(object):
    """
    技能分类：
        主动技能（触发后代替普通攻击）
        被动技能
        buff技能
    技能对象
    m_tSkillName:   技能名，（技能脚本名字）
    m_tSkill:       技能脚本列表
    m_tProbability: 技能触发几率列表
    m_tTreggerFlag: 技能触发器列表
    m_tLevel:       技能等级
    """
    def __init__(self):
        """
        初始化对象参数
        """
        self.m_tSkillName = [0] * KMAXSKILLNUMBER
        self.m_tSkill = [0] * KMAXSKILLNUMBER
        self.m_tProbability = [0] * KMAXSKILLNUMBER
        self.m_tTreggerFlag = [0] * KMAXSKILLNUMBER
        self.m_tLevel = [0] * KMAXSKILLNUMBER
        self.m_tEffect = [0] * KMAXSKILLNUMBER
        self.m_tAttrEffect = [0] * KMAXSKILLNUMBER
        self.m_tMaxCdRound = [0] * KMAXSKILLNUMBER
        self.m_tCurtCdRound = [-1] * KMAXSKILLNUMBER
        self.m_tSkillid = [0] * KMAXSKILLNUMBER

    def setProba(self, name, proba):
        """
        强制设置指定技能触发几率
        name:   技能脚本名字
        proba:  要设定的触发几率
        """
        if name in self.m_tSkillName:
            tempIndex = self.m_tSkillName.index(name)
            self.m_tProbability[tempIndex] = proba
        else:
            return None

    def setCurCd(self, name, cd):
        """
        强制设置指定技能cd
        name:   技能脚本名
        cd:     要设定的当前cd
        """
        if name in self.m_tSkillName:
            tempIndex = self.m_tSkillName.index(name)
            self.m_tCurtCdRound[tempIndex] = cd
        else:
            return None

    
def realProbability(skillObject):
    """
    真实几率
    """
    # print '====================='
    # print '-------------ghou log-----------realProbability', skillObject.m_tSkillName
    # print '-------------ghou log-----------realProbability', skillObject.m_tProbability
    # print '-------------ghou log-----------realProbability', skillObject.m_tTriggerFlag
    # print '====================='
    realProb = 1
    for tregger in range(1, 7):
        treggerCount = skillObject.m_tTreggerFlag.count(tregger)
        if treggerCount <= 0:
            continue
        realProb = 1
        tempStart = 0
        tempAllP = 0
        tempList = range(treggerCount)
        for i in tempList:
            tempIndex = skillObject.m_tTreggerFlag.index(tregger, tempStart)
            tempStart = tempIndex + 1
            tempSkillPro = max(min(skillObject.m_tProbability[tempIndex], 100), 0)
            realProb *= (100 - tempSkillPro)
            # print '------------',realProb
            tempAllP += tempSkillPro
        realProb /= 100 ** (treggerCount - 1)
        tempStart = 0
        tempAllP = tempAllP or 1    # tempAllP will be zero
        for j in tempList:
            tempIndex = skillObject.m_tTreggerFlag.index(tregger, tempStart)
            tempStart = tempIndex + 1
            tempSkillPro = max(min(skillObject.m_tProbability[tempIndex], 100), 0)
            skillObject.m_tProbability[tempIndex] = (100 - realProb) * tempSkillPro / tempAllP

    return realProb


def realProbabilityList(mList):
    """
    计算真实触发几率
    """
    probNom = 100.0
    probAll = 0
    for prob in mList:
        probNom = (probNom * (100 - prob) / 100.0)
        probAll = probAll + prob
    probReal = 100 - probNom
    templist = []
    for prob in mList:
        templist.append(prob * probReal / 100.0)
    return templist


def skillFactory(skillList):
    """
    skillList:  技能名字列表
    [['技能名',技能等级]，
     ['技能名2',技能等级]]
    """
    tempSkill = zcSkill()
    i = 0
    g = globals()
    skill_config = game_config.skill_detail

    for skillname in skillList:
        s_name = skillname[0]
        s_id = skillname[0]
        try:
            s_name = int(s_name)
            sprite_py = skill_config[s_name]['sprite_py'].rstrip('.py')
            s_name = sprite_py
            if cmp(sprite_py, "") == 0:
                continue
            skill_module = all_skill[sprite_py]
        except ValueError:
            skill_module = all_skill[s_name]
        skill_level = skillname[1]

        # print_log(getattr(skill_module,'ZCRealSkill',),'============================++++++++++++++++++++++++++++++++')
        tempSkill.m_tSkill[i] = getattr(skill_module, 'ZCRealSkill')   # 获得触发函数

        # tempSkill.m_tProbability[i] = getattr(skill_module, 'ZCRealProbability')(skill_level)    # 获得触发几率
        # tempSkill.m_tTriggerFlag[i] = getattr(skill_module, 'KREALTREGGER')  # 获得触发器
        tempSkillCf = skill_config[s_id]
        tempSkill.m_tProbability[i] = tempSkillCf['rate']
        tempSkill.m_tTreggerFlag[i] = key_to_tregger[tempSkillCf['skill_type']]
        tempSkill.m_tMaxCdRound[i] = tempSkillCf.get('cd', 0)                   # 技能cd回合数
        tempSkill.m_tCurtCdRound[i] = tempSkillCf.get('pre_cd', 0) - 1          # 技能pre_cd回合数
        
        tempSkill.m_tLevel[i] = skill_level
        tempSkill.m_tSkillName[i] = s_name
        tempSkill.m_tEffect[i] = (tempSkillCf['effect'] + tempSkillCf['effect_lvchange'] * skill_level) / 100.0
        tempSkill.m_tAttrEffect[i] = tempSkillCf.get('attr_effect', 100) / 100.0
        tempSkill.m_tSkillid[i] = s_id
        # print '------------------ghou log------------------skillFactory skill name', s_name, skill_level
        i += 1
    # 每个技能单独计算概率 2014.04.17 songming
    # realProbability(tempSkill)
    return tempSkill


def skillTregger(skillObject, treggerFlag, battle, positionid):
    """
    技能触发器
    :param skillObject: 技能对象
    :param treggerFlag: 触发器标记
    :param battle: 战场上下文
    :param positionid: 触发者当前的位置信息
    :return:
        返回
        1：无技能触发，或触发的技能不限制其他技能的触发
    """
    # print '-----------------ghou log------------------skillTregger', treggerFlag

    if skillObject == 0:
        # print '================ghou log===============skill object is 0'
        return 1

    randCount = skillObject.m_tTreggerFlag.count(treggerFlag)
    if randCount <= 0:
        # print '==============ghou log=============skill not have the tregger', treggerFlag
        return 1

    tempStart = 0

    # tempRand = realRand.myRand()
    # print '----------ghou log-----------', skillObject.m_tSkillName
    # print '----------ghou log-----------', skillObject.m_tProbability
    # print '----------ghou log-----------', skillObject.m_tTreggerFlag
    # print '======================================================='
    # print '=========================================rand number', tempRand
    realProb = []
    realIndex = []
    for i in xrange(randCount):
        tempIndex = skillObject.m_tTreggerFlag.index(treggerFlag, tempStart)
        tempStart = tempIndex + 1
        if skillObject.m_tCurtCdRound[tempIndex] <= 0:
            realProb.append(skillObject.m_tProbability[tempIndex])
            realIndex.append(tempIndex)

    if len(realIndex) <= 0:
        return 1

    tempRealProb = realProbabilityList(realProb)
    tempRand = realRand.myRand()
    for i, v in enumerate(realIndex):
        if tempRand > realProb[i]:
            tempRand -= tempRealProb[i]
        else:
            try:
                tempValue = skillObject.m_tSkill[v](battle, positionid, skillObject.m_tLevel[v], skillObject.m_tEffect[v], attr_effect=skillObject.m_tAttrEffect[v])
            except:
                tempValue = skillObject.m_tSkill[v](battle, positionid, skillObject.m_tLevel[v], skillObject.m_tEffect[v])
            skillObject.m_tCurtCdRound[v] = skillObject.m_tMaxCdRound[v]
            return tempValue
    return 1

    # for i in range(randCount):
    #     # if skillObject.m_tTreggerFlag[i] != treggerFlag:
    #     #     continue
    #     # i = 0
    #     # tempRand = 100
    #     # while (i < randCount):
    #     #     temp = realRand.myRand()
    #     #     if temp < tempRand:
    #     #         tempRand = temp
    #
    #     # 每个技能单独计算概率 2014.04.17 songming
    #     tempRand = realRand.myRand()
    #     tempIndex = skillObject.m_tTreggerFlag.index(treggerFlag, tempStart)
    #     tempStart = tempIndex + 1
    #     # 技能 cd 回合数 判断 2014.03.27 songming
    #     if skillObject.m_tCurtCdRound[tempIndex] == -1 or \
    #         battle.m_nRoundNum - skillObject.m_tCurtCdRound[tempIndex] > skillObject.m_tMaxCdRound[tempIndex]:
    #         skillObject.m_tCurtCdRound[tempIndex] = battle.m_nRoundNum
    #     else:
    #         continue
    #     if tempRand > skillObject.m_tProbability[tempIndex]:
    #         tempRand -= skillObject.m_tProbability[tempIndex]
    #         continue
    #     else:
    #         # try:
    #         #     # print '---------------ghou log----------------skillTregger is start', skillObject.m_tSkillName[tempIndex]
    #         tempValue = skillObject.m_tSkill[tempIndex](battle, positionid, skillObject.m_tLevel[tempIndex], skillObject.m_tEffect[tempIndex])
    #         # battle.HistoryChangeMsg()   # changed by zhangchen on 2014.1.24
    #         return tempValue
    #         # except Exception, e:
    #         #     from lib.utils.debug import trackback
    #         #     trackback()
    #         #     # print 'sl, skill, 166, ', skillObject.m_tSkillName[tempIndex], e
    # return 1


def cardSkillCdChange(skillObject):
    """
    更新卡牌技能当前cd
    """
    if skillObject == 0:
        return
    for i, v in enumerate(skillObject.m_tCurtCdRound):
        if v > 0:
            skillObject.m_tCurtCdRound[i] -= 1


def battle_skill_tregger(battle, battle_skill_scripts):
    """ 战斗前触发

    :param battle:
    :param battle_skill_scripts:
    :return:
    """
    if not battle_skill_scripts:
        return False
    attack_life_list = battle.getCampAllLife()
    if not attack_life_list:
        return False
    attack_life = attack_life_list[0]
    is_tregger = False
    for script in battle_skill_scripts:
        script_name = script.rstrip('.py')
        script_module = all_skill.get(script_name)
        if script_module:
            script_func = getattr(script_module, 'ZCRealSkill', None)
            if script_func:
                script_func(battle, attack_life, 1, 1)
                is_tregger = True

    return is_tregger