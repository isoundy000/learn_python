#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import gevent

from lib.utils.debug import print_log

import game_config
from logics import gvg

from models.association import Association
from return_msg_config import I18nMsg


per_round_response = {
    'game_id': 1,

}