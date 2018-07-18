#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'ghou'

try:
    import ujson as json
except ImportError:
    try:
        import json
    except ImportError:
        import simplejson as json

from RedisBase import ModelTools


class RedisSet(ModelTools):
    """
    对Redis Set类型操作的封装
    透明Redis的处理细节，方便业务层快速处理调用
    """

    def __init__(self, db_name=None, encoding='utf-8'):
        if db_name.upper() == 'USER':
            self.redis = ModelTools.get_redis(db_name.upper())
        elif db_name.upper() == 'GAME':
            self.redis = ModelTools.get_redis(db_name.upper())
        elif db_name.upper() == 'BATTLE':
            self.redis = ModelTools.get_redis(db_name.upper())
        else:
            self.redis = ModelTools.get_redis(db_name.upper())
        self.encoding = encoding
        self._key = None

    def init_key(self, key_name, syst, channel=0, server_id=0, rid=0):
        '''
        初始化key
        :param key_name:
        :param syst:
        :param channel:
        :param server_id:
        :param rid:
        :return:
        '''
        self._key = self.make_tool_key(key_name, syst, channel, server_id, rid)
        return self._key

    def sadd(self, value):
        '''
        添加元素
        :param value:
        :return:
        '''
        value = json.dumps(value)
        self.redis.sadd(self._key, value)

    def scard(self):
        '''
        元素个数
        :return:
        '''
        return self.redis.scard(self._key)

    def smembers(self):
        '''
        获取所有的元素
        :return:
        '''
        new_list = []
        data = self.redis.smembers(self._key)
        for v in data:
            new_list.append(json.loads(v, self.encoding))
        return new_list