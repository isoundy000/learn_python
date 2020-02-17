#!/usr/bin/env python
# -*- coding:utf-8 -*-
from common.dbhelper import DBHelperObject

from handlers.gameserverhandler import query_all_server
from handlers.gameserverhandler import *


GCOUNT = 0
def PushBroadcast2():
    global GCOUNT
    server_data = query_all_server()
    merge_server = None


    GCOUNT += 5