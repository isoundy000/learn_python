#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import datetime as datetime_module
import game_config


def datetime(year, month, day, hour, minute, second):
    """# timestamp_from_date: 根据给的时间生成datetime对象
    args:
        year, month, day, hour, minute, second:    ---    arg 2018, 07, 14, 22, 22, 22
    returns:
        0    ---
    """
    return datetime_module.datetime(year, month, day, hour, minute, second)


def datetime_from_timestamp(timestamp):
    """# datetime_from_timestamp: docstring
    args: 时间戳转datetime
        timestamp:    ---    arg
    returns:
        0    ---
    """
    return datetime_module.datetime.fromtimestamp(timestamp)


def datetime_to_timestamp(datetime_obj):
    """# datetime_to_timestamp: docstring
    args: datetime转时间戳
        datetime_obj:    ---    arg
    returns:
        0    ---
    """
    return time.mktime(datetime_obj.timetuple())


def timestamp_from_deltadaytime(datetime_obj, delta_day_int, hour, minute, second):
    """# timestamp_from_deltadaytime: 指定
    args:               # datetime时间延长几天的时间戳
        ll:    ---    arg
    returns:
        0    ---
    """
    delta_day = datetime_module.timedelta(delta_day_int, 0, 0)
    dt = datetime_obj + delta_day
    dt_new = datetime_module.datetime(
        dt.year,
        dt.month,
        dt.day,
        hour,
        minute,
        second
    )
    return datetime_to_timestamp(dt_new)


def timestamp_from_deltamonthtime(datetime_obj, month_delta, month_day, hour, minute, second):
    """# timestamp_from_deltadaytime: 指定
    args:                   # datetime时间延长几月的时间戳
        ll:    ---    arg
    returns:
        0    ---
    """
    delta_day = datetime_module.timedelta(month_delta * 30, 0, 0)
    dt = datetime_obj + delta_day
    dt_new = datetime_module.datetime(
        dt.year,
        dt.month,
        month_day,
        hour,
        minute,
        second
    )
    return datetime_to_timestamp(dt_new)


def timestamp_now():
    """# timestamp_now: docstring
    args:
        :    ---    arg
    returns:
        0    ---
    """
    return time.time()


def datetime_now():
    """# datetime_now: docstring
    args:
        :    ---    arg
    returns:
        0    ---
    """
    return datetime_module.datetime.now()

SECONDS_ONE_DAY = 3600 * 24
def timestamp_day(timestamp):
    """# timestamp_today: 根据时间戳，获得当天0点的时间戳
    args:
        :    ---    arg
    returns:
        0    ---
    """
    return int(timestamp) / SECONDS_ONE_DAY * SECONDS_ONE_DAY


def timestamp_different_days(time_1, time_2):
    """# timestamp_different_days: 计算两个时间戳相差的天数，天数不是按照24小时计算
    args:
        arg:    ---    arg
    returns:
        0    ---
    """
    return (datetime_from_timestamp(timestamp_day(time_2)) - datetime_from_timestamp(timestamp_day(time_1))).days