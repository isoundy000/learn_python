#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from lib.db import ModelBase
import copy


class Skill(ModelBase):
    """# Skill: 记录技能等级"""

    def __init__(self, uid=None):
        self.uid = uid
        self._attrs = {}
        self._base = {
            'skill': {                  # 用户已经学会的主角技能，对应等级

            },
            'super_skill': {            # 用户已经学会的主角技能，对应等级

            },
            'skill_1': 0,               # 用户装载的第一个技能，0表示没有
            'skill_2': 0,
            'skill_3': 0,
            'is_open': False,           # 是否开启额外的升级线路
        }
        self._attrs.update(self._base)
        super(Skill, self).__init__(self.uid)

    def add_skill(self, skill):
        """# add_skill: 新加一个技能
        args:
            skill:    ---    arg
        returns:
            0    ---
        """
        self.skill[skill] = 1

    def get_skill_copy(self):
        """
        得到技能数据副本
        """
        r = {}
        for k in self._base.iterkeys():
            r[k] = getattr(self, k)
        return copy.deepcopy(r)

    def level_up(self, skill, point_amount):
        """# level_up: 某一个技能升级
        args:
            skill:    ---    arg
        returns:
            0    ---
        """
        if skill in self.skill:
            self.skill[skill] += point_amount
        else:
            self.skill[skill] = point_amount

    def super_level_up(self, skill, point_amount):
        """# level_up: 某一个技能升级
        args:
            skill:    ---    arg
        returns:
            0    ---
        """
        self.super_skill[skill] = point_amount