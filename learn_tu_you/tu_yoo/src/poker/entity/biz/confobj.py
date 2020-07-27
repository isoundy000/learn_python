#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/26


from poker.entity.biz.exceptions import TYBizConfException
from poker.util.reflection import TYClassRegister
import freetime.util.log as ftlog


class TYConfable(object):
    TYPE_ID = 'unknown'

    def __init__(self):
        pass

    def decodeFromDict(self, d):
        raise NotImplementedError


class TYConfableRegister(TYClassRegister):
    @classmethod
    def decodeFromDict(cls, d):
        typeId = d.get('typeId')
        # ftlog.debug('typeId:', typeId, ' d:', d)

        clz = cls.findClass(typeId)
        if not clz:
            raise TYBizConfException(d, '%s unknown typeId %s' % (cls, typeId))

        try:
            confable = clz()
            confable.decodeFromDict(d)
        except Exception, e:
            ftlog.error(clz, d)
            raise e
        return confable

    @classmethod
    def decodeList(cls, dictList):
        ret = []
        for d in dictList:
            ret.append(cls.decodeFromDict(d))
        return ret
