#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/2

import random
import json
import time

import freetime.util.log as ftlog
from poker.entity.configure import gdata
from hall.entity import hallvip
from freetime.core.timer import FTLoopTimer
from poker.entity.dao import daobase, userdata
from newfish.entity import config, util
from newfish.entity.config import FISH_GAMEID



class GrandPrizePool(object):
    
    def __init__(self):
        pass
    
    
def reloadConfig(event):
    global _inited, grandPrizePoolInst
    if not _inited or not grandPrizePoolInst:
        return

    if "game:44:grandPrize:0" not in event.keylist:
        ftlog.info("GrandPrizePool, no need reload config!", event.keylist)
        return

    serverId = gdata.serverId()
    if serverId == "CT9999000001":
        if grandPrizePoolInst:
            # grandPrizePoolInst.dumpGrandPrizePool()
            grandPrizePoolInst.reloadConf()

    ftlog.info("GrandPrizePool, reloadConfig on UT9999000001", serverId)
    

_inited = False
grandPrizePoolInst = None


def initialize():
    global _inited, grandPrizePoolInst
    if not _inited:
        _inited = True
        serverId = gdata.serverId()
        if serverId == "CT9999000001":
            grandPrizePoolInst = GrandPrizePool()
            ftlog.debug("GrandPrizePool, init grandPrizePoolInst", serverId)