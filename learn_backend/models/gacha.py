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
            'gacha_box_log': {},
            'today_used': {},
            'yestaday_used': {},
            'last_day': '',
            'gacha_score_day': '',
            'gacha_score': 0,
            'gacha_score_gift': [],
            'loot_log': {2300: 0, 2500: 0, 4600: 0},  # 掉落记录    默认写死3张卡 僵尸奥兹/德古拉伯爵/拔刀斋

        }
        self.gacha_score_rank_key = None
        self.today = time.strftime('%Y-%m-%d')
        super(Gacha, self).__init__(self.uid)



class RewardGacha(ModelBase):
    """限时gacha
    """

    def __init__(self, uid=None):
        self.uid = uid
        self.rank_key = None
        self._attrs = {
            'refresh_at': 0,        # 活动刷新时间戳
            'reward_gacha_at': 0,   # 免费gacha时间戳
            'reward_gacha_score': 0,    # 活动得到的积分
            'version': 0,           # 配置表中版本号
        }
        super(RewardGacha, self).__init__(self.uid)