# -*- coding=utf-8 -*-
"""
Created by lichen on 17/3/16.
"""

import json

from poker.entity.dao import weakdata
from newfish.entity.config import FISH_GAMEID


#===========================================================================================
def setDayFishData(userId, key, value):
    """
    设置每日数据key、value
    """
    data = getDayFishDataAll(userId, FISH_GAMEID)
    data[key] = value
    setDayFishDataAll(userId, FISH_GAMEID, data)
    return data[key]


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


def getDayFishData(userId, key, defaultVal=None):
    """
    根据key获取每日数据中的value
    """
    data = getDayFishDataAll(userId, FISH_GAMEID)
    value = data.get(key)
    if value is not None:
        try:
            value = json.loads(value)
        except:
            value = data.get(key)
        finally:
            return value
    return defaultVal


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


#===========================================================================================
def setWeekFishData(userId, key, value):
    """
    设置每周数据key、value 设置一个数据
    """
    data = getWeekFishDataAll(userId, FISH_GAMEID)
    data[key] = value
    setWeekFishDataAll(userId, FISH_GAMEID, data)
    return data[key]


def incrWeekFishData(userId, key, value):
    """
    对每周数据中的值加上增量
    """
    assert (isinstance(value, int))
    data = getWeekFishDataAll(userId, FISH_GAMEID)
    if key in data:
        data[key] += value
    else:
        data[key] = value
    setWeekFishDataAll(userId, FISH_GAMEID, data)
    return data[key]


def getWeekFishData(userId, key, defaultVal=None):
    """
    根据key获取每周数据中的value
    """
    data = getWeekFishDataAll(userId, FISH_GAMEID)
    return data.get(key, defaultVal)


def getWeekFishDataAll(userId, gameId):
    """
    获取每周数据（每个自然周的周一0点数据会被清除）
    """
    return weakdata.getWeakData(userId, gameId, weakdata.CYCLE_TYPE_WEEK, "fish")


def setWeekFishDataAll(userId, gameId, data):
    """
    设置每周数据（每个自然周的周一0点数据会被清除）设置一堆数据
    """
    return weakdata.setWeakData(userId, gameId, weakdata.CYCLE_TYPE_WEEK, "fish", data)


#===========================================================================================
def setMonthFishData(userId, key, value):
    """
    设置每月数据key、value
    """
    data = getMonthFishDataAll(userId, FISH_GAMEID)
    data[key] = value
    setMonthFishDataAll(userId, FISH_GAMEID, data)
    return data[key]


def incrMonthFishData(userId, key, value):
    """
    对每月数据中的值加上增量
    """
    assert (isinstance(value, int))
    data = getMonthFishDataAll(userId, FISH_GAMEID)
    if key in data:
        data[key] += value
    else:
        data[key] = value
    setMonthFishDataAll(userId, FISH_GAMEID, data)
    return data[key]


def getMonthFishData(userId, key, defaultVal=None):
    """
    根据key获取每月数据中的value
    """
    data = getMonthFishDataAll(userId, FISH_GAMEID)
    return data.get(key, defaultVal)


def getMonthFishDataAll(userId, gameId):
    """
    获取每月数据（每个自然月的首日0点数据会被清除）
    """
    return weakdata.getWeakData(userId, gameId, weakdata.CYCLE_TYPE_MONTH, "fish")


def setMonthFishDataAll(userId, gameId, data):
    """
    设置每月数据（每个自然月的首日0点数据会被清除）
    """
    return weakdata.setWeakData(userId, gameId, weakdata.CYCLE_TYPE_MONTH, "fish", data)


#===========================================================================================
def getDayRobberyData(userId, key, defaultVal=None):
    """
    根据key获取每日数据中的value（招财模式专用）
    """
    data = getDayRobberyDataAll(userId, FISH_GAMEID)
    return data.get(key, defaultVal)


def getDayRobberyDataAll(userId, gameId):
    """
    获取每日数据（招财模式专用）
    """
    return weakdata.getWeakData(userId, gameId, weakdata.CYCLE_TYPE_DAY, "robbery")


def setDayRobberyDataAll(userId, gameId, data):
    """
    设置每日数据（招财模式专用）
    """
    return weakdata.setWeakData(userId, gameId, weakdata.CYCLE_TYPE_DAY, "robbery", data)


def setDayRobberyData(userId, key, value):
    """
    设置每日数据key、value（招财模式专用）
    """
    data = getDayRobberyDataAll(userId, FISH_GAMEID)
    data[key] = value
    setDayRobberyDataAll(userId, FISH_GAMEID, data)
    return data[key]


def incrDayRobberyData(userId, key, value):
    """
    对每日数据中的值加上增量（招财模式专用）
    """
    assert (isinstance(value, int))
    data = getDayRobberyDataAll(userId, FISH_GAMEID)
    if key in data:
        data[key] += value
    else:
        data[key] = value
    setDayRobberyDataAll(userId, FISH_GAMEID, data)
    return data[key]


#===========================================================================================
def getDayPoseidonData(userId, key, defaultVal=None):
    """
    根据key获取每日数据中的value（海皇来袭专用）
    """
    data = getDayPoseidonDataAll(userId, FISH_GAMEID)
    return data.get(key, defaultVal)


def getDayPoseidonDataAll(userId, gameId):
    """
    获取每日数据（海皇来袭专用）
    """
    return weakdata.getWeakData(userId, gameId, weakdata.CYCLE_TYPE_DAY, "poseidon")


def setDayPoseidonDataAll(userId, gameId, data):
    """
    设置每日数据（海皇来袭专用）
    """
    return weakdata.setWeakData(userId, gameId, weakdata.CYCLE_TYPE_DAY, "poseidon", data)


def setDayPoseidonData(userId, key, value):
    """
    设置每日数据key、value（海皇来袭专用）
    """
    data = getDayPoseidonDataAll(userId, FISH_GAMEID)
    data[key] = value
    setDayPoseidonDataAll(userId, FISH_GAMEID, data)
    return data[key]


def incrDayPoseidonData(userId, key, value):
    """
    对每日数据中的值加上增量（海皇来袭专用）
    """
    assert (isinstance(value, int))
    data = getDayPoseidonDataAll(userId, FISH_GAMEID)
    if key in data:
        data[key] += value
    else:
        data[key] = value
    setDayPoseidonDataAll(userId, FISH_GAMEID, data)
    return data[key]
#===========================================================================================