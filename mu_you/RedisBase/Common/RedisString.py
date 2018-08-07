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
from Tool import dict_diff


class RedisString(ModelTools):
    """
    对Redis String类型操作的封装
    透明Redis的处理细节，方便业务层快速处理调用
    """
    _need_diff = ()  # 开关，判断是否需要对数据进行对比，如果需要，则元组中的元素为需要diff的key的名字

    def __new__(cls, *args, **kwargs):
        cls._attrs_base = {
            'version': 0
        }
        return object.__new__(cls)

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
        if not self._attrs:
            pass
        else:
            self._attrs_base.update(self._attrs)
            self.__dict__.update(self._attrs_base)
        self._old_data = {}
        self._diff = {}
        super(RedisString, self).__init__()

    def save(self, key_name='', syst='', channel=0, server_id=0, rid=0):
        '''
        保存数据
        :param key_name:
        :param syst:
        :param channel:
        :param server_id:
        :param rid:
        :return:
        '''
        if not self._key:       # 是否用默认生成的key
            self.init_key(key_name, syst, channel, server_id, rid)
        r = {}
        for k in self._attrs_base:
            data = getattr(self, k)
            r[k] = data
        self.rset(r)

    def get(self, key_name='', syst='', channel=0, server_id=0, rid=0, key=None):
        """
        获得数据
        server_name = 用于指定数据库列表
        need_init : 如果数据库中没有这个数据，是否需要初始化
        """
        if key:
            _key = key
        elif self._key and not key_name and not syst:
            _key = self._key
        else:
            _key = self.make_tool_key(key_name, syst, channel, server_id, rid)
        data = self.rget(_key)
        if not data:
            return None
        for k in self._attrs_base:
            v = data.get(k)
            if v is None:
                v = self._attrs_base[k]
            setattr(self, k, v)
        return self

    def reset(self, save=True):
        self.__dict__.update(self._attrs)
        if save:
            self.save()

    def init_key(self, key_name, syst, channel=0, server_id=0, rid=0):
        self._key = self.make_tool_key(key_name, syst, channel, server_id, rid)
        return self._key

    #########################redis 底层方法##############################
    def rset(self, value):
        value = json.dumps(value, self.encoding)
        return self.redis.set(self._key, value)

    def rget(self, _key=None):
        if _key:
            value = self.redis.get(_key)
        else:
            value = self.redis.get(self._key)
        if not value:
            return None
        return json.loads(value, self.encoding)

    def rdelete(self):
        self.redis.delete(self._key)

    def set_if_none(self, value):
        value = json.dumps(value, self.encoding)
        return self.redis.setnx(self._key, value)