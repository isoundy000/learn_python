#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/1

import time
from freetime.util.metaclasses import Singleton
from freetime.util import log as ftlog



class TYEvent(object):
    '''
    事件基类
    '''
    def __init__(self):
        self.timestamp = int(time.time())


class EventConfigure(TYEvent):
    '''
    当配置信息发生变化时, 触发此事件,
    '''
    def __init__(self, keylist, reloadlist):
        super(EventConfigure, self).__init__()
        self.keylist = set(keylist)
        self.reloadlist = reloadlist
        self.modules = []
        for k in self.keylist:
            if k == 'all':
                self.modules = ['all']
                break
            else:
                if k.startswith('game'):
                    ks = k.split(':')
                    self.modules.append(ks[2])
                else:
                    self.modules.append(k)
        ftlog.debug('EventConfigure->self.modules=', self.modules)

    def isModuleChanged(self, keys):
        '''
        模块是否改变
        :param keys:
        :return:
        '''
        if 'all' in self.modules:
            return True
        if isinstance(keys, (list, set)):
            for key in keys:
                if key in self.modules:
                    return True
            return False
        return keys in self.modules

    def isChanged(self, keys):
        '''
        集合是否改变
        :param keys:
        :return:
        '''
        if 'all' in self.keylist:
            return True
        if isinstance(keys, (list, set)):
            for key in keys:
                if key in self.keylist:
                    return True
            return False
        return keys in self.keylist


class EventHeartBeat(TYEvent):
    '''
    每秒钟系统服务心跳处理
    每秒钟一次的心跳事件广播, 执行之后间隔一秒再次启动, 即: 这个每秒心跳是个大约值,非准确值
    '''
    __metaclass__ = Singleton
    count = 0

    def __init__(self):
        super(EventHeartBeat, self).__init__()


class UserEvent(TYEvent):
    '''玩家事件'''
    def __init__(self, userId, gameId):
        super(UserEvent, self).__init__()
        self.__gameId = gameId
        self.__userId = userId

    @property
    def gameId(self):
        return self.__gameId

    @property
    def userId(self):
        return self.__userId


# class EventUserAttrsChanged(UserEvent):
#     '''
#     用户的基本属性发生变化, 例如 昵称, 性别
#     由Account.updateUserBaseInfo方法发送至全局globalEventBus
#     用途举例: 斗牛的修改昵称送金币的业务逻辑
#     '''
#     def __init__(self, userId, attNameList):
#         super(EventUserAttrsChanged, self).__init__(userId, 0)
#         self.attNameList = attNameList


class EventUserLogin(UserEvent):
    '''
    用户登录一个游戏的事件
    由Account.loginGame方法发送至游戏实例的tygame.getEventBus()
    '''

    def __init__(self, userId, gameId, dayFirst, isCreate, clientId, isVersionUpdate=False):
        super(EventUserLogin, self).__init__(userId, gameId)
        self.dayFirst = dayFirst
        self.isCreate = isCreate
        self.clientId = clientId
        self.clipboardContent = None        # 粘贴板内容
        self.isVersionUpdate = isVersionUpdate


class MatchEvent(UserEvent):

    def __init__(self, userId, gameId, matchId):
        pass


class ChargeNotifyEvent(UserEvent):
    """
    充值通知事件
    """
    def __init__(self, userId, gameId, rmbs, diamonds, productId, clientId):
        super(ChargeNotifyEvent, self).__init__(userId, gameId)
        self.rmbs = rmbs
        self.diamonds = diamonds
        self.productId = productId
        self.clientId = clientId


class OnLineGameChangedEvent(UserEvent):
    def __init__(self, userId, gameId, isEnter, clientId=None):
        super(OnLineGameChangedEvent, self).__init__(userId, gameId)
        self.isEnter = isEnter
        self.clientId = clientId