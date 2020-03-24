#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import time
import random
import game_config

from lib import utils


class Commander(object):

    def __init__(self, user):
        self.user = user