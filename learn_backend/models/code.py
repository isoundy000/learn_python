#!/usr/bin/env python
# -*- coding:utf-8 -*-
import urllib
import time
import redis
import random
import string
import cPickle as pickle
import datetime
import settings
import game_config

from lib.db import make_redis_client
from lib.db import ModelBase
from lib.utils.debug import print_log

code_pool = list(set(string.digits + string.uppercase) - set('ILOBS0158'))


def generater_code(prefix, length=10):
    return prefix + ''.join(random.choice(code_pool) for _ in xrange(length))


class ActivationCode(object):
    """激活码库
    """
    redis = make_redis_client(settings.ACTIVATION_CODE)
    non_code_sets_name = 'non_code_sets_%s'     # 没有使用过的激活码集合
    all_code_dict_name = 'all_code_dict_%s'     # 此活动所有激活码字典
    one_code_dict_name = 'one_code_dict_%s'     # 单次生成激活码时字典
    one_code_sets_name = 'one_code_sets_%s_%s'  # 单次生成激活码时未使用集合

    @classmethod
    def get(cls, uid=None):
        return cls()

    def make_prefix(self, code_id):
        if isinstance(code_id, int):
            if code_id < 1000:
                return '%03d' % code_id
            else:
                return '%04d' % code_id
        return ''

    def split_key(self, key):
        if len(key) == 13:
            code_id, code = key[:3], key[3:]
        else:
            code_id, code = key[:4], key[4:]
        return int(code_id) if code_id.isdigit() else code_id, code

    def create_code(self, code_id, num=1000):
        """生成激活码
        args:
            code_id: 激活码活动id
            num: 生成的数量
        returns:
            生成的激活码
        """
        prefix = self.make_prefix(code_id)
        create = time.strftime('%Y-%m-%d-%H:%M:%S')
        codes = {}
        value = pickle.dumps({
            'create': create,
            'code_id': code_id,
            'used_uid': None,
        })

        config = game_config.code[code_id]
        for _ in xrange(num):
            code = generater_code(prefix)
            while code in codes:    # or self.exists(code):
                code = generater_code(prefix)
            codes[code] = value
            if config['type']:      # 一码多人用的类型只生产一个就够了
                break

        code_keys = codes.keys()
        if not config['type'] or (config['type'] and not self.redis.hgetall(self.all_code_dict_name % code_id)):
            pipe = self.redis.pipeline()
            pipe.hmset(self.all_code_dict_name % code_id, codes)
            pipe.hset(self.one_code_dict_name % code_id, create, pickle.dumps(code_keys))
            pipe.sadd(self.one_code_sets_name % (code_id, create), *code_keys)
            pipe.sadd(self.non_code_sets_name % code_id, *code_keys)
            pipe.execute()

        return code_keys

    def exists(self, key):
        code_id, _ = self.split_key(key)
        name = self.all_code_dict_name % code_id
        value = self.redis.hget(name, key)
        return pickle.loads(value) if value else None

    def get_code(self, key):
        code_id, _ = self.split_key(key)
        name = self.all_code_dict_name % code_id
        value = self.redis.hget(name, key)
        return pickle.loads(value) if value else None

    def set_code(self, key, obj):
        code_id, _ = self.split_key(key)
        all_name = self.all_code_dict_name % code_id
        non_name = self.non_code_sets_name % code_id
        one_name = self.one_code_sets_name % (code_id, obj['create'])

        pipe = self.redis.pipeline()
        if obj['used_uid']:
            pipe.srem(non_name, key)
            pipe.srem(one_name, key)
        else:
            pipe.sadd(non_name, key)
            pipe.sadd(one_name, key)
        pipe.hset(all_name, key, pickle.dumps(obj))
        pipe.execute()

    def find_keys(self, code_id, non_use=False, history=None, subhistory=None):
        if history:
            name = self.one_code_dict_name % code_id
            value = self.redis.hget(name, history)
            return pickle.loads(value)
        if subhistory:
            name = self.one_code_sets_name % (code_id, subhistory)
            return self.redis.smembers(name)
        if non_use:
            name = self.non_code_sets_name % code_id
            return self.redis.smembers(name)
        else:
            name = self.all_code_dict_name % code_id
            return self.redis.hkeys(name)

    def count(self, code_id, non_use=False, history=False, subhistory=None):
        if history:
            name = self.one_code_dict_name % code_id
            return self.redis.hlen(name)
        if subhistory:
            name = self.one_code_sets_name % (code_id, subhistory)
            return self.redis.scard(name)
        if non_use:
            name = self.non_code_sets_name % code_id
            return self.redis.scard(name)
        else:
            name = self.all_code_dict_name % code_id
            return self.redis.hlen(name)

    def find(self, code_id=None, non_use=False):
        keys = self.find_keys(code_id, non_use)
        for key in keys:
            yield key, self.get_code(key)

    def history_count(self, code_id):
        name = self.one_code_dict_name % code_id
        result = self.redis.hgetall(name)
        history = []
        for create, value in sorted(result.iteritems()):
            all_num = len(pickle.loads(value))
            non_num = self.count(code_id, subhistory=create)
            history.append({
                'code_id': code_id,
                'create': create,
                'all_num': all_num,
                'non_num': non_num,
                'use_num': all_num - non_num,
            })
        return history


class Code(ModelBase):
    """用户激活码
    """
    activation_code = ActivationCode()

    def __init__(self, uid):
        self.uid = uid
        self._attrs = {
            'codes': {},
            'old_data': {}
        }
        self.now = datetime.datetime.now()
        self.dt_str = self.now.strftime('%Y-%m-%d %H:%M:%S')
        super(Code, self).__init__(uid)

    def data_update_func_1(self):
        for k, v in self.codes.items():
            if not isinstance(v, dict):
                self.codes[k] = {
                    'dt': self.dt_str,
                    'codes': [v],
                }

    @classmethod
    def get(cls, uid, server=''):
        o = super(Code, cls).get(uid, server)
        o.refresh()
        return o

    def refresh(self):
        flag = 0
        for k, v in self.codes.items():
            last_date = datetime.datetime.strptime(v['dt'], '%Y-%m-%d %H:%M:%S')
            delta = (self.now.date() - last_date.date()).days
            refresh = game_config.code[k].get('refresh', 0)

            if refresh > 0 and delta >= refresh:
                if k not in self.old_data:
                    self.old_data[k] = []
                self.old_data[k].append(self.codes.pop(k))
                flag = 1
        if flag:
            self.save()

    def check_code_refresh_status(self, config_id):
        """
        return
            0 可领取
            -1 不可再次领取
            正整数： 多少天后刷新
        """
        code_config = game_config.code[config_id]
        # refresh 0: 一个人一类型领取一次， <0 ：一人一类型领取多个， >0： 一人一类型按周期重复领取
        refresh = code_config.get('refresh', 0)
        if refresh > 0:
            if config_id in self.codes:
                last_date = datetime.datetime.strptime(self.codes[config_id]['dt'], '%Y-%m-%d %H:%M:%S')
                return refresh - (self.now.date() - last_date.date()).days
            else:
                return 0
        elif refresh < 0:
            return 0
        else:
            if config_id in self.codes:
                return -1
            return 0

    def use_code(self, code, obj, save=True):
        """使用激活码，并保证使用状态
        """
        obj['used_uid'] = self.uid
        self.activation_code.set_code(code, obj)

        if obj['code_id'] not in self.codes:
            self.codes[obj['code_id']] = {'dt': self.dt_str, 'codes': []}

        self.codes[obj['code_id']]['codes'].append(code)

        if save:
            self.save()


class Adver(object):


    @classmethod
    def activate(cls, deviceid, info):
        """激活
        """
        pass


class AppStoreAdver(object):
    """ 连接点入后记录IP

    """
    redis = make_redis_client(settings.AD_CLICK)
    APP_STORE_ADVER = 'app_store_adver'

    @classmethod
    def new_data(cls):
        """ 新增数据

        :return:
        """
        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return {
            'count': 1,
            'reg_time': now_str,
            'last_time': now_str,
        }

    @classmethod
    def get_all(cls):
        pass

    @classmethod
    def set(cls, ip):
        if not cls.redis.hexists(cls.APP_STORE_ADVER, ip):
            pickle_data = pickle.dumps(cls.new_data())
            cls.redis.hset(cls.APP_STORE_ADVER, ip, pickle_data)
        else:
            pickle_data = cls.redis.hget(cls.APP_STORE_ADVER, ip)
            data = pickle.loads(pickle_data)
            data['count'] = int(data['count']) + 1
            data['last_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cls.redis.hset(cls.APP_STORE_ADVER, ip, pickle.dumps(data))