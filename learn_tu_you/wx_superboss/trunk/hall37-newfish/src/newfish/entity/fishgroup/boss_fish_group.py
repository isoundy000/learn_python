#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/1

import random
import time

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config


class BossFishGroup(object):
    """
    boss鱼群
    """
    def __init__(self, table):
        self.table = table
        pass