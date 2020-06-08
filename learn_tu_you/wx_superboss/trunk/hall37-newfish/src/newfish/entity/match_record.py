#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/8

import json
import time

import freetime.util.log as ftlog
from newfish.entity import config
from poker.entity.dao import gamedata
from hall.entity import hallvip
from newfish.entity.event import MatchWinloseEvent


class MatchRecord(object):
    
    class Record(object):
        
        pass


    @classmethod
    def loadRecord(cls, gameId, userId, matchId):
        try:
            jstr = '1'
        except:
            pass