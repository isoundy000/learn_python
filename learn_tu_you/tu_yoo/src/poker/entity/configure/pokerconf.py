#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6
'''
每个配置项必须是JSON格式
'''

from poker.entity.configure import configure


def getIntegrate():
    return configure.getJson('poker:global', {}).get('integrate', {})


getConfigGameIds = configure.getConfigGameIds


def getCmds():
    return configure.getJson('poker:cmd', {})


def getOldCmds():
    return configure.getJson('poker:oldcmd', {})





def isOpenMoreTable(clientId):
    '''
    判定一个clientId是否支持多开
    目前都不支持
    '''
    return False