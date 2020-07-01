#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6
import time
from datetime import datetime, timedelta

from dateutil import relativedelta


# 单位秒 s
def getCurrentTimestamp():
    '''
    获取当前时间戳 int (unit: second)
    '''
    return int(time.time())


def formatTimeDayInt(ct=None):
    '''
    取得当前的YYYYMMDD的int值, int(150721)
    '''
    if ct == None:
        ct = datetime.now()
    return int(ct.strftime('%Y%m%d')[-6:])


def formatTimeWeekInt(ct=None):
    '''
    取得当前的星期的数值, 例如2015年第二个星期, 返回 int(1502)
    '''
    if ct == None :
        ct = datetime.now()
    w = int(datetime.strftime(ct, '%W'))
    if w <= 0:                              # 如果是0，那么就是上一年的最后一周，调整到上一年的31日即可
        ct = ct - timedelta(days=ct.day)
        return (ct.year % 100) * 100 + int(datetime.strftime(ct, '%W'))
    else:
        return (ct.year % 100) * 100 + w


def formatTimeMonthInt(ct=None):
    '''
    取得当前的YYMM的int值, int(1507)
    '''
    if ct == None :
        ct = datetime.now()
    return int(ct.strftime('%Y%m')[-4:])


def formatTimeMs(ct=None):
    '''
    获取当前时间字符串:%Y-%m-%d %H:%M:%S.%f
    '''
    if ct == None:
        ct = datetime.now()
    ctfull = ct.strftime('%Y-%m-%d %H:%M:%S.%f')
    return ctfull


def formatTimeSecond(ct=None):
    '''
    获取当前时间字符串:%Y-%m-%d %H:%M:%S
    '''
    if ct == None :
        ct = datetime.now()
    ctfull = ct.strftime('%Y-%m-%d %H:%M:%S')
    return ctfull