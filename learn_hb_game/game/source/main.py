#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'ghou'

import sys
from Source.TaskQueue.TaskResponseQueueDispath import *
from Source.WorkPool.Common.WorkPoolManager import *
from Source.WorkPool.Common.WorkPoolFunctions import *
from Source.Net.TcpServerManager import *
from Source.Net.UserSocket.UserSocketAccept import *
from Source.AccServer.AccServerConnection import *
from Source.AccServer.AccServerConnection2 import *
from Source.Timer.Common.TimerManager import *
from Source.GameData.GameDataManager import *
from Source.GameData import GameData
from Source.WSGI.URLRoute import *
from Source.ExtServer.ExtServerConnection import *
from Source.WorldWarServer.WorldWarServerConnection import WorldWarServerConnection
# complete  userproxy 中 辅助结构 _change 更改为不重复update（由list=>dict）
# complete  usermanager中针对每一个用户加锁
from Source.GameConfig.GameConfigManager2 import GameConfigManager
from Source.TaskQueue.TaskRequestQueueManager import TaskRequestQueueManager
from Source.TaskQueue.TaskResponseQueueManager import TaskResponseQueueManager


if __name__ == '__main__':
    # 1.读取运行配置
    config_file = "config.xml"
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    # 1.读取运行配置
    ConfigManager.Create(config_file)
    appConfig = ConfigManager.Singleton()
    GameData.ACC_ID = appConfig["Server"]["Info"]["Acc"]
    GameData.ACC_CODE = appConfig["Server"]["Info"]["AccCode"]
    GameData.Game_ID = appConfig["Server"]["Info"]["ID"]
    if "AccMode" in appConfig["Server"]["Info"]:
        GameData.gAccMode = int(appConfig["Server"]["Info"]["AccMode"])
    if "MergeMode" in appConfig["Server"]["Info"]:
        GameData.i_Game_Merge_Mode = int(appConfig["Server"]["Info"]["MergeMode"])
    print 1
    Log.Init()
    print 2
    Log.Write(ConfigManager.Singleton())
    Log.Write("AccMode", GameData.gAccMode)
    # 2.初始化环境
    Log.Write("[GameMain]Start!!!!!!!!!")
    if not DBEngine.Init():
        Log.Write("[Error]Database Init Error")
        exit(1)
    # 3.预加载配置数据
    # 迁移到确认配置分区执行
    if not GameConfigManager.Init():    # 游戏业务配置数据
        Log.Write("[Error]GameConfig Init Error")
        exit(1)

    if not GameDataManager.Init2():
        Log.Write("[Error]GameDataManager Init Error")
        exit(1)

    # 4.初始化全局数据结构
    if not TaskRequestQueueManager.Init():
        Log.Write("[Error]TaskRequestQueue Init Error")
        exit(1)

    if not TaskResponseQueueManager.Init():
        Log.Write("[Error]TaskResponseQueueManager Init Error")
        exit(1)

    if not WorkPoolManager.Init():      # 处理池
        Log.Write("[Error]WorkPoolManager")
        exit(1)

    WorkPoolManager.Start(WorkPoolFunctions.Excute)

    if not TaskResponseQueueDispath.Start():        # 结果派发


