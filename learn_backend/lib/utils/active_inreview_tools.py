#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import time
import game_config
from lib.utils.debug import print_log


def active_inreview_start_end_time(config, differ_time=0):
    """
    # 获取活动的开启和结束的时间
    :param config: 配置表 如game_config.roulette
    :return: 版本号,开始时间,结束时间
    """
    now = time.time()
    for active_id, value in config.iteritems():
        if 'start_time' not in value or 'end_time' not in value:
            return 0
        start_time = value['start_time']
        if not start_time:
            return 0
        s_time = time.strptime(start_time, '%Y/%m/%d %H:%M:%S')
        start_time_stamp = time.mktime(s_time)
        end_time = value['end_time']
        if not end_time:
            return 0
        e_time = time.strptime(end_time, '%Y/%m/%d %H:%M:%S')
        end_time_stamp = time.mktime(e_time)
        if start_time_stamp <= now - differ_time <= end_time_stamp:
            return value['version']
    return 0


def format_time_active_config_version(config, format, differ_time=0):
    """
    #获取活动的版本号
    :param config: 配置表 如game_config.roulette
    :param format: 时间的格式为%Y/%m/%d 或者 %Y-%m-%d
    :param differ_time: 活动结束几小时之后发奖, differ_time是时间差值
    :return: 版本号
    """
    now = time.time()
    for version, value in config.iteritems():
        if 'start_time' not in value or 'end_time' not in value:
            return 0
        start_time = value['start_time']
        if not start_time:
            return 0
        s_time = time.strptime(start_time, format)
        start_time_stamp = time.mktime(s_time)
        end_time = value['end_time']
        if not end_time:
            return 0
        e_time = time.strptime(end_time, format)
        end_time_stamp = time.mktime(e_time)
        if start_time_stamp <= now - differ_time <= end_time_stamp:
            return value['version']
    return 0