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
    """比赛配置异常"""
    def __init__(self, message=u"系统错误"):
        super(MatchConfException, self).__init__(1, message)


class BadStateException(MatchException):
    """状态错误"""
    def __init__(self, message=u"状态错误"):
        super(BadStateException, self).__init__(2, message)


class MatchStoppedException(MatchException):
    def __init__(self, message=u"比赛已停止"):
        super(MatchStoppedException, self).__init__(3, message)


class AlreadyInMatchException(MatchException):
    def __init__(self, message=u"比赛还在进行中"):
        super(AlreadyInMatchException, self).__init__(4, message)


class SigninException(MatchException):
    """比赛报名类"""
    def __init__(self, ec=5, message=u"报名失败了"):
        super(SigninException, self).__init__(ec, message)


class SigninNotStartException(SigninException):
    def __init__(self, message=u"现在还不能报名"):
        super(SigninNotStartException, self).__init__(6, message)


class SigninStoppedException(SigninException):
    def __init__(self, message=u"报名已经结束了，请参加下一场比赛吧"):
        super(SigninStoppedException, self).__init__(7, message)


class SigninFullException(SigninException):
    def __init__(self, message=u"当前报名人数已满，请等待下一场比赛吧"):
        super(SigninFullException, self).__init__(8, message)


class AlreadySigninException(SigninException):
    def __init__(self, message=u"您已经报名了该比赛，请不要重复报名"):
        super(AlreadySigninException, self).__init__(9, message)


class AlreadySigninOtherException(SigninException):
    def __init__(self, message=u"您已经报名其他场次的比赛，更改比赛需要先取消之前的报名"):
        super(AlreadySigninOtherException, self).__init__(10, message)


class SigninFeeNotEnoughException(SigninException):
    def __init__(self, fee, message=u"您的海星不足，无法报名，快去渔场收集一些吧"):
        super(SigninFeeNotEnoughException, self).__init__(11, message)
        self.fee = fee


class SigninConditionNotEnoughException(SigninException):
    def __init__(self, message=u"想参加比赛需要先去渔场完成新手任务哟"):
        super(SigninConditionNotEnoughException, self).__init__(12, message)


class SigninVersionDisableException(SigninException):
    def __init__(self, message=u"您当前游戏版本过低，请更新后再试！"):
        super(SigninVersionDisableException, self).__init__(13, message)


class NotSigninException(SigninException):
    def __init__(self, message=u"您还没有报名，不能进入渔场"):
        super(NotSigninException, self).__init__(14, message)


class RunOutSigninChanceException(SigninException):
    def __init__(self, message=u"报名次数已耗尽，请下场比赛再来吧"):
        super(RunOutSigninChanceException, self).__init__(15, message)


class MaintenanceException(SigninException):
    def __init__(self, message=u"游戏维护中，请稍后再试！给您带来不便，敬请谅解！"):
        super(MaintenanceException, self).__init__(16, message)
