#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
注意: 不能导入game_config
"""
import time
import datetime
from lib.utils.debug import print_log


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