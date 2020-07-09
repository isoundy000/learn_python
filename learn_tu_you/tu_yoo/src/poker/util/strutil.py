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
from sre_compile import isstring
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


def uuid():
    '''
    取得一个32位长的UUID字符串
    '''
    return str(uuid.uuid4()).replace('-', '')


def dumps(obj):
    '''
    驳接JSON的dumps方法, 使用紧凑的数据格式(数据项之间无空格)
    '''
    return json.dumps(obj, separators=(',', ':'))


def dumpsbase64(obj):
    '''
    驳接JSON的dumps方法,并对结果进行BASE64的编码
    '''
    jstr = json.dumps(obj, separators=(',', ':'))
    return base64.b64encode(jstr)


def loadsbase64(base64jsonstr, decodeutf8=False):
    '''
    驳接JSON的loads方法, 先对json串进行BASE64解密,再解析为JSON格式
    若decodeutf8为真, 那么将所有的字符串转换为ascii格式
    '''
    jsonstr = b64decode(base64jsonstr)
    datas = json.loads(jsonstr)
    if decodeutf8:
        datas = decodeObjUtf8(datas)
    return datas


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


def b64decode(base64str):
    '''
    驳接BASE64的解密方法, 替换数据中的空格到+号后,再进行解密
    '''
    base64str = base64str.replace(' ', '+')
    base64str = base64str.replace('%3d', '=')
    return base64.b64decode(base64str)


def b64encode(normalstr):
    '''
    驳接BASE64的加密方法
    '''
    return base64.b64encode(normalstr)


def md5digest(md5str):
    '''
    计算一个字符串的MD5值, 返回32位小写的MD5值
    '''
    m = md5()
    m.update(md5str)
    md5code = m.hexdigest()
    return md5code.lower()


def urlencode(params):
    '''
    将params进行URL编码
    '''
    return urllib.urlencode(params)


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
def getGameIdFromInstanceRoomId(roomId):
    '''
    解析房间实例的roomId(控制房间和桌子房间), 取得gameId
    注: 若为控制房间showdId必定为0, 若为桌子房间showdId必定大于0
    '''
    roomId = int(roomId)
    assert (roomId > 0)
    gameid = roomId / 10000000
    return gameid


@lfu_cache(maxsize=1000, cache_key_args_index=0)
def getGameIdFromBigRoomId(bigRoomId):
    '''
    解析房间的BigRoomId 取得gameId 444111000 / 1000
    '''
    bigRoomId = int(bigRoomId)
    assert (bigRoomId > 0)
    gameid = bigRoomId / 1000
    return gameid


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


def parseInts(*args):
    """
    转换成int类型
    :param args:
    :return:
    """
    rets = []
    for x in args:
        try:
            i = int(x)
        except:
            i = 0
        rets.append(i)
    if len(rets) == 1:
        return rets[0]
    return rets


def ensureString(val, defVal=''):
    """返回字符串"""
    if isstring(val):
        return val
    if val is None:
        return defVal
    return str(val)