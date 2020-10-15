# -*- coding=utf-8 -*-
"""
Created by lichen on 16/12/13.
"""

from newfish.entity import util


def getChipFinal(changed):
    final = -1
    if "ud" in changed:
        for item in changed["ud"]:
            if item["name"] == "user:chip":
                final = item["count"]
                break
            
    return final


def getUserEconomicData(userId, tableId):
    """获取用户资产数据"""
    ret = {}
    ret["tableChip"] = 0
    ret["bulletChip"] = 0
    # from hall.servers.util.item_handler import ItemHelper
    # itemTabs = ItemHelper.queryUserItemTabsByGame(FISH_GAMEID, userId)
    # for tab in itemTabs:
    #     items = tab.get("items", [])
    #     for item in items:
    #         if item["kindId"]:
    #             ftlog.debug("getUserEconomicData->item:" + str(item["kindId"]))
    #             ret["item:" + str(item["kindId"])] = item["count"]
    return ret


def dumpEconomicData(userId, gainDetail, consumeDetail, roomId, tableId, clientId):
    """添加资产数据"""
    for gain in gainDetail:
        util.addItems(gain[0], gain[1], gain[2], gain[3], roomId, tableId, clientId, 1)
    for consume in consumeDetail:
        util.addItems(consume[0], consume[1], consume[2], consume[3], roomId, tableId, clientId, 1)
    return 0