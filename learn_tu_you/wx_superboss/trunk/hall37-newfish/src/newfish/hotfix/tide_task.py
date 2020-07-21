#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/21

import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.entity.dao import userdata, onlinedata
import random

# rooms = gdata.rooms()
#ftlog.info('kkkkkkkkkkkkk', rooms.keys())
onlineLocList = onlinedata.getOnlineLocList(116009)[0]
room = gdata.rooms()[onlineLocList[0]]
table = room.maptable[onlineLocList[1]]
table.tideTaskSystem.taskReady(random.choice(range(1, 9)))
#ftlog.info('fffffffffffff', room.maptable.keys())
#ftlog.info('sssssssssssss', table.tideTaskSystem.usersData)