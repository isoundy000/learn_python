#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/3

'''
游戏基类
'''
from freetime.core.timer import FTLoopTimer
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.entity.events.tyeventbus import TYEventBus
from poker.entity.robot.robot import TYRobotManager


class _TYGameCallAble(type):

    def __init__(self, name, bases, dic):
        super(_TYGameCallAble, self).__init__(name, bases, dic)
        self.instance = None

    def __call__(self, gameId=0, *args, **kwargs):
        v = None
        if gameId > 0:
            v = gdata.games()[gameId]
        else:
            if self.instance is None:
                self.instance = super(_TYGameCallAble, self).__call__(*args, **kwargs)
            v = self.instance
        return v



class TYGame(object):

    __metaclass__ = _TYGameCallAble
    PLAY_COUNT = 'playGameCount'                # 游戏局数
    WIN_COUNT = 'winGameCount'                  # 胜利局数

    def __init__(self, *args, **argds):
        self._eventBus = TYEventBus()
        self._robotmgr = TYRobotManager()
        self._packageName = None                # 此变量由系统自动赋值, 其值为当前游戏的主package的名字
        self._robotmgr.gameId = self.gameId()

    def gameId(self):
        '''
        取得当前游戏的GAMEID, int值
        '''
        raise NotImplementedError('')

    def newTable(self, room, tableId):
        '''
        此方法由系统进行调用
        更具给出的房间的基本定义信息, 创建一个TYTable的实例
        其必须是 poker.entity.game.table.TYTable的子类
        room 桌子所属的房间的TYRoom实例
        tableId 新桌子实例的ID
        '''
        raise NotImplementedError('')

    def initGameBefore(self):
        '''
        此方法由系统进行调用
        游戏初始化的预处理
        '''

    def initGame(self):
        '''
        此方法由系统进行调用
        游戏自己初始化业务逻辑模块, 例如: 初始化配置, 建立事件中心等
        执行的时序为:  首先调用所有游戏的 initGameBefore()
                    再调用所有游戏的 initGame()
                    最后调用所有游戏的 initGameAfter()
        '''

    def initGameAfter(self):
        '''
        此方法由系统进行调用
        游戏初始化的后处理
        '''

    def getInitDataKeys(self):
        '''
        取得游戏数据初始化的字段列表
        '''
        return []

    def getInitDataValues(self):
        '''
        取得游戏数据初始化的字段缺省值列表
        '''
        return []

    def getGameInfo(self, userId, clientId):
        '''
        取得当前用户的游戏账户信息dict
        '''
        return {}

    def getDaShiFen(self, userId, clientId):
        '''
        取得当前用户的游戏账户的大师分信息
        '''
        return {}

    def getPlayGameCount(self, userId, clientId):
        '''
        取得当前用户游戏总局数
        '''
        return 0

    def getPlayGameInfoByKey(self, userId, clientId, keyName):
        '''
        取得当前用户的游戏信息
        key - 要取得的信息键值，枚举详见TYGame类的宏定义
        '''
        return None

    def getEventBus(self):
        '''
        取得当前游戏的事件中心
        '''
        return self._eventBus

    def isWaitPigTable(self, userId, room, tableId):
        '''
        检查是否是杀猪状态的桌子, 缺省为非杀猪状态的桌子
        '''
        return 0


GAME_STATUS_RUN = 0                     # 进程初始化后，处于正常服务状态
GAME_STATUS_SHUTDOWN_GO = 80            # 进程接收到了关闭命令，停止接收例如quickstart等消息，进行关闭处理
GAME_STATUS_SHUTDOWN_ERROR = 90         # 进程接收到了关闭命令，停止接收例如quickstart等消息，进行关闭处理,但是关闭过程中出现了异常
GAME_STATUS_SHUTDOWN_DONE = 100         # 进程接收到了关闭命令，并且已经处理完成
_gameStatus = GAME_STATUS_RUN