#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/17
import calendar
from poker.servers.util.direct import dbuser
from poker.util import timestamp
from datetime import datetime

CYCLE_TYPE_DAY = 1  # 每天循环(自然天)
CYCLE_TYPE_WEEK = 2  # 每星期循环(自然周)
CYCLE_TYPE_MONTH = 3  # 每月循环(自然月)
CYCLE_TYPE_MONTH_REMAIN_TIME = 4  # 本月剩余时间




def getWeakData(userId, gameId, cycleType, datakey):
    '''
    取得一个用户的弱存储数据, 例如: 每日登陆的数据,凌晨过后即被清空重新建立
    cycleType 参考: CYCLE_TYPE_DAY, CYCLE_TYPE_WEEK, CYCLE_TYPE_MONTH
    返回必定是一个dict数据集合
    可参考day1st.py的使用方法
    '''
    return ""