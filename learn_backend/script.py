#!/usr/bin/env python
# -*- coding:utf-8 -*-
from run import settings
from logics.share import debug_sync_change_time

import datetime
import time
import game_config

from logics.user import User
from lib.db import ModelBase
from models.user import User as um
from models.payment import *
c = um.get('h11234567').redis
import sys
uid = sys.argv[1] if len(sys.argv) > 1 else 'h11234567'
u = User.get(uid)

if settings.DEBUG:
    debug_sync_change_time()