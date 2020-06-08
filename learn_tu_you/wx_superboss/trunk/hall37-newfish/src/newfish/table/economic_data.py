#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6



class EconomicData(object):
    """
    渔场内资产缓存数据
    """
    def __init__(self, player, table):
        self.player = player
        self.userId = player.userId
        self.clientId = player.clientId
        self.table = table
        self.loadData()
    
    def loadData(self):
        pass