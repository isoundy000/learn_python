#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6
import json
from copy import deepcopy

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.entity.biz.exceptions import TYBizConfException
from poker.entity.events.tyevent import EventConfigure
from poker.entity.events import tyeventbus
from poker.entity.dao import gamedata
from poker.protocol import router
from poker.util import strutil
from newfish.entity import config
from newfish.entity.config import FISH_GAMEID
from newfish.entity.event import FishModuleTipEvent
from newfish.entity.redis_keys import GameData


class ModuleTip(object):
    """
    引导提示
    """
    def __init__(self):
        self.name = None
        self.type = None
        self.needReport = None

    def decodeFromDict(self, d):
        self.name = d.get("name")
        if not isinstance(self.name, (str, unicode)) or not self.name:
            raise TYBizConfException(d, "ModuleTip.name must be not empty string")
        self.type = d.get("type", 0)
        if not isinstance(self.type, int):
            isinstance(self.name, str)
            raise TYBizConfException(d, "ModuleTip.type must be int")

        self.needReport = d.get("needReport", 1)
        if not isinstance(self.needReport, int):
            raise TYBizConfException(d, "ModuleTip.needReport must be int")

        return self


_inited = False
_moduleTipMap = {}


def initialize():
    ftlog.debug("newfish moduletip initialize begin")
    global _inited
    if not _inited:
        _inited = True
        _reloadConf()
        from newfish.game import TGFish
        tyeventbus.globalEventBus.subscribe(EventConfigure, _onConfChanged)
        TGFish.getEventBus().subscribe(FishModuleTipEvent, handleEvent)
    ftlog.debug("newfish moduletip initialize end")


def _reloadConf():
    global _moduleTipMap
    conf = config.getGameConf("moduleTip")
    _moduleTipMap = {}
    for moduleConf in conf.get("modules", []):
        moduleTip = ModuleTip().decodeFromDict(moduleConf)
        if moduleTip.name in _moduleTipMap:
            raise TYBizConfException(moduleConf, "newfish Duplicate moduleTip %s" % (moduleTip.name))
        _moduleTipMap[moduleTip.name] = moduleTip
    _moduleTipMap = _moduleTipMap
    ftlog.debug("newfish moduletip._reloadConf successed modules=", _moduleTipMap.keys())


def _onConfChanged(event):
    """配置发生了改变"""
    if _inited and event.isChanged("game:" + str(FISH_GAMEID) + ":moduleTip:0"):
        ftlog.debug("newfish moduletip._onConfChanged")
        _reloadConf()                                   # 模块配置发生了改变
        


def handleEvent(event):
    """小红点的事件"""
    if isinstance(event, FishModuleTipEvent):
        moduleTip = findModuleTip(event.name)
        if not moduleTip:
            ftlog.error("newfish not find moduleTip:", event.name)
            return
        if event.type == 1:
            isChange = setTipValue(event.userId, moduleTip, event.value)
            pass


def addModuleTipEvent(userId, moduleName, value):
    """
    添加对应的提示信息
    """
    from newfish.game import TGFish
    tip = FishModuleTipEvent(userId, FISH_GAMEID, 1, moduleName, value)
    TGFish.getEventBus().publishEvent(tip)
    ftlog.debug("newfish addModuleTipEvent name=", moduleName, "value=", value, "userId=", userId)


def cancelModuleTipEvent(userId, moduleName, value):
    """
    取消对应的提示信息
    """
    pass


def resetModuleTipEvent(userId, moduleName):
    """
    重置提示信息
    """
    from newfish.game import TGFish
    tip = FishModuleTipEvent(userId, FISH_GAMEID, -1, moduleName, None)
    TGFish.getEventBus().publishEvent(tip)
    ftlog.debug("newfish resetModuleTipEvent name=", moduleName, "userId=", userId)


def _buildModuleTipKey(moduleTip):
    """生成模块红点的redis域"""
    return "moduletip:%s" % (moduleTip.name)


def findModuleTip(moduleName):
    global _moduleTipMap
    ftlog.debug("newfish findModuleTip modules=", _moduleTipMap.keys(), moduleName)
    return _moduleTipMap.get(moduleName)


def getTipValue(userId, moduleTip):
    """
    获取数据库的值
    """
    value = gamedata.getGameAttrJson(userId, FISH_GAMEID, _buildModuleTipKey(moduleTip),[])
    return value


def setTipValue(userId, moduleTip):
    """设置提示的值"""
    oldValues = getTipValue(userId, moduleTip)


def resetModuleTip(userId, moduleName):
    """
    删除模块tip信息中所有值
    """
    module = findModuleTip(moduleName)
    if module:
        resetTipValue(userId, module)