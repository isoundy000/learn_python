#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from Source.DataBase.Table.t_system_params import t_system_params
from Source.GameData import GameData
from Source.GameData import ReviewVersion
from Source.GameData import WriteList
from Source.GameData import ChannelForceUpdate
from Source.Log.Write import Log


def ReviewVersionRefresh():
    '''
    提审服白名单版本
    :return:
    '''
    ReviewVersion.review_version_lst.clear()
    fm_db = t_system_params.LoadParamBykey("review_version_lst")
    if fm_db:
        tmp1 = fm_db.split(",")
        for tmp11 in tmp1:
            if tmp11:
                ReviewVersion.review_version_lst.add(tmp11)
    Log.Write("ReviewVersion.review_version_lst", ReviewVersion.review_version_lst)


def SyncResource2Refresh():
    '''
    同步前端资源版本号和非法的版本号
    :return:
    '''
    GameData.gWhiteTestResourceVersion = t_system_params.LoadParamBykey("WhiteTestResourceVersion")     # 前端资源热更白名单测试功能
    if GameData.gWhiteTestResourceVersion:
        GameData.gWhiteTestResourceVersion = int(GameData.gWhiteTestResourceVersion)
    Log.Write("GameData.gWhiteTestResourceVersion", GameData.gWhiteTestResourceVersion)
    GameData.gInvalidClientVersion = t_system_params.LoadParamBykey("InvalidClientVersion")
    if GameData.gInvalidClientVersion:
        GameData.gInvalidClientVersion = int(GameData.gInvalidClientVersion)
    Log.Write("GameData.gInvalidClientVersion", GameData.gInvalidClientVersion)


def WriteListRefresh():
    '''
    白名单ip list
    :return:
    '''
    WriteList.ip_list.clear()
    fm_db = t_system_params.LoadParamBykey("writelist")
    if fm_db:
        tmp1 = fm_db.split(",")
        for tmp11 in tmp1:
            if tmp11:
                WriteList.ip_list.add(tmp11)
    WriteList.ip_list = WriteList.ip_list | WriteList.ip_list_config        # set([1, 2, 3, 4, 5]) == set([1, 2]) | set([3, 4, 5])
    Log.Write("WriteList.ip_list", WriteList.ip_list)


def Init():
    SyncResource2Refresh()
    ReviewVersionRefresh()
    WriteListRefresh()
    ChannelForceUpdate.channel_forceupdate_url.clear()                  # 清理系统消息 系统通知渠道强制下载更新