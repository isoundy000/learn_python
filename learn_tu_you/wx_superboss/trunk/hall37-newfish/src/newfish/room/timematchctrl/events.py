#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/9/8


from poker.entity.events.tyevent import TYEvent


class MatchStartSigninEvent(TYEvent):
    """比赛开始报名事件"""
    def __init__(self, gameId, instId):
        super(MatchStartSigninEvent, self).__init__()
        self.gameId = gameId
        self.instId = instId


class MatchCancelEvent(TYEvent):
    """比赛取消事件"""
    def __init__(self, gameId, instId, reason):
        super(MatchCancelEvent, self).__init__()
        self.gameId = gameId
        self.instId = instId
        self.reason = reason


class MatchingEvent(TYEvent):
    """比赛事件"""
    def __init__(self, gameId, matchId, instId, matchingId):
        super(MatchingEvent, self).__init__()
        self.gameId = gameId
        self.matchId = matchId
        self.instId = instId
        self.matchingId = matchingId


class MatchingStartEvent(MatchingEvent):
    """比赛开始事件"""
    def __init__(self, gameId, matchId, instId, matchingId):
        super(MatchingStartEvent, self).__init__(gameId, matchId, instId, matchingId)


class MatchingStageStartEvent(MatchingEvent):
    """比赛阶段开始事件"""
    def __init__(self, gameId, matchId, instId, matchingId, stageIndex):
        super(MatchingStageStartEvent, self).__init__(gameId, matchId, instId, matchingId)
        self.stageIndex = stageIndex


class MatchingStageFinishEvent(MatchingEvent):
    """比赛阶段完成事件"""
    def __init__(self, gameId, matchId, instId, matchingId, stageIndex):
        super(MatchingStageFinishEvent, self).__init__(gameId, matchId, instId, matchingId)
        self.stageIndex = stageIndex


class MatchingFinishEvent(MatchingEvent):
    """比赛完成事件"""
    def __init__(self, gameId, matchId, instId, matchingId):
        super(MatchingFinishEvent, self).__init__(gameId, matchId, instId, matchingId)