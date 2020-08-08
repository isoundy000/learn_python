#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/8
# 上报捕鱼成本收益模块

from poker.entity.biz import bireport
from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config
from newfish.entity.config import FISH_GAMEID


class COST_BENEFIT_TYPE:

    CBT_COST_TYPE = 0       # 消耗
    CBT_BENEFIT_TYPE = 1    # 收益


class FishCostBenefitModule(object):
    """
    成本收益模块
    """

    def __init__(self, room_id, table_id, table):
        self.room_id = room_id
        self.table_id = table_id
        self.table = table
        self.fish_map = dict()
        self.report_enable = 0
        self.report_interval = 0
        self.report_count = 0
        self.update_timer = None
        self.refresh_conf()
        self.refresh_timer = FTLoopTimer(60, -1, self.refresh_conf)
        self.refresh_timer.start()


    def refresh_conf(self):
        pass

    def clear(self):
        pass

    def add_cost(self, f_type, cost):
        """
        添加成本
        """
        if cost <= 0 or not self.report_enable:
            return
        self.fish_map.setdefault(f_type, [0, 0])
        self.fish_map[f_type][COST_BENEFIT_TYPE.CBT_COST_TYPE] += cost

    def add_benefit(self, f_type, benefit):
        """
        添加收益 f_type: 鱼ID
        """
        if benefit <= 0 or not self.report_enable:
            return
        self.fish_map.setdefault(f_type, [0, 0])
        self.fish_map[f_type][COST_BENEFIT_TYPE.CBT_BENEFIT_TYPE] += benefit