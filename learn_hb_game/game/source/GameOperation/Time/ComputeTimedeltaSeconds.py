#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


from datetime import datetime, timedelta


def ComputeTimedeltaSeconds(t1, t2):
    '''
    两个datetime时间相差的秒数
    :param t1:
    :param t2:
    :return:
    '''
    td = t1 - t2
    return td.seconds + td.days * 24 * 60 * 60