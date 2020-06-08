#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/5
import json

import freetime.util.log as ftlog
from poker.util import keywords


def DATA_TYPE_INT(field, value, defaultVal, recovers):
    '''
    整形数字, 缺省为0
    '''
    try:
        if value != None :
            return int(value)
    except:
        if ftlog.is_debug() :
            ftlog.error()
    if recovers != None :
        recovers.append(field)
        recovers.append(defaultVal)
    assert(isinstance(defaultVal, int)), 'DATA_TYPE_INT type, defaultVal must be int, field=' + str(field)
    return defaultVal


def DATA_TYPE_INT_ATOMIC(field, value, defaultVal, recovers):
    '''
    整形数字, 缺省为0, 必须使用单独方法进行原子操作
    '''
    try:
        if value != None :
            return int(value)
    except:
        if ftlog.is_debug() :
            ftlog.error()
    if recovers != None :
        recovers.append(field)
        recovers.append(defaultVal)
    assert(isinstance(defaultVal, int)), 'DATA_TYPE_INT_ATOMIC type, defaultVal must be int, field=' + str(field)
    return defaultVal


def DATA_TYPE_FLOAT(field, value, defaultVal, recovers):
    '''
    浮点数字, 缺省为0.0
    '''
    try:
        if value != None :
            return float(value)
    except:
        if ftlog.is_debug() :
            ftlog.error()
    if recovers != None :
        recovers.append(field)
        recovers.append(defaultVal)
    assert(isinstance(defaultVal, float)), 'DATA_TYPE_FLOAT type, defaultVal must be float, field=' + str(field)
    return defaultVal


def DATA_TYPE_FLOAT_ATOMIC(field, value, defaultVal, recovers):
    '''
    浮点数字, 缺省为0.0, 必须使用单独方法进行原子操作  
    '''
    try:
        if value != None :
            return float(value)
    except:
        if ftlog.is_debug() :
            ftlog.error()
    if recovers != None :
        recovers.append(field)
        recovers.append(defaultVal)
    assert(isinstance(defaultVal, float)), 'DATA_TYPE_FLOAT_ATOMIC type, defaultVal must be float, field=' + str(field)
    return defaultVal


def DATA_TYPE_STR(field, value, defaultVal, recovers):
    '''
    字符串, 缺省为空串  
    '''
    try:
        if value != None :
            return unicode(value)
    except:
        if ftlog.is_debug() :
            ftlog.error()
    if recovers != None :
        recovers.append(field)
        recovers.append(defaultVal)
    assert(isinstance(defaultVal, (str, unicode))), 'DATA_TYPE_STR type, defaultVal must be str or unicode, field=' + str(field)
    return defaultVal


def DATA_TYPE_STR_FILTER(field, value, defaultVal, recovers):
    '''
    字符串, 缺省为空串, 如果有值则进行关键字过滤
    ''' 
    try:
        if value != None :
            return keywords.replace(unicode(value))
    except:
        if ftlog.is_debug() :
            ftlog.error()
    if recovers != None :
        recovers.append(field)
        recovers.append(defaultVal)
    assert(isinstance(defaultVal, (str, unicode))), 'DATA_TYPE_STR_FILTER type, defaultVal must be str or unicode, field=' + str(field)
    return defaultVal
