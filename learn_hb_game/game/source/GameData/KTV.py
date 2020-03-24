#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from Source.DataBase.Table.t_ktv import t_ktv
import GameData


def Init():
    if not GameData.ktv:                        # 环境变量
        GameData.ktv = t_ktv.LoadAllToDict()