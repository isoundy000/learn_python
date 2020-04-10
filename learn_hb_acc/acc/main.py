#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# from Source.GameConfig.GameConfigManager import *
import sys
from Source.Config.ConfigManager import ConfigManager
from Source.Log.Write import Log
from Source.DataBase.Common.DBEngine import DBEngine
from Source.GameData import SystemParams
from Source.GameConfig.GameConfigManager2 import GameConfigManager
from Source.GameResource.GameResourceManager2 import GameResourceManager


if __name__ == '__main__':
    # 1.读取运行配置
    config_file = "config.xml"
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    # 1.读取运行配置
    ConfigManager.Create(config_file)
    appConfig = ConfigManager.Singleton()
    Log.Init()
    Log.Write(ConfigManager.Singleton())
    # 2.初始化环境
    if not DBEngine.Init():
        Log.Write("[Error]Database Init Error")
        exit(1)

    SystemParams.Init()     # 重新获取更新白名单|更新版本号|前端的更新版本等信息

    # 3.预加载配置数据
    if not GameConfigManager.Init():
        Log.Write("[Error]GameConfig Init Error")
        exit(1)

    if not GameResourceManager.Init():
        Log.Write("[Error]GameResource Init Error")
        exit(1)

