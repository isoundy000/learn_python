#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6
import time
from datetime import datetime, timedelta

from dateutil import relativedelta


def timeStampToStr(ts, formatTime = "%Y-%m-%d %H:%M:%S"):
    """时间戳转字符串"""
    t = time.localtime(ts)
    return time.strftime(formatTime, t)


def getDaysList(tstp, count, formatTime = "%Y-%m-%d"):
    ret = []
    for i in range(count):
        ret.append(timeStampToStr(tstp + i * 24 * 3600, formatTime))
    return ret


def getTimeStampFromStr(strTime, formatTime = "%Y-%m-%d %H:%M:%S"):
    """字符串转时间戳"""
    timeArray = time.strptime(strTime, formatTime)
    timeStamp = int(time.mktime(timeArray))
    return timeStamp


def getMonthStartTimestamp(timestamp=None):
    '''
    获取timestamp所在时间当前月的开始时间
    '''
    return getDeltaMonthStartTimestamp(timestamp, 0)


def getWeekStartTimestamp(timestamp=None):
    '''
    获取timestamp这个时间所在周的开始时间戳
    '''
    if timestamp is None:
        timestamp = int(time.time())
    dt = datetime.fromtimestamp(timestamp)
    return (timestamp - dt.date().weekday() * 86400 - dt.hour * 3600 - dt.minute * 60 - dt.second)


def getDayLeftSeconds(timestamp=None):
    '''
    获取timestamp这个时间到timestamp所在的天结束时的秒数
    '''
    return 86400 - getDayPastSeconds(timestamp)


def getDayPastSeconds(timestamp=None):
    '''
    今日零点到现在过去的秒数
    '''
    if timestamp is None:
        timestamp = int(time.time())
    nt = time.localtime(timestamp)
    return nt[3] * 3600 + nt[4] * 60 + nt[5]


def getDayStartTimestamp(timestamp=None):
    '''
    获取今天零点的时间戳
    '''
    if timestamp is None:
        timestamp = int(time.time())
    return int(timestamp) - getDayPastSeconds(timestamp)


# 单位秒 s
def getCurrentTimestamp():
    '''
    获取当前时间戳 int (unit: second)
    '''
    return int(time.time())


def getCurrentTimestampFloat():
    '''
    获取当前时间戳 float (unit: second)
    '''
    return time.time()


def getCurrentDayStartTimestamp():
    '''
    获取今天开始的时间戳
    '''
    tNow = getCurrentTimestamp()
    return tNow - (tNow % 86400)


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



def isSameMonth(d1, d2):
    return d1.strftime('%Y%m') == d2.strftime('%Y%m')


def is_same_week(timestamp1, timestamp2):
    return getWeekStartTimestamp(timestamp1) == getWeekStartTimestamp(timestamp2)


def is_same_day(timestamp1, timestamp2):
    return datetime.fromtimestamp(timestamp1).date() == datetime.fromtimestamp(timestamp2).date()