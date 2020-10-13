# -*- coding:utf-8 -*-
"""
Created on 2016年7月12日

@author: zhaojiangang
"""
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
    """费用类型"""
    TYPE_NO_RETURN = 0
    TYPE_RETURN = 1
    VALID_TYPES = (TYPE_NO_RETURN, TYPE_RETURN)

    @classmethod
    def isValid(cls, value):
        return value in cls.VALID_TYPES


class MatchFinishReason(object):
    """比赛分组完成原因"""
    FINISH = 0
    USER_WIN = 1
    USER_LOSER = 2
    USER_NOT_ENOUGH = 3
    RESOURCE_NOT_ENOUGH = 4
    USER_LEAVE = 5
    OVERTIME = 6
    GIVEUP = 7

    @classmethod
    def toString(cls, userId, reason):
        lang = util.getLanguage(userId)
        if reason == cls.USER_NOT_ENOUGH:
            # return u"由于参赛人数不足，比赛无法开启，报名费已返还，请期待下一场比赛吧"
            return config.getMultiLangTextConf("ID_TAKE_MATCH_ERR_USER_NOT_ENOUGH", lang=lang)
        elif reason == cls.RESOURCE_NOT_ENOUGH:
            # return u"服务器开小差了,本场比赛临时被取消，报名费已返还，请期待下一场比赛吧"
            return config.getMultiLangTextConf("ID_TAKE_MATCH_ERR_RES_NOT_ENOUGH", lang=lang)
        elif reason == cls.USER_LEAVE:
            # return u"由于您未在开赛前进入赛场等待，报名被取消了，报名费已自动退还，请关注下一场比赛吧"
            return config.getMultiLangTextConf("ID_TAKE_MATCH_ERR_USER_LEAVE", lang=lang)
        elif reason == cls.OVERTIME:
            # return u"比赛超时错误"
            return config.getMultiLangTextConf("ID_TAKE_MATCH_ERR_OVERTIME", lang=lang)
        return u""


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


class WaitReason(object):
    """等待原因"""
    UNKNOWN = 0
    WAIT = 1
    BYE = 2
    RISE = 3


class ScoreCalcType(object):
    PING_FANG_GEN = 1
    BAI_FEN_BI = 2
    KAI_FANG_FANG_DA = 3


class StageType(object):
    # ASS
    ASS = 1
    # 定局
    DIEOUT = 2
    
    VALID_TYPES = (ASS, DIEOUT)
    
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