#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import json
import time
import base64
import hashlib
import game_config
import settings
import datetime
import traceback

# from M2Crypto import RSA, EVP, BIO

from lib import utils
from models.payment import Payment, MySQLConnect
from models.user import User as UserM
from logics.user import User as UserL
from lib.utils.debug import print_log


def pay_apply(user, obj, can_open_gift=True, real_price=0):
    """统一支付应用函数
    args:
        user: 用户对象
        obj: 充值数据字典对象，现统一格式
            'product_id': 商品ID,
            'scheme_id': 商品ID对应的scheme_id,
            'order_id':    定单ID
            'order_coin':  充值的金币数
            'order_money': 充值的金钱
            'order_time':  定单时间 格式为'%Y-%d-%m %H:%M:%S'
            'raw_data':   原始票据信息
        can_open_gift: 是否可以开启周卡月卡
        real_price: can_open_gift为False时的真实充值钱数
    """
    obj['old_coin'] = user.coin
    obj['level'] = user.level
    obj['user_id'] = user.uid

    # 已完成订单直接返回True
    mysql_conn = MySQLConnect(settings.PAYLOG_HOST)
    if mysql_conn.exists_order_id(obj['order_id']):
        return True
    is_360_zhichong = obj.pop('is_360_zhichong', False)     # 判断是否是360直冲

    if mysql_conn.pay(obj, user):

        # 判断是否是首充双倍活动时间段
        time_config = game_config.inreview.get(144, {})
        time_config_name = time_config.get('name', '')
        time_config_servers = time_config.get('story', '')
        if time_config_name:
            start_time, end_time = time_config_name.split(',')
            servers = time_config_servers.split(',') if time_config_servers else []
        else:
            start_time, end_time = '', ''
            servers = []
        today = time.strftime('%F')
        if start_time <= today <= end_time and (not servers or (servers and user._server_name in servers)):
            pay_list = user.active_double_pay
        else:
            pay_list = user.double_pay

        if is_360_zhichong:
            order_coin = obj['order_coin']
            product_id = obj['product_id']
            price = obj['order_money']
            user.coin += order_coin
            special_type = open_gift = 0
        else:
            product_id = obj['product_id']
            config = game_config.get_config(user._server_name, 'charge').get(product_id)
            order_coin = obj['order_coin']
            if config['is_double']:     # 首充双倍
                if product_id in pay_list:                              # 已经双倍过了
                    amount = order_coin + obj.get(('gift_coin', 0))
                else:                                                   # 双倍
                    pay_list.append(product_id)
                    amount = order_coin + order_coin + obj.get('gift_coin', 0) * 2
            else:
                amount = order_coin + obj.get('gift_coin', 0)

            special_type = open_gift = config['open_gift']
            price = obj['order_money']
            user.coin += amount
            # 当充值钱不够时，不触发周卡，月卡
            if not can_open_gift:
                open_gift = 0
                price = real_price

        # 充值基金活动增加积分
        if special_type:
            pass
        else:
            pass

        try:
            user.add_pay_award(open_gift=open_gift, price=price, product_id=product_id)
        except:
            user.add_pay_award(open_gift=open_gift, price=price)

        # 用价格 *10 计算vip经验， 因为充周卡、月卡 可能也会给钻石，但给的钻石可能不是固定的比率 10
        user.add_vip_exp(price * user.user_m.PAYMENT_RATE)
        user.save()
        return True
    else:
        return False


def apple_pay(env, result_data):
    """
    苹果支付验证
    :param env:
    :param result_data:
    :return:
    """
    from logics.platform import apple as platform_app
    from models.code import Adver

    user = env.user
    receipt_data = result_data['receipt-data'] = env.get_argument('receipt-data')

    receipt = platform_app.payment_verify(receipt_data, settings.DEBUG)
    if not receipt:
        return False

    product_id = receipt['product_id']
    # 不是本游戏的订单，返回成功，避免前端积攒过多垃圾信息
    if product_id not in game_config.charge_scheme:
        return True

    goods_id = game_config.charge_scheme[product_id]
    order_coin = game_config.charge[goods_id]['coin']
    gift_coin = game_config.charge[goods_id]['gift_coin']
    order_money = game_config.charge[goods_id]['price']
    result_data['scheme_id'] = goods_id

    obj = {
        'product_id': goods_id,
        'scheme_id': product_id,
        'order_coin': order_coin,
        'gift_coin': gift_coin,
        'order_money': order_money,
        'order_id': receipt['transaction_id'],
        'order_time': time.strftime('%F %T'),
        'raw_data': receipt['purchase_date'][:19],
        'platform': platform_app.PLATFORM_NAME,
    }

    old_coin = user.coin
    success = pay_apply(user, obj)

    # 更新游戏多用户充值记录
    new_coin = user.coin
    if success and new_coin > old_coin:
        device_mark = env.get_argument('device_mark', '')
        Adver.update_youxiduo_count(device_mark, order_money)

    return success


def qiku_pay(env, result_data):
    """
    七酷支付验证
    :param env:
    :param result_data:
    :return:
    """
    from logics.platform import qiku as platform_app

    user = env.user
    product_id = int(env.get_argument('product_id'))

    if product_id not in game_config.charge:
        return False
    charge_config = game_config.charge[product_id]
    params = {
        'openid': env.get_argument('openid', ''),
        'openkey': env.get_argument('openkey', ''),
        'pf': env.get_argument('pf', ''),
        'pfkey': env.get_argument('pfkey', ''),
        'pay_token': env.get_argument('pay_token', ''),
        'ts': int(time.time()),
        'zoneid': env.get_argument('zoneid', ''),
        'format': 'json',
        'amt': charge_config['price'] * 10,  # 平台游戏币：price  10：1
        'appid': platform_app.APP_ID,
    }

    success, receipt = platform_app.payment_verify(params, settings.DEBUG)
    result_data.update(receipt)
    if not success:
        return False

    result_data['scheme_id'] = product_id
    result_data['product_id'] = product_id

    order_coin = charge_config['coin']
    gift_coin = charge_config['gift_coin']
    order_money = charge_config['price']
    scheme_id = charge_config['cost']

    obj = {
        'product_id': product_id,
        'scheme_id': scheme_id,
        'order_coin': order_coin,
        'gift_coin': gift_coin,
        'order_money': order_money,
        'order_id': receipt['billno'],
        'order_time': time.strftime('%F %T'),
        'raw_data': '',
        'platform': platform_app.PLATFORM_NAME,
    }

    return pay_apply(user, obj)


def msdk_pay(env, result_data):
    """msdk支付验证
    """
    from logics.platform import msdk as platform_app

    user = env.user

    login_type = env.get_argument('login_type')

    product_id = int(env.get_argument('product_id'))

    charge_config = game_config.charge.get(product_id)

    if not charge_config:
        return False

    params = {
        'openid': env.get_argument('openid', ''),
        'openkey': env.get_argument('openkey', ''),
        'pay_token': env.get_argument('pay_token', ''),
        'pf': env.get_argument('pf', ''),
        'zoneid': env.get_argument('zoneid', ''),
        'amt': charge_config['price'] * 10,
        'pfkey': env.get_argument('pfkey', ''),
    }

    pay_data = platform_app.pay(login_type, params, is_sandbox=settings.DEBUG)

    if not pay_data:
        return False

    result_data.update(pay_data)
    result_data['scheme_id'] = product_id
    result_data['product_id'] = product_id

    order_coin = charge_config['coin']
    gift_coin = charge_config['gift_coin']
    order_money = charge_config['price']
    scheme_id = charge_config['cost']

    obj = {
        'product_id': product_id,
        'scheme_id': scheme_id,
        'order_coin': order_coin,
        'gift_coin': gift_coin,
        'order_money': order_money,
        'order_id': pay_data['billno'],
        'order_time': time.strftime('%F %T'),
        'raw_data': '',
        'platform': pay_data['game_platform'],
    }

    return pay_apply(user, obj)


def virtual_pay_by_admin(user, goods_id, admin=None, reason='', tp='admin'):
    """
    tp: admin 后台代充，算真实收入
        admin_test  管理员测试用
    """
    goods_id = int(goods_id)
    scheme_id = game_config.charge[goods_id]['cost']
    order_coin = game_config.charge[goods_id]['coin']
    gift_coin = game_config.charge[goods_id]['gift_coin']
    order_money = game_config.charge[goods_id]['price']
    order_id = '%s_%s_%s' % (goods_id, time.time(), utils.rand_string(3))

    obj = {
        'product_id': goods_id,
        'scheme_id': scheme_id,
        'order_coin': order_coin,
        'gift_coin': gift_coin,
        'order_money': order_money,
        'order_id': order_id,
        'order_time': time.strftime('%F %T'),
        'raw_data': 'virtual_pay_by_admin',
        'platform': tp,
        'admin': admin,
        'reason': reason,
    }

    return pay_apply(user, obj)


def callback_91(env):
    '''
    91回调
    :param env:
    :return:
    '''
    pay_status = int(env.get_argument('PayStatus', 0))
    if not pay_status:
        return False

    product_name = env.get_argument('ProductName', '')
    consume_stream_id = str(env.get_argument('ConsumeStreamId', ''))
    coo_order_serial = str(env.get_argument('CooOrderSerial', ''))
    uin = str(env.get_argument('Uin', ''))
    goods_id = str(env.get_argument('GoodsId', ''))
    goods_info = env.get_argument('GoodsInfo', '')
    goods_count = int(env.get_argument('GoodsCount', 0))
    original_money = float(env.get_argument('OriginalMoney', 0))
    order_money = float(env.get_argument('OrderMoney', 0))
    note = env.get_argument('Note', '')
    create_at = str(env.get_argument('CreateTime', ''))
    sign = str(env.get_argument('Sign', ''))

    obj = {
        '_id': coo_order_serial,
        'app_id': settings.PLATFORM_91_APP_ID,
        'act': 1,
        'product_name': product_name.encode('utf-8'),
        'consume_stream_id': consume_stream_id,
        'coo_order_serial': coo_order_serial,
        'uin': uin,
        'goods_id': goods_id,
        'goods_info': goods_info,
        'goods_count': goods_count,
        'original_money': original_money,
        'order_money': order_money,
        'note': note.encode('utf-8'),
        'pay_status': pay_status,
        'create_at': create_at,
        'app_key': settings.PLATFORM_APPKEY_91,
        'success': 1,
    }

    pre_sign = (
        "%(app_id)d"
        "%(act)d"
        "%(product_name)s"
        "%(consume_stream_id)s"
        "%(coo_order_serial)s"
        "%(uin)s"
        "%(goods_id)s"
        "%(goods_info)s"
        "%(goods_count)d"
        "%(original_money).2f"
        "%(order_money).2f"
        "%(note)s"
        "%(pay_status)d"
        "%(create_at)s"
        "%(app_key)s"
    ) % obj

    new_sign = hashlib.md5(pre_sign).hexdigest()
    if new_sign != sign:
        return False

    goods_id = int(goods_id)
    charge_config = game_config.charge(goods_id)
    order_coin = charge_config['coin']
    gift_coin = charge_config['gift_coin']
    order_money = charge_config['price']
    scheme_id = charge_config['cost']

    amount = original_money
    can_open_gift = True            # 标识是否可以开启周卡月卡活动
    if amount < order_money:
        can_open_gift = False
        if amount < 100:
            order_coin = int(amount * 11)
            gift_coin = 0
        else:
            order_coin = int(amount * 11.5)
            gift_coin = 0
    elif amount > order_money:
        over_money = amount - order_money
        if amount < 100:
            gift_coin += int(over_money * 11)
        else:
            gift_coin += int(over_money * 11.5)

    obj = {
        'product_id': goods_id,
        'scheme_id': scheme_id,
        'order_coin': order_coin,
        'gift_coin': gift_coin,
        'order_money': int(amount),
        'order_id': consume_stream_id,
        'order_time': time.strftime('%F %T'),
        'raw_data': '',
        'platform': '91',
        'uin': uin,
    }

    user_id, server_id = note.split(',')
    um = UserM.get(user_id, server_id)
    user = UserL(um.uid, um)

    return pay_apply(user, obj, can_open_gift, real_price=int(amount))