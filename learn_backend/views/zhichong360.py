#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
from models.user import UnameUid, User
import game_config
import urllib
import hashlib
from logics.payment import pay_apply
from logics.user import User as UserL


# 平台分配的app_id
APP_ID = '201374761'
# 平台分配的app_key
APP_KEY = '40e4a9072dddabdba9789e1587e9e2de'
# 平台分配的app_secret
APP_SECRET = 'bd2284dc782f386f7f4de10af0344551'


def user(env, *args, **kwargs):
    '''
    根据qid查询玩家信息
    :param env:
    :param args:
    :param kwargs:
    :return:
    '''
    result = {                  # 应答信息模板
        'result_code': '',      # 查询应答码，0000为成功，0001为签名错误，0002为用户不存在
        'result_msg': '',
        'record': {
            'timestamp': time.time(),
            'user_info': ''
        }
    }

    # 签名算法
    qid = env.get_argument('qid', '')
    sign = env.get_argument('sign', '')
    timestamp = env.get_argument('timestamp', '')
    sign_str = '%s#%s#%s#%s' % (APP_KEY, qid, timestamp, APP_SECRET)
    if sign != hashlib.md5(sign_str).hexdigest():
        result['result_code'] = '0001'
        result['result_msg'] = 'sign err!'
        return result


    user_info_keys = [
        'server_id',        # 区服编号
        'server_name',      # 区服名称（url编码）
        'role_name',        # 角色名称（url编码）
        'gender',           # 性别
        'last_active_time', # 最后登陆时间
        'time',             # 在线时长
        'association_name', # 帮派或阵容（url编码）
        'occupation',       # 职业
        'level',            # 角色等级
        'state',            # 角色状态，是否被禁用，0/1
        'exp',              # 经验值
        'create_time',      # 角色创建时间
    ]
    account = '%s_%s' % ('360', qid)
    if not UnameUid.check_exist(account):       # 判断该qid是否存在
        result['result_msg'] = 'qid not exist!'
        result['result_code'] = '0003'
        return result
    uu = UnameUid.get(account)
    if not uu.servers:      # 用户在所有服务器里都没有数据
        result['result_msg'] = 'no user!'
        result['result_code'] = '0002'
        return result
    user_info_list = []
    # 查询各服务器上的用户信息
    for server, uid in uu.servers.iteritems():
        result['result_msg'] = 'uid is %s' % uid        # 将uid信息放进result_msg返回，方便调使用
        user_info = {}
        user_info['server_id'] = server
        user_info['server_name'] = urllib.quote(game_config.get_server_name(server).encode('utf8'))
        u = User.get(uid)
        user_info['role_name'] = urllib.quote(u.name.encode('utf8'))
        user_info['last_active_time'] = u.active_time
        user_info['level'] = u.level
        user_info['state'] = u.is_ban
        user_info['occupation'] = u.uid
        user_info_str = '^'.join([str(user_info.get(k, '')) for k in user_info_keys])
        user_info_list.append(user_info_str)

    # 返回数据
    result['result_code'] = '0000'
    result['record']['user_info'] = '|'.join(user_info_list)

    return result


def pay(env, *args, **kwargs):
    '''
    接受充值请求，成功则返回ok，后台进行相关修改
    :param env:
    :param args:
    :param kwargs:
    :return:
    '''
    result = {                      # 应答信息模板
        'result_code': 'failed',    # 查询应答码，ok为成功，
        'result_msg': '',
        'record': {
            'timestamp': time.time(),
            'game_amount': 0,
        }
    }

    qid = env.get_argument('qid', '')
    app_key = env.get_argument('app_key', '')
    server_id = env.get_argument('server_id', '')
    order_id = env.get_argument('order_id', '')
    amount = env.get_argument('amount', '')     # 传入的amount以分为单位
    sign = env.get_argument('sign', '')

    # 验证签名
    sign_str = '%s#%s#%s#%s#%s#%s' % (amount, app_key, order_id, qid, server_id, APP_SECRET)
    if sign != hashlib.md5(sign_str).hexdigest():
        result['result_msg'] = 'sign err'
        return result

    # 获取用户uuid
    account = '%s_%s' % ('360', qid)
    if not UnameUid.check_exist(account):
        result['result_msg'] = 'user not exist!'
        return result
    um = UnameUid.get(account)
    servers = um.servers

    if server_id not in servers:
        result['result_msg'] = 'server_id not exist!'
        return result

    u = UserL.get(servers[server_id])

    pass