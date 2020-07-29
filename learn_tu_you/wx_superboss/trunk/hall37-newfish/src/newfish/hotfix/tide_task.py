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
    ftlog.info('zzzzzz', gdata.serverId())
    ftlog.info('zzzzzz', gdata.srvIdRoomIdListMap())
    ftlog.info('zzzzzz', gdata.allServersMap())
FTLoopTimer(0, 0, _main)