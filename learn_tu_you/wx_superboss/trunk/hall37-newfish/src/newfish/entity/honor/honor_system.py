#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6
# 新版称号系统

import json
import time

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.util import strutil
from poker.entity.dao import daobase, gamedata
from hall.entity import hallitem
from newfish.entity import config, module_tip, util, mail_system
from newfish.entity.redis_keys import GameData, UserData
from newfish.entity.config import FISH_GAMEID
from newfish.entity.event import GetAchievementTaskRewardEvent, GetHonorEvent, \
    NewbieTaskCompleteEvent, MainQuestSectionFinishEvent



def _buildUserHonorKey(userId):
    """
    称号数据存取key
    """
    return UserData.honor % (FISH_GAMEID, userId)


def getWeaponPowerAddition(honors, wpId):
    """
    获得特殊称号的武器威力加成
    """
    power = 1
    # for honorId in honors:
    #     honorConf = config.getHonorConf(honorId)
    #     if honorConf["bufferType"] == BufferType.PowerAdd:
    #         bufferInfo = honorConf["bufferInfo"]
    #         if util.getWeaponType(wpId) == bufferInfo["weaponType"]:
    #             power += bufferInfo["powerAddition"]
    return power


def getHonorList(userId, hasDesc=False, honorTypeList=None):
    """
    获取称号信息列表
    """



    return []


def getHonor(userId, honorId):
    """获得单个称号数据"""
    assert (str(honorId) in config.getHonorConf().keys())
    value = daobase.executeUserCmd(userId, "HGET", _buildUserHonorKey(userId), str(honorId))
    if value:
        return strutil.loads(value, False, True)
    return [0, 0, 0]


def _getAllHonors(userId):
    """
    获得所有称号数据
    """
    assert (isinstance(userId, int) and userId > 0)
    value = daobase.executeUserCmd(userId, "HGETALL", _buildUserHonorKey(userId))
    if value:
        honorIds = value[0::2]
        infos = [strutil.loads(info, False, True) for info in value[1::2] if info]
        return dict(zip(honorIds, infos))
    return {}


def getOwnedHonors(userId, allHonors=None):
    """
    获得已拥有称号数据
    """
    honors = {}
    allHonors = allHonors or _getAllHonors(userId)
    pass
    return honors



_inited = False


def initialize():
    global _inited
    if not _inited:
        _inited = True
        ftlog.debug("newfish honor_system initialize begin")
        from poker.entity.events.tyevent import EventUserLogin
        from newfish.game import TGFish
        TGFish.getEventBus().subscribe(GetAchievementTaskRewardEvent, _triggerAchievementTaskRewardEvent)
        TGFish.getEventBus().subscribe(NewbieTaskCompleteEvent, _triggerNewbieTaskCompleteEvent)
        TGFish.getEventBus().subscribe(EventUserLogin, _triggerUserLoginEvent)
        TGFish.getEventBus().subscribe(MainQuestSectionFinishEvent, _triggerMainQuestSectionFinishEvent)
        ftlog.debug("newfish honor_system initialize end")