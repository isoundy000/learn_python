#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6

import json
from copy import deepcopy

import freetime.util.log as ftlog
import poker.util.timestamp as pktimestamp
from poker.util import strutil
from poker.entity.dao import daobase, gamedata
from hall.entity import hallitem, datachangenotify
from newfish.entity import config, module_tip, util, mail_system
from newfish.entity.config import FISH_GAMEID, PEARL_KINDID, CHIP_KINDID
from newfish.entity.redis_keys import UserData, GameData


# 5101: [0, 0, 0, 0, 0]
# skillMode 0:经典 1:千炮
DEFAULT_VALUE = [0, 0, 0, 0, 0]
MAX_STAR_LEVEL = 5          # 最大技能星级
MAX_ORIGINAL_LEVEL = 25     # 最大技能等级
MAX_INSTALL_NUM = 3         # 最大装备数（经典）
MAX_INSTALL_NUM_M = 2       # 最大装备数（千炮）
INDEX_STAR_LEVEL = 0        # 第0位:技能星级
INDEX_ORIGINAL_LEVEL = 1    # 第1位:技能原始等级
INDEX_CURRENT_LEVEL = 2     # 第2位:技能当前等级
INDEX_STATE = 3             # 第3位:技能状态&顺序（经典）
INDEX_STATE_M = 4           # 第4位:技能状态&顺序（千炮）
AUXILIARY_SKILL_NUM = 2     # 辅助技能个数


def _getAllSkills(userId):
    """
    获得所有技能数据
    """
    assert isinstance(userId, int) and userId > 0
    value = daobase.executeUserCmd(userId, "HGETALL", _getUserSkillKey(userId))     # [1, 2, 3, 4, 5, 6]
    if value:
        skillIds = value[0::2]      # [1, 3, 5]
        infos = [strutil.loads(info, False, True) for info in value[1::2] if info]
        skillDict = dict(zip(skillIds, infos))
        allSkillIdsConf = config.getAllSkillId()        # 获取所有技能ID
        popSkillIds = [skillId for skillId in skillIds if str(skillId) not in allSkillIdsConf]
        for _skillId in popSkillIds:
            del skillDict[_skillId]                     # 删掉存档中与配置中不存在的skillId
        return skillDict
    return {}


def getInstalledSkill(userId, skillMode):
    """
    获得已装备技能数据
    """
    skills = {}
    allSkills = _getAllSkills(userId)
    if allSkills:
        for skillId, info in allSkills.iteritems():
            if config.getSkillStarConf(skillId, info[INDEX_STAR_LEVEL], skillMode):
                state = info[INDEX_STATE] if skillMode == config.CLASSIC_MODE else info[INDEX_STATE_M]
                if state:
                    skills[int(skillId)] = [info[INDEX_STAR_LEVEL], info[INDEX_CURRENT_LEVEL]]
    return skills


def _getUserSkillKey(userId):
    """
    技能数据存取key
    """
    return UserData.skill % (FISH_GAMEID, userId)