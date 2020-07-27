# -*- coding=utf-8 -*-
"""
Created by lichen on 17/3/23.
"""


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
    moduleTipMap = {}
    for moduleConf in conf.get("modules", []):
        moduleTip = ModuleTip().decodeFromDict(moduleConf)
        if moduleTip.name in moduleTipMap:
            raise TYBizConfException(moduleConf, "newfish Duplicate moduleTip %s" % (moduleTip.name))
        moduleTipMap[moduleTip.name] = moduleTip
    _moduleTipMap = moduleTipMap
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
        elif event.type == 0:
            isChange = delTipValue(event.userId, moduleTip, event.value)
        else:
            isChange = resetTipValue(event.userId, moduleTip)
        if not isChange:
            ftlog.debug("handleEvent->", event.userId, event.name, event.value)
            return
        from newfish.entity import util
        level = util.getUnlockCheckLevel(event.userId)
        if event.name == "task" and level < config.getCommonValueByKey("dailyQuestOpenLevel"):
            return
        moduleNames = [event.name]
        ftlog.debug("newfish module_tip modulename=", event.name, "value =", event.value, "userId=", event.userId, event.type)
        modules = getInfo(event.userId, moduleNames)
        mo = buildInfo(modules)
        router.sendToUser(mo, event.userId)


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
    from newfish.game import TGFish
    tip = FishModuleTipEvent(userId, FISH_GAMEID, 0, moduleName, value)
    TGFish.getEventBus().publishEvent(tip)
    ftlog.debug("newfish cancelModuleTipEvent name=", moduleName, "value=", value, "userId=", userId)


def resetModuleTipEvent(userId, moduleName):
    """
    重置提示信息
    """
    from newfish.game import TGFish
    tip = FishModuleTipEvent(userId, FISH_GAMEID, -1, moduleName, None)
    TGFish.getEventBus().publishEvent(tip)
    ftlog.debug("newfish resetModuleTipEvent name=", moduleName, "userId=", userId)


def buildInfo(modules):
    """构建消息"""
    mo = MsgPack()
    mo.setCmd("module_tip")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("action", "fishUpdate")
    modulesInfo = []
    for module in modules:
        modulesInfo.append({
            "name": module.name,
            "type": module.type,
            "value": module.value,
            "needReport": module.needReport
        })
    mo.setResult("modules", modulesInfo)
    return mo


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


def setTipValue(userId, moduleTip, value):
    """设置提示的值"""
    oldValues = getTipValue(userId, moduleTip)
    values = deepcopy(oldValues)
    if isinstance(value, list):
        values.extend(list(set(value)))
        values = list(set(values))
    elif value not in values:
        values.append(value)
    gamedata.setGameAttr(userId, FISH_GAMEID, _buildModuleTipKey(moduleTip), json.dumps(values))
    return not values or oldValues != values


def delTipValue(userId, moduleTip, value):
    """删除提示红点"""
    oldValues = getTipValue(userId, moduleTip)
    values = deepcopy(oldValues)
    if isinstance(value, list):
        values = list(set(values) - set(value))
        values = list(set(values))
    elif value in values:
        values.remove(value)
    gamedata.setGameAttr(userId, FISH_GAMEID, _buildModuleTipKey(moduleTip), json.dumps(values))
    return not values or oldValues != values


def resetTipValue(userId, moduleTip):
    """充值提示红点的值"""
    gamedata.setGameAttr(userId, FISH_GAMEID, _buildModuleTipKey(moduleTip), json.dumps([]))
    return True


def getInfo(userId, moduleNames):
    """
    获取模块tip信息
    """
    if moduleNames:
        return getModulesInfo(userId, moduleNames)
    else:
        return getAllModulesInfo(userId)


def getModulesInfo(userId, moduleNames):
    """
    获取模块tip信息
    @param userId: 用户Id
    @param moduleNames: 模块名
    @return: list<ModuleTip>
    """
    from newfish.entity import util
    level = util.getUnlockCheckLevel(userId)
    modules = []
    for moduleName in moduleNames:
        m = findModuleTip(moduleName)
        if m:
            module = strutil.cloneData(m)
            if module.name == "task" and level < config.getCommonValueByKey("dailyQuestOpenLevel"):
                module.value = []
            else:
                module.value = getTipValue(userId, module)
            modules.append(module)
    return modules


def getAllModulesInfo(userId):
    """
    获取所有模块tip信息
    """
    from newfish.entity import util
    level = util.getUnlockCheckLevel(userId)
    global _moduleTipMap
    modules = []
    for _key, value in _moduleTipMap.iteritems():
        module = strutil.cloneData(value)
        if module.name == "task" and level < config.getCommonValueByKey("dailyQuestOpenLevel"):
            module.value = []
        else:
            module.value = getTipValue(userId, module)
        modules.append(module)
    return modules


def delModulesTipValue(userId, moduleNames, values):
    """
    删除模块tip信息中某个值
    @param userId: 用户Id
    @param moduleNames: 模块名
    @param values: 模块信息中的值
    """
    moduleNames = moduleNames if isinstance(moduleNames, list) else [moduleNames]
    values = values if isinstance(values, list) else [values]
    moduleValues = zip(moduleNames, values)
    for moduleValue in moduleValues:
        moduleName = moduleValue[0]
        value = moduleValue[1]
        module = findModuleTip(moduleName)
        if module:
            if value == 0:
                resetTipValue(userId, module)
            else:
                delTipValue(userId, module, value)
    return getModulesInfo(userId, moduleNames)


def resetModuleTip(userId, moduleName):
    """
    删除模块tip信息中所有值
    """
    module = findModuleTip(moduleName)
    if module:
        resetTipValue(userId, module)