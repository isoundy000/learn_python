#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import time
import datetime
import random
import settings
import cPickle as pickle
from gzip import zlib
import game_config
from lib.utils import weight_choice
from lib.db import ModelBase
from models.fake import robot


class Arena(ModelBase):

    pass