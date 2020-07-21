#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/4

from collections import namedtuple

from freetime.core.timer import FTTimer
import freetime.entity.config as ftcon
import freetime.entity.service as ftsvr
import freetime.util.log as ftlog
from poker.entity.configure import gdata, configure
from poker.entity.events.tyevent import EventHeartBeat
from poker.entity.events.tyeventbus import globalEventBus
from poker.entity.game.game import TYGame
from poker.protocol.procstatus import updateStatus
from poker.util import strutil
from poker.util.objects import makeReadonly
from freetime.core.tasklet import FTTasklet
from freetime.util import performance
from freetime.core import protocol

_DEBUG = 0
debug = ftlog.info


def getProtoClassByName(protoname):
    '''
    扑克大厅系统的协议层支持设定
    '''



def initialize():
    '''
    扑克大厅系统的初始化入口
    当所有的REDIS和MYSQL链接建立完成后调用此方法
    '''
    try:
        if _DEBUG:
            debug('==== poker.initialize begin ====')
        sconf = ftcon.getServerConf(ftsvr.getId())
        taskc = sconf.get('task-concurrent', 0)
        if taskc > 0:
            FTTasklet.MAX_CONCURRENT = taskc
            if _DEBUG:
                debug('reset FTTasklet.MAX_CONCURRENT=', FTTasklet.MAX_CONCURRENT)

        from poker.entity.dao import daobase
        daobase._REDIS_CMD_PPS_ = 1
        configure._CONFIG_CMD_PPS_ = 1
        protocol._COUNT_PPS = 1
        performance.regPPSCounter(protocol.ppsCountProtocolPack)
        performance.regPPSCounter(configure.ppsCountConfigCmds)
        performance.regPPSCounter(daobase.ppsCountRedisCmd)
        performance.regPPSCounter(performance.threadInfo)

        # 初始化基本全局配置数据
        updateStatus(10)
        gdatas = gdata._initialize()

        from poker.entity.biz import bireport
        bireport.report('bireport', 'open')

        # 初始化DAO
        updateStatus(20)
        daobase._initialize()

        # 初始化旧命令对照表
        updateStatus(30)
        from poker.protocol import oldcmd
        oldcmd._initialize()

        # 装载游戏的PLUGIN
        updateStatus(40)
        tygamelist = _loadTYGames(gdatas)

        # 初始化命令路由
        updateStatus(50)
        from poker.protocol import router
        router._initialize()

        if gdata.serverType() == gdata.SRV_TYPE_UTIL:   # 服务类型: 游戏的无状态消息处理服务(例如: 取得插件列表)
            router._initialize_udp()

        # 初始化房间配置
        updateStatus(60)
        _loadRoomDefines(gdatas)
    except:
        pass



def _doServertHeartBeat():
    '''
    每秒钟一次的心跳事件广播, 执行之后间隔一秒再次启动, 即: 这个每秒心跳是个大约值,非准确值
    '''
    pass


def _auto_change_room_count(roomDict):
    '''
    此方法和webmgr中mode1～mode4的削减标准一致
    '''
    pass


def _loadRoomDefines(gdatas):
    '''
    需要整理一个全局的 serverid-roomid-roombaseinfo的大集合
    取得server_rooms.json的配置内容, key为服务ID, value为房间配置内容
    '''
    pass


def _loadTYGames(gdatas):
    '''
    装载挂接的游戏PLUGIN, 挂接多少PLUGIN由配置: poker:global中的game_packages决定
    '''
    pass


def _initializeRooms(gdatas):
    '''
    初始化所有的房间对象
    '''
    pass


def _initializeTables(gdatas):
    '''
    初始化所有的桌子对象
    '''
    if _DEBUG:
        debug('initializeTables begin')



def _initializePoker(gdatas):
    '''
    初始化服务的基本(大厅通用)的HTTP和TCP命令入口
    '''
    if _DEBUG:
        debug('initializePoker begin')
    stype = gdata.serverType()

    # 启动全局配置系统的同步
    from poker.entity.configure import synccenter
    synccenter._initialize()
    globalEventBus.subscribe(EventHeartBeat, synccenter.doSyncData)

    from poker.entity.biz import integrate
    integrate._initialize()

    # 如果是CONN进程, 那么启动空闲TCP链接的检查
    if stype == gdata.SRV_TYPE_CONN:
        from poker.protocol.conn.protocols import doCleanUpEmptyTcp
        globalEventBus.subscribe(EventHeartBeat, doCleanUpEmptyTcp)

    # 如果是AGENT进程, 那么启用自身的命令处理器
    if stype == gdata.SRV_TYPE_AGENT:
        from poker.protocol.common.protocols import onAgentSelfCommand
        from freetime.support.tcpagent.protocol import A2SProtocol, A2AProtocol
        A2SProtocol.onCommand = onAgentSelfCommand
        A2AProtocol.onCommand = onAgentSelfCommand

    if gdata.isHttpProcess():
        from poker.protocol import runhttp
        runhttp.addWebRoot(gdata.pathWebroot())

    if stype == gdata.SRV_TYPE_UTIL:
        from poker.entity.dao import datasubscribe
        datasubscribe._initialize()

    if _DEBUG:
        debug('initializePoker end')