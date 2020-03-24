#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from datetime import datetime, timedelta
from Source.Log.Write import Log


def Refresh():
    '''
    拼接当前的年月日时间
    :return:
    '''
    time_str_list = str(datetime.now().date()).split("-")
    time_str = time_str_list[0] + "_" + time_str_list[1] + "_" + time_str_list[2]
    Log.Write("[Report_time_str]", time_str)
    return time_str


def Refresh7d():
    b7day = datetime.now().date() - timedelta(days=7)
    time_str_list = str(b7day).split("-")
    time_str = time_str_list[0] + "_" + time_str_list[1] + "_" + time_str_list[2]
    Log.Write("[Report_time_str]", time_str)
    return time_str


if __name__ == '__main__':
    Refresh()
    Refresh7d()