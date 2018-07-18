#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'ghou'

import redis

from Config import REDIS_CONFIG

REDIS_CLIENT_DICT = {}  # 每个db都有一个pool


def make_redis_client(redis_config):
    """make_redis_client: docstring
    args:
        redis_config:    ---    arg
    returns:
        0    ---
    """
    try:
        if cmp(redis.VERSION, (2, 10, 1)) >= 0:
            pool = redis.BlockingConnectionPool(retry_on_timeout=True, **redis_config)
        else:
            pool = redis.BlockingConnectionPool(**redis_config)
    except:
        pool = redis.BlockingConnectionPool(**redis_config)
    redis_client = redis.Redis(connection_pool=pool)
    return redis_client


def get_redis_client_key(redis_config):
    """
    组装 Redis 客户端在 pool 中的 Key
    """
    return '_'.join([redis_config['host'], str(redis_config['port']), str(redis_config['db'])])


def init_client_dict():
    """# init_pool: 每个redis库一个client，放在
    args:
        :    ---    arg
    returns:
        0    ---
    """
    for redis_config in REDIS_CONFIG.itervalues():
        client_key = get_redis_client_key(redis_config)
        REDIS_CLIENT_DICT[client_key] = make_redis_client(redis_config)


def get_redis_client(redis_config):
    """
    args:
        redis_config:
                {'db': 4,
                 'host': '10.6.7.25',
                 'password': 'F8974044A778',
                 'port': 6379,
                 'socket_timeout': 5}
    """
    client_key = get_redis_client_key(redis_config)
    if client_key not in REDIS_CLIENT_DICT:
        client = make_redis_client(redis_config)
        REDIS_CLIENT_DICT[client_key] = client
    return REDIS_CLIENT_DICT[client_key]


class ModelTools(object):
    """# ModelTools: 一堆工具"""

    @classmethod
    def get_redis(cls, redis_name):
        return cls.get_redis_client(redis_name)

    @classmethod
    def get_redis_client(cls, redis_name):
        '''
        获取redis客户端
        redis_config = {'db': 4,
             'host': '10.6.7.25',
             'password': 'F8974044A778',
             'port': 6379,
             'socket_timeout': 5}
        :param redis_name:
        :return:
        '''
        redis_config = REDIS_CONFIG.get(redis_name)
        if not redis_config:
            raise ValueError, "NOT EXIST THE REDIS CONFIG"
        client_key = get_redis_client_key(redis_config)
        client = REDIS_CLIENT_DICT.get(client_key)
        if client is None:
            client = make_redis_client(redis_config)
            REDIS_CLIENT_DICT[client_key] = client
        return client

    @classmethod
    def _key_prefix(cls, channel=0, server_id=0, rid=0):
        '''
        生成key的前缀
        :param channel: 渠道
        :param server_id: 区服
        :param rid: 用户id
        :return:
        '''
        key = ""
        # flag = False
        if channel:
            key += '%s' % channel
            # flag = True
        if server_id:
            key += '_%s' % server_id
            # flag = True
        if rid:
            key += '_%s' % rid
            # flag = True
        # if not flag:
        #     return "%s_%s" % (cls.__module__, cls.__name__)
        # else:
        #     return "%s_%s_%s" % (cls.__module__, cls.__name__, key)
        return key

    @classmethod
    def _key_to_rid(cls, key):
        '''
        根据key返回玩家rid
        :param channel: 渠道
        :param server_id: 区服
        :param rid: 玩家rid
        :return:
        '''
        new_list = key.strip('_')
        if new_list[-3].isdigit() and int(new_list[-3]) > 0:
            return int(new_list[-3])
        return 0

    def make_tool_key(self, special_name, syst, channel=0, server_id=0, rid=0):
        '''
        生成key
        :param special_name: 自定义key
        :param syst: 系统
        :param channel: 渠道
        :param server_id: 区服
        :param rid: 玩家rid
        :return:
        '''
        return self.__class__.make_key_cls(special_name, syst, channel, server_id, rid)

    @classmethod
    def make_key_cls(cls, special_name, syst, channel=0, server_id=0, rid=0):
        '''
        通过类方法生成key
        :param special_name: 自定义key
        :param syst: 系统
        :param channel: 渠道
        :param server_id: 区服
        :param rid: 玩家rid
        :return:
        '''
        return cls._key_prefix(channel, server_id, rid) + "_%s_%s" % (str(syst), str(special_name))