#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import time

DEBUG = False
PLATFORM = ''       # 平台 标识: pub、ios

ADMIN_LIST = [
    '1737785826@qq.com',
]

DEFAULT_BACKEND_ADMIN = [   # 初始化后台管理员
                         ('test_admin', '1qwe32'),      # username, password
                         ]

DEFAULT_BACKEND_SUPER_ADMIN = ['they', 'giftljlj']      # 超级管理员账号，可实时获得后台添加的新功能权限
CACHE_KEY_DELAY_SECONDS = 300

from lib.utils.debug import print_log

# 所有平台标示
ENV_QIKU = 'pub_qiku'
ENV_PUB = 'cloud_android'
ENV_IOS = 'cloud_ios'
ENV_DEV_NEW = 'dev_new'
ENV_STG_QIKU = 'stg_qiku'
ENV_STG_IOS = 'stg_ios'
ENV_STG_PUB = 'stg_pub'
ENV_TEST_QIKU = 'test_qiku'
ENV_TEST_PUB = 'test_pub'
ENV_TEST_IOS = 'test_ios'

ENV_STG = [ENV_STG_QIKU, ENV_STG_PUB, ENV_STG_IOS, ENV_DEV_NEW, ENV_TEST_QIKU, ENV_TEST_PUB, ENV_TEST_IOS]

NEW_SERVER_TYPE = [1, 4]    # 新服config_type

# 91平台相关
PLATFORM_APPKEY_91 = '6b7fc05664f723d149575c239757e35a869e811929ec6e54'
PLATFORM_SERVICE_URL_91 = 'http://service.sj.91.com/usercenter/AP.aspx'
PLATFORM_91_APP_ID = 113290

BASE_ROOT = os.path.dirname(os.path.abspath(__file__)) + os.path.sep

# URL_PARTITION = 'genesis'
#
# SERVICE_NAME = 'h1'

COMPRESS_SWITCH = True      # 数据压缩开关
MIN_COMPRESS = 50           # 最小字节的压缩大小
FILTER_ADMIN_PAY = True     # 后台页面是否过滤 虚拟充值


SESSION_SWITCH = False      # session开关
SESSION_EXPIRED = 24 * 60 * 60      # session过期时间


def set_evn(env_name, server_name, *args, **kwargs):
    """# set_evn: docstring
    args:
        evn_name, server_name:    ---    arg
    returns:
        0    ---    
    """
    globals()['LANG'] = 'ch'

    env_module = __import__('env_config.%s' % env_name, globals(), locals(), [server_name])
    func = getattr(env_module, env_name)
    globals().update(func(server_name))
    init_combine_server()

    if server_name == 'master':
        config_type = 1
    else:
        config_type = int(server_name)
    globals()['CONFIG_TYPE'] = config_type
    globals()['ENV_NAME'] = env_name
    globals()['SERVICE_NAME'] = server_name

    prefix = ''
    length = 1
    for k in globals()['SERVERS']:
        if k == 'master':continue
        if prefix:
            temp = len(k[len(prefix):])
            if length < temp:
                length = temp
        else:
            for idx, i in enumerate(k):     # k = 'h1'
                if not k[idx:].isdigit():
                    prefix += i
                else:
                    temp = len(k[idx:])
                    if length < temp:
                        length = temp
    # eg: h11234567
    pattern = re.compile('^%s\d{%s,%s}$' % (prefix, 1+7, length+7)).match
    globals()['UID_PATTERN'] = pattern

    # 新服开关
    if config_type in NEW_SERVER_TYPE:
        globals()['SERVERS_OPEN'] = True
    else:
        globals()['SERVERS_OPEN'] = False

    if not globals().get('MOVE_SERVICE'):
        globals()['MOVE_SERVICE'] = {}


def init_combine_server():
    """ 添加合服列表
    """
    servers = globals()['SERVERS']
    for k in servers:
        if k == 'master':
            continue

        father_server = get_father_server(k)
        servers[father_server]['combined_servers'].append(k)


def get_combined(server_name):
    father_server_name = get_father_server(server_name)
    sc = globals()['SERVERS'][father_server_name]
    return sc.get('combined_servers', [server_name])


def get_father_server(server_name):
    """如果合服则使用父服务器（father_server）, 否则返回自己
    :param server_name:
    :return:
    """
    sc = globals()['SERVERS'][server_name]
    return server_name
    return sc.get('father_server', server_name)


def is_father_server(server_name):
    """判断是否为主服务器
    """
    return server_name == get_father_server(server_name)


def get_config_type(server_name, now=None):
    """ 获取config_type

    :param server_name:
    :return:
    """
    now = now or time.strftime("%Y-%m-%d %H:%M")

    config_type = None
    for k, v in globals()['MOVE_SERVICE'].iteritems():
        if config_type:
            break
        if now >= k and config_type is None:
            config_type = v.get(server_name)

    if config_type:
        return config_type
    else:
        return globals()['SERVERS'].get(server_name, {}).get('config_type', 1)


def get_new_server(config_type):
    '''
    1 新服 2老服 3老老服 4新区
    :param config_type:
    :return:
    '''
    if isinstance(config_type, int):
        config_type = [config_type]
    from models.config import ServerConfig
    servers = []
    sc = ServerConfig.get()
    for server, value in sc.config_value.iteritems():
        if server == "master":
            continue
        if not value['is_open']:
            continue
        if get_config_type(server) not in config_type:
            continue
        servers.append(server)
    return servers