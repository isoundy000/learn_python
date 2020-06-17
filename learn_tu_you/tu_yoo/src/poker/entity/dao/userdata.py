#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/3

from poker.entity.dao import daoconst
from poker.entity.dao.daoconst import UserDataSchema
from poker.servers.util.direct import dbuser


def getAttrs(userId, filedList):
    '''
        取得用户的主账户数据
        '''
    assert (isinstance(userId, int))
    assert (userId > 0)
    return dbuser._getUserDatas(userId, filedList)


def getAttr(userId, field):
    '''
    获取用户属性值
    '''
    vals = getAttrs(userId, [field])
    return vals[0]