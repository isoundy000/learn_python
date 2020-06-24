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