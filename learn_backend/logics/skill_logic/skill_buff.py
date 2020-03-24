#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


class zcBuff(object):
    """
    buff挂载节点
    """
    def __init__(self, name, func, roundcount, effectcount, treggers, flag, team):
        """
        初始化
        m_name:     buff名字
        m_func:     buff效果函数
        m_record:   记录剩余循环数
        m_effect:   效果释放次数
        m_tregger:  buff触发效果触发器
        m_flag:     buff类型标记，同样类型的buff不能叠加
        m_term:     buff分类
        """
        self.m_name = name
        self.m_func = func
        self.m_record = roundcount
        self.m_effect = effectcount
        self.m_tregger = treggers
        self.m_flag = flag
        self.m_team = team