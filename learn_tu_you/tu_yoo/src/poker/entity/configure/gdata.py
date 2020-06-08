#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/2

import stackless

import psutil

import freetime.entity.config as ftcon
import freetime.util.log as ftlog

ENABLIE_DEFENCE_2 = 1

RUN_MODE_ONLINE = 1         # 服务运行模式: 正式线上
RUN_MODE_SIMULATION = 2     # 服务运行模式: 仿真
RUN_MODE_RICH_TEST = 3      # 服务运行模式: 大机器测试模式（机器资源多，可自由配置进程）
RUN_MODE_TINY_TEST = 4      # 服务运行模式: 个人小机器测试模式（机器资源少，自动最小资源模式）

SRV_TYPE_AGENT = 'AG'       # 服务类型: 消息代理传输服务
SRV_TYPE_SDK_HTTP = 'PL'    # 服务类型: PLATFORM SDK的HTTP服务
SRV_TYPE_SDK_GATEWAY = 'PG' # 服务类型: PLATFORM SDK的HTTP服务
SRV_TYPE_CONN = 'CO'        # 服务类型: 游戏接入的TCP链接服务
SRV_TYPE_HTTP = 'HT'        # 服务类型: 游戏的HTTP服务
SRV_TYPE_ROBOT = 'RB'       # 服务类型: 游戏的机器人服务
SRV_TYPE_UTIL = 'UT'        # 服务类型: 游戏的无状态消息处理服务(例如: 取得插件列表)
SRV_TYPE_ROOM = 'GR'        # 服务类型: 游戏的房间服务
SRV_TYPE_TABLE = 'GT'       # 服务类型: 游戏的桌子服务
SRV_TYPE_CENTER = 'CT'      # 服务类型: 游戏的业务处理中心服务(例如: 排行榜等集中处理的业务)


SRV_TYPE_PKG_NAME = {
    SRV_TYPE_AGENT: 'agent',
    SRV_TYPE_SDK_HTTP: 'http',
    SRV_TYPE_SDK_GATEWAY: 'gateway',
    SRV_TYPE_CONN: 'conn',
    SRV_TYPE_HTTP: 'http',
    SRV_TYPE_ROBOT: 'robot',
    SRV_TYPE_UTIL: 'util',
    SRV_TYPE_ROOM: 'room',
    SRV_TYPE_TABLE: 'table',
    SRV_TYPE_CENTER: 'center',
}


SRV_TYPE_ALL = (SRV_TYPE_AGENT, SRV_TYPE_SDK_HTTP, SRV_TYPE_CONN, SRV_TYPE_HTTP,
                SRV_TYPE_ROBOT, SRV_TYPE_UTIL, SRV_TYPE_ROOM, SRV_TYPE_TABLE,
                SRV_TYPE_CENTER, SRV_TYPE_SDK_GATEWAY)


PROTOCOL_TYPE_HTTP = 'ht-http'  # 协议类型 : 游戏服的HTTP协议
PROTOCOL_TYPE_CONN = 'co-tcp'   # 协议类型 : CONN服务的TCP协议
PROTOCOL_TYPE_GAME_S2A = 's2a'  # 协议类型 : 游戏服务的TCP协议


CONN_CMD_ROUTE_TYPE_RANDOM = 'random'   # CONN接到命令时的路由类型: 在目标类型服务进程中, 随机选择一个进程, 进行转发
CONN_CMD_ROUTE_TYPE_UESRID = 'userId'   # CONN接到命令时的路由类型: 在目标类型服务进程中, 选择参数USERID取模所在进程, 进行转发
CONN_CMD_ROUTE_TYPE_ROOMID = 'roomId'   # CONN接到命令时的路由类型: 目标类型一定是GR类型, 选择参数ROOMID的值所对应的进程, 直接转发
CONN_CMD_ROUTE_TYPE_TABLEID = 'tableId' # CONN接到命令时的路由类型: 目标类型一定是GT类型, 选择参数TABLEID的值所对应的进程, 直接转发


_datas = {}     # 内部变量保存空间

curProcess = psutil.Process()


def _initialize():
    global _datas
    if len(_datas) <= 0:
        ftlog.info('_initialize gdata begin.')
        _datas = {}
        pgdict = ftcon.getConf('poker:global')
        sid = ftcon.global_config["server_id"]
        _datas['server_type'] = sid[0:2]
        _datas['server_num'] = sid[2:]
        try:
            _datas['server_num_idx'] = int(sid[2:]) - 1
        except:
            _datas['server_num_idx'] = -1
        _datas.update(pgdict)
        _datas['game_packages'] = tuple(pgdict['game_packages'])
        pass


def initializeOk():
    '''
    判定当前各个游戏是否初始化完成
    注: 由poker系统initialize()方法进行初始化
    :return:
    '''
    return _datas.get('initialize.ok', 0)


def getTaskSession():
    '''获取task的session'''
    return stackless.getcurrent()._fttask.session


def isControlProcess():
    '''是控制进程'''
    return _datas['is_control_process']


def isHttpProcess():
    return _datas['is_http_process']


def gamePackages():
    '''
    取得要初始化的游戏的package包列表, 例如: ['hall', 'dizhu', 'texas']
    '''
    return _datas['game_packages']


def games():
    '''
    取得当前系统初始化后的TYGame的所有实例
    key为: int(gameId)
    value为: TYGame()
    注: 由poker系统initialize()方法进行初始化
    '''
    return _datas['tygame.instance.dict']

def globalConfig():
    '''
    取得global.json的配置内容
    '''
    return ftcon.global_config


def serverId():
    '''
    当前进程的ID, 例如: GA00060001, UT01
    '''
    return globalConfig()['server_id']


def serverType():
    '''
    当前进程的类型, 例如: GA, UT
    '''
    return _datas['server_type']


def serverNum():
    '''
    当前进程的ID去掉类型后的部分, 例如: 00060001, 01
    '''
    return _datas['server_num']


def serverNumIdx():
    '''
    当前进程的ID去掉类型后的部分, 例如: 00060001, 01
    '''
    return _datas['server_num_idx']


def centerServerLogics():
    '''
    取得配置当中, CENTER定义的业务逻辑服务
    '''
    return _datas['center_server_logic']


def name():
    '''
    在poker.json中定义的name的值
    '''
    return _datas['name']


def corporation():
    '''
    在poker.json中定义的corporation的值
    '''
    return _datas['corporation']


def mode():
    '''
    运行模式, 在poker.json中定义的mode的值
    参考: RUN_MODE_ONLINE, RUN_MODE_SIMULATION, RUN_MODE_RICH_TEST, RUN_MODE_TINY_TEST
    '''
    return _datas['mode']