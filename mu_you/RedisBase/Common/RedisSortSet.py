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
from Tool import round_float_or_str, generate_rank_score, get_before_monday_date


class RedisSortSet(ModelTools):
    """
    对Redis Sort Set类型操作的封装
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

    def zadd(self, rid, score):
        """
        更新积分
        :param uid: 玩家uid
        :param num: 玩家胜利的场数
        :return:
        """
        self.redis.zadd(self._key, rid, generate_rank_score(score))

    def zincrby_score(self, rid, score):
        """
        增加积分
        :param rid: 玩家rid
        :param score: 玩家积分
        :return:
        """
        self.redis.zincrby(self._key, rid, score)

    def zcard(self):
        """
        获得数量
        :return:
        """
        return self.redis.zcard(self._key)

    def get_rank(self, rid):
        """
        获取自己排名
        :return:
        """
        rank = self.redis.zrevrank(self._key, rid)
        if rank is None:
            rank = -1
        return rank + 1

    def get_num_ranks(self, start=1, end=50, with_score=True):
        """
        获取前N名 start=1, end=50 为1到50名
        :param start:
        :param end:
        :return:
        """
        return self.redis.zrevrange(self._key, start - 1, end - 1, withscores=with_score,
                                    score_cast_func=round_float_or_str)

    def rename_rank(self):
        """
        重命名的数据
        :return:
        """
        if self.redis.exists(self._key):
            self.redis.rename(self._key, '%s_%s' % (self._key, get_before_monday_date()))

    def delete(self):
        """
        删除
        :return:
        """
        self.redis.delete(self._key)