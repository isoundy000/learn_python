# -*- encoding: utf-8 -*-
'''
Created on 2018年7月9日

@author: houguangdong
'''
import logging
import os
import sys
import time, datetime
import redis

# pool = redis.BlockingConnectionPool(retry_on_timeout=True, **{'host': '39.96.117.45', 'port': 6380, 'socket_timeout': 5,
#                                                     'db': 0, 'password': 'sanguo_passwd'})
pool = redis.BlockingConnectionPool(retry_on_timeout=True, **{'host': 'r-2ze6934bf0317b44.redis.rds.aliyuncs.com', 'port': 6379, 'socket_timeout': 5,
                                                    'db': 0, 'password': 'QiyuTest123'})
redis_cli = redis.Redis(connection_pool=pool)


# class ModelTools(object):
#     """# ModelTools: 一堆工具"""
#
#     @classmethod
#     def get_redis_client(cls):
#         return redis


def c():
    redis_cli.set('a', 'a')
    redis_cli.get('a')


class GloryWarData():
    '''
    保存分组服务器信息
    '''
    def __init__(self):
        self.GLORY_WAR_KEY_PREFIX = 'glory_war_'
        self.GLORY_WAR_PERIOD = 'glory_war_period'
        self.period_key = None
        self.key = None
        self.redis = redis_cli

    ####################################################
    def make_period_key(self):
        if self.period_key is None:
            self.period_key = self.GLORY_WAR_PERIOD
        return self.period_key

    def set_period(self, period):
        self.redis.set(self.make_period_key(), int(period))

    def get_period(self):
        value = self.redis.get(self.make_period_key())
        return value if value else 0

    ####################################################
    def make_glory_war_key(self, period, group):                            # 生成key
        if self.key is None:
            self.key = '%s%s%s' % (self.GLORY_WAR_KEY_PREFIX, period, group)
        return self.key

    def set_group_data(self, period, group, data):                          # 放数据
        self.redis.set(self.make_glory_war_key(period, group), data)

    def get_group_data(self, period, group):                                # 取数据
        return self.redis.get(self.make_glory_war_key(period, group))


class RandomPosition():
    '''
    随机战斗位置 所有区都用一个随机各种 random.randint(1, 7)
    '''
    def __init__(self, period):
        self.key = None
        self.period = period
        self.redis = redis_cli
        self.RANDOM_POSITION = 'random_position_'

    def make_key(self):
        if self.key is None:
            self.key = '%s%s' % (self.RANDOM_POSITION, self.period)
            print self.key
        return self.key

    def set_random(self, data):
        if self.get_random():                                               # 设置完了
            return
        self.redis.set(self.make_key(), data)

    def get_random(self):
        return self.redis.get(self.make_key())


def print_log_maker(frame_num):

    def print_log_embryo(*args):
        """# print: 将s打印至log_stdout
        """
        f = sys._getframe(frame_num)
        rv = (os.path.normcase(f.f_code.co_filename), f.f_code.co_name, f.f_lineno)

        logging.critical('=' * 10 + '  LOG ' + str(datetime.datetime.now()) + ' %f START  ' %time.time() + '=' * 11)
        logging.critical('=' * 8 + '  AT %s: %s: %d: ' %rv + '=' * 8)

        l = [str(i) for i in args]

        logging.critical('|| ' + ', '. join(l))

        logging.critical('=' * 35 + '  LOG END  ' + '=' * 35 + '\n\n')

    return print_log_embryo


def lianxi():
    import random
    pos_list = []
    for i in range(1, 4):
        for j in range(2 ** (i - 1)):
            print j
            pos_list.append(random.randint(1, 7))
    print pos_list
    # redis_cli.set('a', u'中文')
    # print redis_cli.get('a')
    import json
    d = json.dumps({'a': '张三', 'b': '111'}, encoding='utf-8')
    redis_cli.set('d', d)
    f = redis_cli.get('d')
    print f
    k = json.loads(f, encoding='utf-8')
    print f, k


if __name__ == '__main__':
    # a = RandomPosition(2)
    # a.set_random([7, 8, 9])
    # print a.get_random()
    # lianxi()
    c()