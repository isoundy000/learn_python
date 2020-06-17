#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/10

from poker.entity.biz.exceptions import TYBizException


class MatchException(TYBizException):
    """比赛的异常 errorCode"""
    def __init__(self, ec, message):
        super(MatchException, self).__init__(ec, message)


class MatchConfException(MatchException):

    def __init__(self, message=u"系统错误"):
        super(MatchConfException, self).__init__(1, message)


class BadStateException(MatchException):
    """状态错误"""
    def __init__(self, message=u"状态错误"):
        super(BadStateException, self).__init__(2, message)


class SigninException(MatchException):
    """比赛报名类"""
    def __init__(self, ec=5, message=u"报名失败了"):
        super(SigninException, self).__init__(ec, message)
