#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


# 每秒钟运行一次
TickTimerConfig = [
    # (1, SystemSecTick),
    # (15, SystemStatus),
]


# 每小时运行一次
PerDayHourConfig = {
    0: [],
    1: [],
    23: [],
}


# 每半点运行一次 如: (00:30, 01:30, ...)
PerDayHalfHourConfig = {
    0: [],
    1: [],
    23: [],
}


# 精确时间运行
ExactTimerConfig = [
    # (12, 0, 0, WorldBoss1Start),
    # (12, 30, 0, WorldBoss1End),
]


SecondTimerConfig = []