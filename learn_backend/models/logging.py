#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time
import datetime
import cPickle as pickle

from lib.db import ModelBase


class Logging(ModelBase):

    EXPIRE_DAY = 7
    EXPIRE = 3600 * 24 * EXPIRE_DAY

    def __init__(self, user):
        self.user = user
        self._server_name = self.user.uid[:-7]
        try:
            self.redis = self.user.user_m.redis[1]
        except:
            self.redis = self.user.user_m.redis
        self.today_index = self.make_key_cls('%s_%s' % (self.user.uid, time.strftime('%F')), self._server_name)

    def save(self):
        pass

    def add_logging(self, method, args=None, data=None):
        """添加玩家动作记录
        args:
            method:
            args: 请求参数
            data: 结果
        """
        _key = self.make_key_cls('%s_%s' % (self.user.uid, time.time()), self._server_name)
        result = {'method': method, 'args': args or {}, 'data': data or {}, 'dt': time.strftime('%F %T')}
        self.redis.set(_key, pickle.dumps(result))
        self.redis.expire(_key, self.EXPIRE)

        self.redis.rpush(self.today_index, _key)
        self.redis.expire(self.today_index, self.EXPIRE)