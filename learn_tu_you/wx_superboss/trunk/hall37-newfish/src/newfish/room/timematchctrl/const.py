#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/10

from newfish.entity import config, util


class MatchType(object):
    """比赛类型"""
    # 人满开赛
    USER_COUNT = 1
    # 定时赛
    TIMING = 2
    # 定时积分赛
    TIME_POINT = 3
    # 合法的类型
    VALID_TYPES = (USER_COUNT, TIMING, TIME_POINT)

    @classmethod
    def isValid(cls, value):
        return value in cls.VALID_TYPES


class FeeType(object):

    TYPE_NO_RETURN = 0
    TYPE_RETURN = 1
    VALID_TYPES = (TYPE_NO_RETURN, TYPE_RETURN)

    @classmethod
    def isValid(cls, value):
        return value in cls.VALID_TYPES


class SeatQueuingType(object):

    # 随机
    RANDOM = 1
    # 蛇形
    SNAKE = 2
    # 种子
    SEED = 3
    # 报名时间
    SIGNIN_TIME = 4
    # 幸运值
    LUCKY = 5

    VALID_TYPES = (RANDOM, SNAKE, SEED, SIGNIN_TIME, LUCKY)

    @classmethod
    def isValid(cls, value):
        return value in cls.VALID_TYPES



class GroupingType(object):
    """分组类型"""
    TYPE_NO_GROUP = 0
    TYPE_GROUP_COUNT = 1
    TYPE_USER_COUNT = 2
    VALID_TYPES = (TYPE_NO_GROUP, TYPE_GROUP_COUNT, TYPE_USER_COUNT)

    @classmethod
    def isValid(cls, value):
        return value in cls.VALID_TYPES