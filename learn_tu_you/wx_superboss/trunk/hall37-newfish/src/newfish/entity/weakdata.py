#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6
import json

from poker.entity.dao import weakdata
from newfish.entity.config import FISH_GAMEID



def getDayFishDataAll(userId, gameId):
    """
    获取每日数据（每个自然日的0点数据会被清除）
    """
    return weakdata.getWeakData(userId, gameId, weakdata.CYCLE_TYPE_DAY, "fish")


def setDayFishDataAll(userId, gameId, data):
    """
    设置每日数据（每个自然日的0点数据会被清除）
    """
    return weakdata.setWeakData(userId, gameId, weakdata.CYCLE_TYPE_DAY, "fish", data)


def incrDayFishData(userId, key, value):
    """
    对每日数据中的值加上增量
    """
    assert (isinstance(value, int))
    data = getDayFishDataAll(userId, FISH_GAMEID)
    if key in data:
        data[key] += value
    else:
        data[key] = value
    setDayFishDataAll(userId, FISH_GAMEID, data)
    return data[key]