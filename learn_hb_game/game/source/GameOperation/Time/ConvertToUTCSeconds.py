#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import time


def ConvertToUTCSeconds(t):
    '''
    转化datetime为时间戳
    :param t:
    :return:
    '''
    return int(time.mktime((t.year, t.month, t.day, t.hour, t.minute, t.second, 0, 0, 0)))