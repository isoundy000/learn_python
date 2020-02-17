#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import datetime

REAL_TIME_FUNC = time.time
REAL_STRFTIME_FUNC = time.strftime
REAL_DATETIME_CLASS = datetime.datetime
REAL_DATETIME_FUNC = datetime.datetime.now


def change_time(t):
    """# change_time: 将*全局*当前时间修改成t，将来时间是以t为开始计时
        t 为unix时间戳，如果t为0，则时间恢复
        """
    time.time = REAL_TIME_FUNC
    time.strftime = REAL_STRFTIME_FUNC
    datetime.datetime = REAL_DATETIME_CLASS

    if t == 0:
        return

    delta_t = t - int(time.time())
    delta_obj = datetime.timedelta(seconds=delta_t)

    def fake_time_func():
        return REAL_TIME_FUNC() + delta_t

    time.time = fake_time_func

    def fake_strftime_func(fmt, time_tuple=None):
        if time_tuple is None:
            time_tuple = time.localtime(time.time())
        return REAL_STRFTIME_FUNC(fmt, time_tuple)

    time.strptime = fake_strftime_func

    class fake_datetime(datetime.datetime):
        """# fake_datetime: docstring"""
        @classmethod
        def now(cls, tz=None):
            return REAL_DATETIME_FUNC(tz) + delta_obj

    datetime.datetime = fake_datetime