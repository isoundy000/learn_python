#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""

[ O  O  O  O  #  O  O  O  O]
[ O  O  O  #  #  #  O  O  O]
[ O  O  #  #  *  #  #  O  O]
[ O  #  #  *  *  *  #  #  O]
[ #  #  *  *  9  *  *  #  #]
[ O  #  #  *  *  *  #  #  O]
[ O  O  #  #  *  #  #  O  O]
[ O  O  O  #  #  #  O  O  O]
[ O  O  O  O  #  O  O  O  O]


[ 0  ,  0  ,  0  ,  0  , -2 ,  0  ,  0  ,  0  ,  0]
[ 0  ,  0  ,  0  , -2  , -2 , -2  ,  0  ,  0  ,  0]
[ 0  ,  0  , -2  , -2  , -1 , -2  , -2  ,  0  ,  0]
[ 0  , -2  , -2  , -1  , -1 , -1  , -2  , -2  ,  0]
[-2  , -2  , -1  , -1  , (r, c) , -1  , -1  , -2  , -2]
[ 0  , -2  , -2  , -1  , -1 , -1  , -2  , -2  ,  0]
[ 0  ,  0  , -2  , -2  , -1 , -2  , -2  ,  0  ,  0]
[ 0  ,  0  ,  0  , -2  , -2 , -2  ,  0  ,  0  ,  0]
[ 0  ,  0  ,  0  ,  0  , -2 ,  0  ,  0  ,  0  ,  0]

"""

import time
import random
import copy
import gevent

from gevent.event import Event
# from gevent.coros import RLock
from gevent.lock import RLock
from gevent.local import local

import game_config

from lib import utils
from lib.utils import time_tools
from lib.utils.debug import print_log, trackback, track_upon

from logics.user import User
from logics.battle