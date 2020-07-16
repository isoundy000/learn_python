#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/15

import json
import hashlib

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.util import strutil
from poker.protocol.decorator import markHttpHandler, markHttpMethod
from poker.protocol import runhttp
from poker.entity.configure import gdata
from poker.entity.dao import userdata, daobase, gamedata, userchip
from poker.servers.conn.rpc import onlines
from hall.entity.hallconf import HALL_GAMEID
from hall.entity import hallvip
from hall.servers.common.base_http_checker import BaseHttpMsgChecker
from newfish.servers.util.rpc import user_rpc
from newfish.entity import config, store, util, gift_system, mail_system, weakdata
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData, WeakData, UserData


