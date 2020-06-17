#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/2

from hashlib import md5
import uuid
import json
import base64
import urllib
import re
import struct
import os
import freetime.util.log as ftlog

from freetime.util import encry
from freetime.util.cache import lfu_cache
from poker.util.constants import CLIENT_SYS_IOS, CLIENT_SYS_ANDROID, CLIENT_SYS_H5, \
    CLIENT_SYS_WINPC, CLIENT_SYS_MACOS
from poker.util import constants
from copy import deepcopy


def cloneData(data):
    '''
    使用JSON的loads和dump克隆一个数据对象
    '''
    return deepcopy(data)
    # try:
    #     return json.loads(json.dumps(data))
    # except:
    #     ftlog.warn('Can not use json copy !! data=' + repr(data))
    #     return deepcopy(data)


def loads(jsonstr, decodeutf8=False, ignoreException=False, execptionValue=None):
    '''
    驳接JSON的loads方法
    若decodeutf8为真, 那么将所有的字符串转换为ascii格式
    若ignoreException为真, 那么忽略JSON格式的异常信息
    若execptionValue为真, 当若ignoreException为真时,发生异常,则使用该缺省值
    '''
    if ignoreException:
        try:
            datas = json.loads(jsonstr)
        except:
            datas = execptionValue
    else:
        datas = json.loads(jsonstr)
    if datas and decodeutf8:
        datas = decodeObjUtf8(datas)
    return datas



def decodeObjUtf8(datas):
    '''
    遍历datas(list,dict), 将遇到的所有的字符串进行encode utf-8处理
    '''
    if isinstance(datas, dict):
        ndatas = {}
        for key, val in datas.items():
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            ndatas[key] = decodeObjUtf8(val)
        return ndatas
    if isinstance(datas, list):
        ndatas = []
        for val in datas:
            ndatas.append(decodeObjUtf8(val))
        return ndatas
    if isinstance(datas, unicode):
        return datas.encode('utf-8')
    return datas



@lfu_cache(maxsize=1000, cache_key_args_index=0)
def parseClientId(clientId):
    '''
    解析客户端Id
    :param clientId:
    '''
    if isinstance(clientId, (str, unicode)):
        infos = clientId.split('_', 2)
        if len(infos) == 3:
            try:
                clientsys = infos[0][0]
                if clientsys == 'W':
                    clientsys = CLIENT_SYS_WINPC
                elif clientsys == 'I' or clientsys == 'i':
                    clientsys = CLIENT_SYS_IOS
                elif clientsys == 'H' or clientsys == 'h':
                    clientsys = CLIENT_SYS_H5
                elif clientsys == 'M' or clientsys == 'm':
                    clientsys = CLIENT_SYS_MACOS
                else:
                    clientsys = CLIENT_SYS_ANDROID
                return clientsys, float(infos[1]), infos[2]
            except:
                ftlog.error('clientId=', clientId)
                return 'error', 0, 'error'
    ftlog.error('parseClientId params error, clientId=', clientId)
    return 'error', 0, 'error'