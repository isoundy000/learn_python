#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/2


class TYUserVipSystem(object):

    def getUserVip(self, userId):
        '''
        获取用户vip
        @param userId: 要获取的用户ID
        @return: TYUserVip
        '''
        raise NotImplemented()


userVipSystem = TYUserVipSystem()


def _initialize():
    pass