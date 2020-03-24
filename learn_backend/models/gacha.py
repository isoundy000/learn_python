#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from lib.utils.active_inreview_tools import active_inreview_start_end_time, format_time_active_config_version
from lib.utils.debug import print_log

from lib.db import ModelBase
import time
import game_config
import datetime
from models.notify import Notify
import settings
from lib.utils import generate_rank_score, round_float_or_str
from return_msg_config import i18n_msg


class Gacha(ModelBase):

    def __init__(self, uid=None):
        self.uid = uid
        self.base_point = 1000
        self._attrs = {
            'gacha': {

            },
            'loot_log': {2300: 0, 2500: 0, 4600: 0},  # 掉落记录    默认写死3张卡 僵尸奥兹/德古拉伯爵/拔刀斋
        }
        self.gacha_score_rank_key = None
        self.today = time.strftime('%Y-%m-%d')
        super(Gacha, self).__init__(self.uid)