#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/10
'''常量基类
'''


class BaseConst(object):
    '''自定义常量基类
    '''
    class ConstError(TypeError): pass
    class ConstCaseError(ConstError): pass

    def __setattr__(self, name, value):
        if self.__dict__.has_key(name):
            raise self.ConstError, "Can't change const.%s" % name
        if not name.isupper():
            raise self.ConstCaseError, 'Const name "%s" is not all uppercase' % name
        self.__dict__[name] = value


class TyGlobleConst(BaseConst): pass


import sys
sys.modules["tyGlobleConst"] = TyGlobleConst()

import tyGlobleConst
tyGlobleConst.VERTION = 0.1
print tyGlobleConst.VERTION