#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/8
"""
超级boss
"""
import random
import time

from freetime.util import log as ftlog
from newfish.entity import config, util


class SuperBossFishGroup(object):
    """
    超级boss鱼阵
    """
    def __init__(self):
        self._stageCount = 0