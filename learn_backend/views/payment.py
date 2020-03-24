#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import time
import settings
import game_config
from logics import payment


SUCCESS_RETURN = {

}


ERROR_RETURN = {

}


def pay(env):
    """
    支付接口
    :param env:
    :return:
    """
    tp = env.get_argument('type', 'apple')
    pay_method = getattr(payment, '%_pay', tp)

    result_data = {}
    if not pay_method(env, result_data):
        return 1, result_data

    return 0, result_data


def callback(env, tp=None):
    '''
    支付回调函数
    :param env:
    :param tp:
    :return:
    '''
    tp = tp or env.get_argument('tp', 'apple')
    if settings.DEBUG:
        print '=== payment_callback ===:', env.request.arguments
        path = os.path.join(settings.BASE_ROOT, 'logs', 'pay_%s_%s.txt' % (tp, time.strftime('%F-%T')))
        f = open(path, 'w')
        f.write(repr(env.request))
        f.close()

    callback_method = getattr(payment, 'callback_%s' % tp)
    rs = callback_method(env)
    # 有些平台可能需要返回动态数据（比如金山）,特殊处理下
    if not isinstance(rs, bool):
        return rs
    return SUCCESS_RETURN[tp] if rs else ERROR_RETURN[tp]