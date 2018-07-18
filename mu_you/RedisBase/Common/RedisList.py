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


class RedisList(ModelTools):
    """
    对Redis List类型操作的封装
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

    def llen(self):
        '''
        获取list的元素长度
        :return:
        '''
        return self.redis.llen(self._key)

    def lpush(self, data):
        '''
        从列表首添加元素
        :param data:
        :return:
        '''
        value = json.dumps(data)
        self.redis.lpush(self._key, value)

    def rpush(self, data):
        '''
        从列表尾添加元素
        :param data:
        :return:
        '''
        value = json.dumps(data)
        self.redis.rpush(self._key, value)

    def blrpop(self, r=True, timeout=0):
        '''
        从列表中取出一个数据
        :param r: 默认从列表尾部
        :param timeout:
        :return:
        '''
        if r:
            value = self.redis.brpop(self._key, timeout)
        else:
            value = self.redis.blpop(self._key, timeout)
        if not value:
            return
        return json.loads(value, self.encoding)

    def lrpop(self, r=True):
        '''
        从列表中取出数据
        :param r: 默认从列表尾部
        :return:
        '''
        if r:
            value = self.redis.rpop(self._key)
        else:
            value = self.redis.lpop(self._key)
        return json.loads(value, self.encoding)

    def lrange(self, start=0, end=30):
        '''
        取出所有的数据
        :param start:
        :param end:
        :return:
        '''
        new_data = []
        data = self.redis.lrange(self._key, start - 1, end - 1)
        for v in data:
            new_data.append(json.loads(v, self.encoding))
        return new_data

    def delete(self):
        """
        删除
        :return:
        """
        self.redis.delete(self._key)