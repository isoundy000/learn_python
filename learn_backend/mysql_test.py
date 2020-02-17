#!/usr/bin/env python
# -*- coding:utf-8 -*-

import settings
settings.set_evn('dev_new', 'h1')

from models.payment import payment_insert

d = {
    'admin': 'default',
    'gift_coin': 6,
    'level': 99,
    'old_coin': 3090,
    'order_coin': 60,
    'order_id': '1_1397051527.07_ypj',
    'order_money': 6,
    'order_time': '2014-04-09 21:52:07',
    'platform': 'admin',
    'product_id': 1,
    'raw_data': 'virtual_pay_by_admin',
    'reason': u'\u4ee3\u5145',
    'scheme_id': 'zombiecoinTier1',
    'user_id': u'test'
}


payment_insert(d['order_id'], d)