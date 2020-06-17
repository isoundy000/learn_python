#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6
import time


# 单位秒 s
def getCurrentTimestamp():
    '''
    获取当前时间戳 int (unit: second)
    '''
    return int(time.time())