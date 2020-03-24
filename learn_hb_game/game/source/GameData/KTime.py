#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


from Source.DataBase.Table.t_ktime import t_ktime
import GameData
from Source.GameOperation.Time.ConvertToUTCSeconds import *


def Init():
    if not GameData.ktime:
        GameData.ktime = t_ktime.LoadAllToDict()