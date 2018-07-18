# -*- encoding: utf-8 -*-
'''
Created on 2018年7月13日

@author: houguangdong
'''
import json

import redis

pool = redis.BlockingConnectionPool(retry_on_timeout=True, **{'host': '39.96.117.45', 'port': 6380, 'socket_timeout': 5,
                                                    'db': 0, 'password': 'sanguo_passwd'})
redis_cli = redis.Redis(connection_pool=pool)


class ModelTools():

    @classmethod
    def get_user_redis(cls):
        return redis_cli

    @classmethod
    def get_game_redis(cls):
        return redis_cli

    @classmethod
    def get_battle_redis(cls):
        return redis_cli

    @classmethod
    def _key_prefix(cls, channel=0, server_id=0, rid=0, syst='', num=1000000):
        '''
        生成key的前缀
        :param channel: 渠道
        :param server_id: 区服
        :param rid: 用户id
        :param syst: 玩法
        :return:
        '''
        key = ""
        flag = False
        if channel:
            key += '%s' % channel
            flag = True
        if server_id:
            key += '_%s' % server_id
            flag = True
        if rid:
            key += '_%s' % (int(server_id) * num + rid)
            flag = True
        if syst:
            key += '_%s' % syst
            flag = True
        if not flag:
            return "%s_%s" % (cls.__module__, cls.__name__)
        else:
            return "%s_%s_%s" % (cls.__module__, cls.__name__, key)

    @classmethod
    def _key_to_rid(cls, channel=0, server_id=0, rid=0, syst='', num=1000000):
        '''
        根据key返回玩家rid
        :param channel: 渠道
        :param server_id: 区服
        :param rid: 玩家rid
        :param syst: 系统
        :param num: 常量
        :return:
        '''
        new_list = cls._key_prefix(channel, server_id, rid, syst).strip('_')
        if new_list[-2].isdigit() and int(new_list[-2]) > num:
            return int(new_list[-2]) % num
        if new_list[-1].isdigit() and int(new_list[-1]) > num:
            return int(new_list[-1]) % num
        return 0

    def make_tool_key(self, special_name, channel=0, server_id=0, rid=0, syst=''):
        '''
        生成key
        :param special_name: 自定义key
        :param channel: 渠道
        :param server_id: 区服
        :param rid: 玩家rid
        :param syst: 系统
        :return:
        '''
        return self.__class__.make_key_cls(special_name, channel, server_id, rid, syst)

    @classmethod
    def make_key_cls(cls, special_name, channel=0, server_id=0, rid=0, syst=''):
        '''
        通过类方法生成key
        :param special_name: 自定义key
        :param channel: 渠道
        :param server_id: 区服
        :param rid: 玩家rid
        :param syst: 系统
        :return:
        '''
        return cls._key_prefix(channel, server_id, rid, syst) + "_%s" % str(special_name)


class RedisString(ModelTools):
    """
    对Redis String类型操作的封装
    透明Redis的处理细节，方便业务层快速处理调用
    """

    def __init__(self, db_name=None, to_pyfunc=str, encoding='utf-8'):
        if db_name == 'user':
            self.redis = ModelTools.get_user_redis()
        elif db_name == 'game':
            self.redis = ModelTools.get_game_redis()
        elif db_name == 'battle':
            self.redis = ModelTools.get_battle_redis()
        self.to_pyfunc = to_pyfunc
        self.encoding = encoding

    def init_key(self, attr_name, carrier, channel=0, server_id=0, rid=0):
        self.key = self.make_tool_key(attr_name, channel, server_id, rid, syst=carrier)

    def set(self, value):
        value = self.to_pyfunc(value)
        value = json.dumps(value, self.encoding)
        # value = json.dumps(value, encoding='utf-8')
        return self.redis.set(self.key, value)

    def get(self):
        return json.loads(self.redis.get(self.key), encoding='utf-8')

    def set_if_none(self, value):
        value = json.dumps(value, encoding='utf-8')
        return self.redis.setnx(self.key, value)