# -*- coding=utf-8 -*-
"""
Created by lichen on 17/2/22.
"""


import random

from freetime.util import log as ftlog
from newfish.entity import config


def getDropItem(dropId):
    """获取掉落的道具"""
    dropInfo = config.getDropConf(dropId)
    ftlog.debug("getDropItem", dropInfo, dropId)
    if not dropInfo:
        ftlog.error("getDropItem error dropId =", dropId)
    dropType = 0
    drops = []
    for count in xrange(dropInfo.get("randomCount", 1)):
        randInt = random.randint(1, 10000)
        for item in dropInfo.get("items", []):
            probb = item["probb"]
            if probb[0] <= randInt <= probb[1]:
                dropType = dropInfo["type"]
                dropItem = {"name": item["itemId"], "count": item["number"]}
                drops = _appendItem(drops, dropItem)
    ftlog.debug("getDropItem->", dropType, drops)
    if len(drops) == 1 and dropType != 5:
        return dropType, drops[-1]
    return dropType, drops


def _appendItem(drops, dropItem):
    """
    添加道具
    :param drops: 掉落集合
    :param dropItem: 掉落道具
    """
    ftlog.debug("_appendItem->", drops, dropItem)
    if not dropItem:
        return drops
    itemIdList = [item["name"] for item in drops if item]
    if dropItem["name"] in itemIdList:
        index = itemIdList.index(dropItem["name"])
        drop =  drops[index]
        if drop["name"] == dropItem["name"]:
            drop["count"] += dropItem["count"]
    else:
        drops.append(dropItem)
    ftlog.debug("_appendItem->", drops)
    return drops


_inited = False


def initialize():
    ftlog.info("newfish drop_system initialize begin")
    global _inited
    if not _inited:
        _inited = True
    ftlog.info("newfish drop_system initialize end")

