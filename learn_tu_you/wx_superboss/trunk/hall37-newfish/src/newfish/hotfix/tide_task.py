#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/21

import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.entity.dao import userdata, onlinedata
from newfish.entity import config, util
import random

# rooms = gdata.rooms()
# ftlog.info('kkkkkkkkkkkkk', rooms.keys())
# [441011001, 441021001, 441031001, 441041001, 443011001, 443021001, 444021001, 444031001, 444041001, 444051001, 444111001, 444121001, 444141001, 444151001, 444991001, 445011001, 446011001]


onlineLocList = onlinedata.getOnlineLocList(10013)[0]                # 116009
room = gdata.rooms()[onlineLocList[0]]
table = room.maptable[onlineLocList[1]]
table.tideTaskSystem.taskReady(random.choice(range(1, 9)))
# ftlog.info('fffffffffffff', room.maptable.keys())
# ftlog.info('sssssssssssss', table.tideTaskSystem.usersData)


# FISH_GAMEID = 44
# bigRoomIds = gdata.gameIdBigRoomidsMap().get(FISH_GAMEID)
# ftlog.info(bigRoomIds, 'zzzzzzzzz')
# [44101, 44102, 44103, 44104, 44301, 44302, 44402, 44403, 44404,
#  44405, 44411, 44412, 44414, 44415, 44499, 44501, 44601]

# ctrlRoomIds = []
# for bigRoomId in bigRoomIds:
#     roomConf = gdata.getRoomConfigure(bigRoomId)
#     ctrlRoomIds.extend(gdata.bigRoomidsMap().get(bigRoomId, []))
# ctrlRoomIds.sort()
# ftlog.info(ctrlRoomIds, 'cccccccccccc')
# [441011000, 441021000, 441031000, 441041000, 443011000, 443021000, 444021000,
# 444031000, 444041000, 444051000, 444111000, 444121000, 444141000, 444151000,
# 444991000, 445011000, 446011000

ftlog.info('zzzzzzzzzzzzzzccccccccc', gdata.srvIdRoomIdListMap())
# {'GT0044001_999': [441011001, 441021001, 441031001, 441041001, 443011001, 443021001, 444021001, 444031001, 444041001, 444051001, 444111001, 444121001, 444141001, 444151001, 444991001, 445011001, 446011001]}
ftlog.info("roomIdDefineMap", gdata.roomIdDefineMap())


import freetime.util.log as ftlog
from freetime.core.timer import FTLoopTimer
from poker.entity.configure import gdata
def _main():
    ftlog.info('zzzzzz', gdata.serverId())                  # GT0044001_999
    ftlog.info('zzzzzz', gdata.srvIdRoomIdListMap())        # {'GT0044001_999': [441011001, 441021001, 441031001, 441041001, 443011001, 443021001, 444021001, 444031001, 444041001, 444051001, 444111001, 444121001, 444141001, 444151001, 444991001, 445011001, 446011001]}
    ftlog.info('zzzzzz', gdata.allServersMap())



import freetime.util.log as ftlog
from freetime.core.timer import FTLoopTimer
from poker.entity.configure import gdata
def _main1():
    ftlog.info('ssssss')
a = FTLoopTimer(20, -1, _main1)
a.start()
ftlog.info('cccccc', a.getTimeOut())
a.reset(30)
ftlog.info('dddddd', a.getTimeOut())



import freetime.util.log as ftlog
from poker.entity.configure import gdata
# ftlog.info('111111111111', gdata.rooms().keys())
# [441011001, 441021001, 441031001, 441041001, 443011001, 443021001, 444021001, 444031001, 444041001, 444051001, 444111001, 444121001, 444141001, 444151001, 444991001, 445011001, 446011001]
room = gdata.rooms()[444111001]
# ftlog.info('111111111111', room.maptable.keys())
# [4410410010001, 4410410010002, 4410410010003, 4410410010004, 4410410010005, 4410410010006, 4410410010007, 4410410010008, 4410410010009, 4410410010010]
table = room.maptable[4410110010001]
ftlog.info('111111111111', table.runConfig.allSuperBossGroupIds)




import freetime.util.log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config, util
from poker.entity.dao import userdata, gamedata
from newfish.entity.redis_keys import GameData, WeakData, UserData, ABTestData
def _main1():
    userId = 10002
    a = not util.isVersionLimit(userId)
    b = not util.isPurchaseLimit(userId)
    c = util.isFinishAllRedTask(userId)
    clientVersion = gamedata.getGameAttr(userId, config.FISH_GAMEID, GameData.clientVersion)
    if clientVersion in util.getReviewVersionList(userId):  # config.getPublic("reviewClientVersion", []):
        ftlog.debug('6666666666666', clientVersion, util.getReviewVersionList(userId))
    state = not util.isVersionLimit(userId) and not util.isPurchaseLimit(userId) and util.isFinishAllRedTask(userId)
    ftlog.debug(state, a, b, c, "777777777777777")


import freetime.util.log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config, util
def _main1():
    userId = 10013
    ftlog.debug(util.balanceItem(userId, 14177), '11111111111111111')
FTLoopTimer(5, 0, _main1).start()