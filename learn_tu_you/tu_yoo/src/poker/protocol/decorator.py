#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/14



def markCmdActionHandler(clazz):
    '''
    标记一个class为客户端发送的TCPCMD命令的入口类
    '''
    mtype = sys._getframe().f_code.co_name + '.' + clazz.__module__ + '.' + clazz.__name__
    setattr(clazz, _CLASS_MARKE, mtype)
    _marked_clz_method_data.clear()
    return clazz


def markCmdActionMethod(cmd, action='', clientIdVer=0.0, lockParamName='userId', scope='global'):
    pass
