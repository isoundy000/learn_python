#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime


def check_time(config, now=None):
    """检测激活码活动配置里这个活动是否有效
    args:
        config: 活码活动配置
        now: 对比时间，datetime.datetime对象
    returns:
        bool值，True表示有效，False表示无效
    """
    now = now or datetime.datetime.now()

    now = opentime = closetime = datetime.datetime.now()
    if config['open'] != '-1':
        opentime = datetime.datetime.strptime(config['open'], '%Y-%m-%d,%H:%M')
    if config['close'] != '-1':
        closetime = datetime.datetime.strptime(config['close'], '%Y-%m-%d,%H:%M')

    return opentime <= now <= closetime