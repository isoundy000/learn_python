# -*- coding=utf-8 -*-
"""
Created by hhx on 17/6/20.
"""

import time
import json

from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from poker.protocol import router
from poker.entity.dao import gamedata, userdata
from newfish.entity import util
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData


class HistoryType:
    Create = 0          # 创建房间(房主)
    Unbind = 1          # 解散房间(房主)
    Win = 2             # 胜利(系统)
    Lose = 3            # 失败(系统)
    Expires = 4         # 过期(系统)
    ShutDownOwner = 5   # 系统维护(房主)
    ShutDownOther = 6   # 系统维护(参与者)
    Enter = 7           # 进入房间(参与者)
    Leave = 8           # 离开房间(参与者)
    Disband = 9         # 解散房间(参与者)


# 添加对战历史
def addOneHistory(userId, otherUserId, type, ftId, rewards=None):
    ftlog.debug("addOneHistory->", userId, otherUserId, type, rewards)
    curTime = int(time.time())
    desc = ""
    rewards = rewards or []
    otherUserId = otherUserId or 0

    # 添加对战详情到发件人发件箱
    if userId > 10000:
        otherUserName = ""
        if otherUserId:
            otherUserName = util.getNickname(otherUserId)
        # if type == HistoryType.CreatRoom:
        #     if rewards:
        #         desc = u"创建了奖励为%s的竞技房间" % (getRewardDesc(rewards))
        #     else:
        #         desc = "创建了竞技房间"
        # elif type == HistoryType.Unbind:
        #     if rewards:
        #         desc = u"解散了奖励为%s的竞技房间" % (getRewardDesc(rewards))
        #     else:
        #         desc = "解散了房间"
        # elif type == HistoryType.Win:
        #     if rewards:
        #         desc = u"在和%s(账号:%d)的竞技中获得第1名,赢了%s" % (otherUserName, otherId, getRewardDesc(rewards))
        #     else:
        #         desc = u"在和%s(账号:%d)的竞技中获得第1名" % (otherUserName, otherId)
        # elif type == HistoryType.Lose:
        #     desc = u"在和%s(账号:%d)的竞技中获得第2名" % (otherUserName, otherId)

        historyId = gamedata.incrGameAttr(userId, FISH_GAMEID, GameData.fightHistoryId, 1)
        historyInfos = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.fightHistory, [])

        historyInfos.append({"id": historyId, "userId": otherUserId, "time": curTime, "name": otherUserName,
                             "reward": rewards, "type": type, "ftId": ftId, "desc": desc})
        historyInfos = _removeHistoryExpData(historyInfos, 50)
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.fightHistory, json.dumps(historyInfos))


# 获取发件(赠送)记录
def getAllHistory(userId):
    historyInfos = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.fightHistory, [])
    tempHis = _removeHistoryExpData(historyInfos, 50)
    tempHis = tempHis[0:30]
    return tempHis


# 获取对战历史信息
def doGetAllHistorys(userId):
    message = MsgPack()
    message.setCmd("fishFightHistory")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    message.setResult("historys", getAllHistory(userId))
    router.sendToUser(message, userId)


def getRewardDesc(rewards):
    rewards = util.buildRewards(rewards)
    desc = ""
    for reward in rewards:
        desc += reward["desc"]
    return desc


# 删除发件箱过期邮件
def _removeHistoryExpData(infos, totalCount):
    ftlog.debug("_removeHistoryExpData", len(infos), totalCount)
    infos.sort(key=lambda data: (data["time"]), reverse=True)
    if len(infos) > totalCount: #最多50条
        tempMail = infos[0:(totalCount)]
        return tempMail
    else:
        return infos