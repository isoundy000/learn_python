#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/21

import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.entity.dao import userdata, onlinedata
import random

room = gdata.rooms()
ftlog.info('kkkkkkkkkkkkk', room.keys())
room = gdata.rooms()[444111001]
table = room.maptable[4441110010004]
# ftlog.info(table.tideTaskSystem.taskReady(random.choice(range(1, 9))))
ftlog.info('fffffffffffff', room.maptable.keys())
ftlog.info('zzzzzzzzzzzzz', onlineLocList=onlinedata.getOnlineLocList(10013))
ftlog.info('sssssssssssss', table.tideTaskSystem.usersData)