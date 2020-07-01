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
        if value != None:
            return int(value)
    except:
        if ftlog.is_debug():
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
        if value != None:
            return int(value)
    except:
        if ftlog.is_debug():
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
        if value != None:
            return float(value)
    except:
        if ftlog.is_debug():
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
        if value != None:
            return float(value)
    except:
        if ftlog.is_debug():
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
        if value != None:
            return unicode(value)
    except:
        if ftlog.is_debug():
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
        if ftlog.is_debug():
            ftlog.error()
    if recovers != None:
        recovers.append(field)
        recovers.append(defaultVal)
    assert(isinstance(defaultVal, (str, unicode))), 'DATA_TYPE_STR_FILTER type, defaultVal must be str or unicode, field=' + str(field)
    return defaultVal


def DATA_TYPE_LIST(field, value, defaultVal, recovers):
    '''
    JSON格式的数组, 缺省为[]
    '''
    try:
        if value != None :
            vl = json.loads(value)
            if isinstance(vl, list):
                return vl
    except:
        if ftlog.is_debug():
            ftlog.error()
    if recovers != None :
        recovers.append(field)
        recovers.append(defaultVal)
    assert(isinstance(defaultVal, list)), 'DATA_TYPE_LIST type, defaultVal must be dict, field=' + str(field)
    return defaultVal


def DATA_TYPE_DICT(field, value, defaultVal, recovers):
    '''
    JSON格式的字典, 缺省的{}
    '''
    try:
        if value != None :
            vl = json.loads(value)
            if isinstance(vl, dict):
                return vl
    except:
        if ftlog.is_debug():
            ftlog.error()
    if recovers != None :
        recovers.append(field)
        recovers.append(defaultVal)
    assert(isinstance(defaultVal, dict)), 'DATA_TYPE_DICT type, defaultVal must be dict, field=' + str(field)
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


def DATA_TYPE_BOOLEAN(field, value, defaultVal, recovers):
    '''
    真假值, 缺省为假 False
    '''
    if value == 1 or value == 'true' or value == 'True':
        return 1
    if recovers != None:
        if value == 0 or value == 'false' or value == 'False':
            return 0
        else:
            recovers.append(field)
            recovers.append(defaultVal)
    assert (defaultVal == 0 or defaultVal == 1), 'DATA_TYPE_BOOLEAN type, defaultVal must be 0 or 1, field=' + str(
        field)
    return defaultVal


def redisDataSchema(cls):
    return ""


class DataSchema():

    FIELDS_ALL = ()  # 字段集合, 由redisDataSchema修饰符自动赋值
    FIELDS_ALL_SET = set()
    WRITES_FIELDS = set()
    READ_ONLY_FIELDS = ()  # 只读字段集合, 由redisDataSchema修饰符自动赋值, 即 检测方法名称以_ATOMIC为结尾的字段集合

    @staticmethod
    def checkData(field, value, recovers=None):
        '''
        检测对应的字段的数据格式, 此方法由redisDataSchema修饰符自动生成
        '''

    @classmethod
    def mkey(*argl):
        '''
        返回数据中的主键的值, 此方法由redisDataSchema修饰符自动生成
        '''