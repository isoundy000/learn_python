#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time

import GameData

import KTime
import KTV




class GameDataManager:

    @staticmethod
    def Init():             # 依赖配置表
        pass

    @staticmethod
    def Init2():            # 不依赖配置表
        GameData.UTC_Time = int(time.time())
        GameData.UTC_Sec = GameData.UTC_Time
        KTime.Init()
        KTV.Init()
        return True

