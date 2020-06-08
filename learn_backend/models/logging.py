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

    def get_all_logging(self):
        '''
        获取一周之内玩家所有的日志记录
        :return: '2020-03-03T22:14:42.955484'   now.isoformat()[:10]    '2020-03-03'
        '''
        data = []
        now = datetime.datetime.now()
        for i in [(now - datetime.timedelta(days=i)).isoformat()[:10] for i in xrange(0, self.EXPIRE_DAY)]:
            index = self.make_key_cls('%s_%s' % (self.user.uid, i), self._server_name)
            for _key in self.redis.lrange(index, 0, -1)[::-1]:
                d = self.redis.get(_key)
                if d:
                    data.append(pickle.loads(d))
        return data

    def get_one_day_logging(self, days_str):
        """ 获取一天的日志

        :param days_str: '2016-01-26'
        :return:
        """
        data = []
        index = self.make_key_cls('%s_%s' % (self.user.uid, days_str), self._server_name)
        for _key in self.redis.lrange(index, 0, -1)[::-1]:
            d = self.redis.get(_key)
            if d:
                data.append(pickle.loads(d))
        return data

    def get_some_logging(self, days):
        """ 获得玩家最近 days(int) 天数的日志, days最大等于7 """
        if days > 7 or days <= 0 or type(days) != int:
            days = 7

        data = []
        now = datetime.datetime.now()
        # 获得格式如 "2015-03-02" 的日期列表
        date_list = [(now - datetime.timedelta(days=i)).isoformat()[:10] for \
                     i in xrange(0, days)]

        for date in date_list:
            raw_str = '%s_%s' % (self.user.uid, date)
            index = self.make_key_cls(raw_str, self._server_name)
            for _key in self.redis.lrange(index, 0, -1)[::-1]:
                value = self.redis.get(_key)
                if value:
                    data.append(pickle.loads(value))
        return data


class Step(ModelBase):
    """ 详细的用户行为记录
        用来记录用户所到的每一个阶段
    """

    def __init__(self, uid=None):
        """
            logs: {step: timestamp, step1: timestamp}
        """
        self.uid = uid
        self._attrs = {'steps': {}}
        super(Step, self).__init__(uid)

    def add_step(self, step):
        '''
        记录步骤
        :param step:
        :return:
        '''
        if step not in self.steps:
            self.steps[step] = int(time.time())
            self.save()