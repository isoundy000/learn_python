#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
注意: 不能导入game_config
"""
import time
import datetime
from lib.utils.debug import print_log


def refresh_cyc(model, refresh_time_str, refresh_hour, refresh_func=None, save=False):
    """
    周期性刷新活动
    :param refresh_time:上次刷新时间
    :param refresh_hour:每天几点刷新
    :param refresh_func:刷新函数
    """
    refresh_time = getattr(model, refresh_time_str)
    cur_time = time.time()

    if not refresh_time:
        setattr(model, refresh_time_str, cur_time)
        if callable(refresh_func):
            refresh_func()
        if save:
            model.save()
        return True
    else:
        refresh_datetime = datetime.datetime.fromtimestamp(refresh_time)
        if refresh_datetime.hour >= refresh_hour:
            date4 = datetime.datetime(refresh_datetime.year,
                                      refresh_datetime.month,
                                      refresh_datetime.day,
                                      refresh_hour) + datetime.timedelta(days=1)
        else:
            date4 = datetime.datetime(refresh_datetime.year,
                                      refresh_datetime.month, refresh_datetime.day, refresh_hour)

        time4 = time.mktime(date4.timetuple())
        if refresh_time < time4 <= cur_time:
            setattr(model, refresh_time_str, cur_time)
            if callable(refresh_func):
                refresh_func()
            if save:
                model.save()

            return True

    return False


def debug_sync_change_time():
    from lib.utils import change_time
    from models.config import ChangeTime

    delta_seconds = ChangeTime.get()
    delta_seconds = int(float(delta_seconds)) if delta_seconds else 0
    real_time = int(change_time.REAL_TIME_FUNC())
    sys_time = real_time + delta_seconds
    if sys_time != int(time.time()):
        change_time.change_time(sys_time)
        print_log('debug_change_time: %s -- %s -- %s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(real_time)),
                                                         time.strftime('%Y-%m-%d %H:%M:%S'),
                                                         delta_seconds))
        return True

    return False


def cal_new_coin(old_coin, new_coin, method_param):
    """消耗钻石的特殊活动处理"""
    import game_config

    coin = old_coin - new_coin

    # 更正roulette返还钻石后的积分
    if method_param == 'roulette.open_roulette':
        roulette_config = game_config.roulette
        max_id = max(roulette_config.keys())
        coin = roulette_config[max_id]['price']
    elif method_param == 'roulette.open_roulette10':
        roulette_config = game_config.roulette
        max_id = max(roulette_config.keys())
        coin = roulette_config[max_id]['price_10']

    return coin