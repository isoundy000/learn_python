#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/15
from datetime import datetime
import os, stackless, urllib

from twisted.internet import defer, reactor
from twisted.internet.defer import succeed
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers
from twisted.web.iweb import IBodyProducer
from zope.interface import implements

from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.util import strutil
from freetime.core.tasklet import FTTasklet

TRACE_RESPONSE = 0  # 是否跟踪打印所有的REQUEST和RESPONSE
CONTENT_TYPE_JSON = {'Content-Type': 'application/json;charset=UTF-8'}
CONTENT_TYPE_HTML = {'Content-Type': 'text/html;charset=UTF-8'}
CONTENT_TYPE_PLAIN = {'Content-Type': 'application/octet-stream', 'Content-Disposition': 'attachment' }
CONTENT_TYPE_GIF = {'Content-Type': 'image/gif'}

_http_path_methods = {}  # HTTP命令集合中心, key为HTTP的全路径, value为处理该路径的callable
_path_webroots = []  # 静态资源的查找路径列表




def getRequest():
    '''
    取得当前HTTP请求的原始的request对象
    '''
    return stackless.getcurrent()._fttask.run_args['data']


def getDict():
    '''
    将当前的HTTP请求的所有参数内容, 转换为一个dict
    '''
    request = getRequest()
    args = request.args
    rparam = {}
    for k, v in args.items():
        rparam[k] = v[0].strip()
    return rparam


def getParamStr(key, defaultVal=None):
    pass


def getParamInt(key, defaultVal=0):
    '''
    取得当前HTTP请求的一个参数的int值
    '''
    val = getParamStr(key, defaultVal)
    try:
        return int(val)
    except:
        pass
    return defaultVal