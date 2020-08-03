#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/11

import time


class FishData():
    """
    各个字段的含义描述
    lastlogin: 上次登录时间，从2012/5/1以来的第N天
    nslogin: 连续登录天数
    exp: 用户经验值
    level: 用户等级
    gunLevel: 用户最大火炮等级
    gunSkinId: 用户火炮皮肤
    registTime: 注册时间，2017/12/07新增
    """
    config = [
        ["lastlogin", 0],
        ["nslogin", 0],
        ["exp", 0],
        ["level", 1],
        ["gunLevel", 2101],
        ["gunSkinId", 0],
        ["gunLevel_m", 2101],
        ["gunSkinId_m", 0],
        ["loginDays", 1],
        ["continuousLogin", 1]
    ]

    @classmethod
    def getGameDataKeys(cls):
        """获取用户初始化的key"""
        keys = []
        for item in cls.config:
            keys.append(item[0])
        return keys

    @classmethod
    def getGameDataValues(cls):
        """获取玩家初始化的值"""
        values = []
        for item in cls.config:
            values.append(item[1])
        return values