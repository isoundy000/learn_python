# -*- coding=utf-8 -*-
"""
上报捕鱼成本收益模块
"""
# @Author  : Kangxiaopeng
# @Time    : 2019/3/14

from poker.entity.biz import bireport
from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config
from newfish.entity.config import FISH_GAMEID


class COST_BENEFIT_TYPE:
    CBT_COST_TYPE = 0   # 消耗
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
        self.report_enable = False
        self.report_interval = 0
        self.report_count = 0
        self.update_timer = None
        self.refresh_conf()
        self.refresh_timer = FTLoopTimer(60, -1, self.refresh_conf)
        self.refresh_timer.start()

    def refresh_conf(self):
        """
        刷新配置
        """
        last_interval = self.report_interval
        last_enable = self.report_enable
        reportConf = config.getReportFishCBConf(self.table.runConfig.fishPool)
        self.report_enable = reportConf.get("enable", 0) == 1
        if not self.report_enable:
            if self.update_timer:
                self.update_timer.cancel()
                self.update_timer = None
            return
        self.report_interval = reportConf.get("interval", 60)
        self.report_count = reportConf.get("count", 50)
        if not last_enable or last_interval != self.report_interval:
            if self.update_timer:
                self.update_timer.cancel()
            self.update_timer = FTLoopTimer(self.report_interval, -1, self.update)
            self.update_timer.start()

    def clear(self):
        """
        清理时需要把缓存数据全部上报
        """
        if self.update_timer:
            self.update_timer.cancel()
        if self.refresh_timer:
            self.refresh_timer.cancel()
        self.report()

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
        添加收益
        """
        if benefit <= 0 or not self.report_enable:
            return
        self.fish_map.setdefault(f_type, [0, 0])
        self.fish_map[f_type][COST_BENEFIT_TYPE.CBT_BENEFIT_TYPE] += benefit

    def update(self):
        """
        上报成本收益
        """
        count = self.report(self.report_count)

        # interval = report_interval
        # if count == 0:
        #     interval = 2 * report_interval
        #
        # self.update_timer = FTLoopTimer(interval, 0, self.update)
        # self.update_timer.start()

    def report(self, count_limit=-1):
        """
        上报成本收益
        """
        count = 0
        for k, v in self.fish_map.iteritems():
            if v[COST_BENEFIT_TYPE.CBT_COST_TYPE] > 0 or v[COST_BENEFIT_TYPE.CBT_BENEFIT_TYPE] > 0:
                if ftlog.is_debug():
                    ftlog.debug("report, fish cost 2", "roomId =", self.room_id, "tableId =", self.table_id,
                                "fishType =", k,
                                "cost =", v[COST_BENEFIT_TYPE.CBT_COST_TYPE], "benefit =",
                                v[COST_BENEFIT_TYPE.CBT_BENEFIT_TYPE])
                count += 1
                bireport.reportGameEvent("BI_NFISH_COST_BENEFIT", config.ROBOT_MAX_USER_ID, FISH_GAMEID, self.room_id,
                                         self.table_id, int(v[COST_BENEFIT_TYPE.CBT_COST_TYPE]),
                                         int(v[COST_BENEFIT_TYPE.CBT_BENEFIT_TYPE]), 0, 0, [], config.CLIENTID_ROBOT, k)

                if ftlog.is_debug():
                    ftlog.debug("BI_NFISH_COST_BENEFIT", config.ROBOT_MAX_USER_ID, FISH_GAMEID, self.room_id,
                                self.table_id, int(v[COST_BENEFIT_TYPE.CBT_COST_TYPE]),
                                int(v[COST_BENEFIT_TYPE.CBT_BENEFIT_TYPE]), 0, 0, [], config.CLIENTID_ROBOT, k)
                self.fish_map[k] = [0, 0]

            if count >= count_limit > 0:
                ftlog.debug("report, break", count, count_limit)
                break
            if ftlog.is_debug():
                ftlog.debug("report, interval =", self.report_interval, "count =", count_limit, count, self.table_id)
        return count






