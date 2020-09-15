# -*- coding=utf-8 -*-
"""
Created by lichen on 16/12/13.
"""

from copy import deepcopy

from freetime.entity.msg import MsgPack
from poker.protocol import router
from newfish.entity.config import FISH_GAMEID
from newfish.entity.msg import GameMsg
from newfish.entity.event import ChipChangeEvent


def changeNotify(uid, gid, attrs, broadcastUserIds=None):
    #attrs={"ud":[{},{}], "gd":[], "items":[]}
    msg = MsgPack()
    msg.setCmd("chg")
    msg.setResult("gameId", FISH_GAMEID)
    msg.setResult("userId", uid)
    if "ud" in attrs:
        ud = {}
        for item in attrs["ud"]:
            if item["name"] == "tableChip":
                from newfish.game import TGFish
                TGFish.getEventBus().publishEvent(ChipChangeEvent(uid, FISH_GAMEID, 0, item["count"]))
            ud[item["name"]] = item["count"]
        msg.setResult("ud", ud)
    if "gd" in attrs:
        gd = {}
        for item in attrs["gd"]:
            gd[item["name"]] = item["count"]
        msg.setResult("gd", gd)
    if "items" in attrs:
        items = {}
        for item in attrs["items"]:
            items[item["name"]] = item["count"]
        msg.setResult("items", items)
    if broadcastUserIds: 
        GameMsg.sendMsg(msg, broadcastUserIds)
    else:
        GameMsg.sendMsg(msg, uid)


def chargeNotify(chargeNotifyEvent):
    userId = chargeNotifyEvent.userId
    rmbs = chargeNotifyEvent.rmbs
    from poker.entity.dao import onlinedata    
    locList = onlinedata.getOnlineLocList(userId)
    for loc in locList:
        roomId = loc[0]
        tableId = loc[1]
        seatId = loc[2]
        gameId = roomId/10000000
        if gameId == FISH_GAMEID and tableId > 0 and seatId > 0:
            message = MsgPack()
            message.setCmd("table_call")
            message.setParam("action", "charge_notify")
            message.setParam("gameId", FISH_GAMEID)
            message.setParam("userId", userId)
            message.setParam("clientId", chargeNotifyEvent.clientId)
            message.setParam("roomId", roomId)
            message.setParam("tableId", tableId)
            message.setParam("seatId", seatId)
            router.sendTableServer(message, roomId)
        
    
def mergeChange(changed1, changed2):
    changed = deepcopy(changed1)
    for key in ["ud", "gd", "items"]:
        if key in changed2:
            if key not in changed:
                changed[key] = deepcopy(changed2[key])
            else:            
                for item in changed2[key]:
                    for it in changed[key]:
                        if it["name"] == item["name"]:
                            it["count"] = item["count"]
                            break
                    else:
                        changed[key].append(item)
    return changed
