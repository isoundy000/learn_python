#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6
import time
from datetime import datetime


# 单位秒 s
def getCurrentTimestamp():
    '''
    获取当前时间戳 int (unit: second)
    '''
    return int(time.time())


def formatTimeMs(ct=None):
    '''
        获取当前时间字符串:%Y-%m-%d %H:%M:%S.%f
        '''
    if ct == None:
        ct = datetime.now()
    ctfull = ct.strftime('%Y-%m-%d %H:%M:%S.%f')
    return ctfull