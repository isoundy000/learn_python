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


class RedisHash(ModelTools):
    """
    对Redis Hash类型操作的封装
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

    def hlen(self):
        h = self.redis.hlen(self._key)
        if not h:
            return 0
        return len(h)

    def hdel(self, field):
        '''
        删除一个元素
        :param field:
        :return:
        '''
        return self.redis.hdel(self._key, field)

    def hset(self, field, value):
        '''
        设置一个元素
        :param field:
        :param value:
        :return:
        '''
        value = json.dumps(value, self.encoding)
        self.redis.hset(self._key, field, value)

    def hmset(self, multi_dict):
        '''
        设置多个元素
        :param multi_dict:
        :return:
        '''
        d = {}
        for k, v in multi_dict.iteritems():
            d[k] = json.dumps(v, self.encoding)
        self.redis.hmset(self._key, d)

    def hget(self, field):
        '''
        获取一个域的值
        :param field:
        :return:
        '''
        return json.loads(self.redis.hget(self._key, field), self.encoding)

    def hgetall(self):
        '''
        获取多个元素key和value
        :return:
        '''
        all_dict = self.redis.hgetall(self._key)
        d = {}
        for k, v in all_dict.iteritems():
            d[k] = json.dumps(v, self.encoding)
        return d

    def hincrby(self, field, value):
        value = json.dumps(value, self.encoding)
        self.redis.hincrby(self._key, field, value)

    def hvals(self):
        '''
        获取元素的值
        :return:
        '''
        all_value = self.redis.hvals(self._key)
        return [json.loads(i, self.encoding) for i in all_value]

    def delete(self):
        self.redis.delete(self._key)