#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/8


class TYObservers(dict):
    '''
    桌子上的观察者的集合
    '''
    def __init__(self, table):
        super(TYObservers, self).__init__()
        self.table = table