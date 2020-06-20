#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6



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