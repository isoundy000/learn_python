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