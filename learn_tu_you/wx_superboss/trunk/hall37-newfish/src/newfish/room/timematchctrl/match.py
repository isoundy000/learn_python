#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/10



class TimeMatch(object):

    _matchMap = {}

    WINLOSE_SLEEP = 0

    @classmethod
    def getMatch(cls, roomId):
        """获取比赛"""
        return cls._matchMap.get(roomId, None)