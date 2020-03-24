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
    """各种广告积分墙

       deviceid: idfa 或者 mac
       所有deviceid 都统一转成大写并去除分号，解决各个平台 mac地址 格式不统一的问题
    """
    redis = make_redis_client(settings.AD_CLICK)
    ad_name = 'fuck_all_ad'                                 # 所有激活的设备   单次生成激活码时未使用集合
    activate_count_name = 'all_ad_activate_count'           # 所有平台的激活数
    adclick_count_name = 'all_ad_click_count'               # 所有平台的广告点击数
    youxiduo_count_name = 'youxiduo_count_name'


    @classmethod
    def get(cls, deviceid):
        """
        return:
        {
            'ts': 0,
            'source': 'yijifen',                            # 广告平台来源
            'callback': 'http://www.baidu.com',             # 回调地址
            'deviceid': '0C74C2E9F2D0'                      # 设备标识
            'idfa': '99AD5E51-1164-47E4-BF0F-69646AE8F5B6', # 设备标识
            'mac': '0C74C2E9F2D0',                          # mac
            'activate': False,                              # 是否激活
        }
        """
        deviceid = deviceid.replace(':', '').upper()
        info = cls.redis.hget(cls.ad_name, deviceid)
        return eval(info) if info else {}

    @classmethod
    def update(cls, deviceid, info, force=False):
        if not deviceid:
            return
        deviceid = deviceid.replace(':', '').upper()
        if force or not cls.redis.hexists(cls.ad_name, deviceid):
            cls.redis.hset(cls.ad_name, deviceid, info)
            # 按source 或者 回调地址url 记录广告点击数
            path, query = urllib.splitquery(info['callback'])
            key = '%(path)s||%(date)s' % {'path': info['source'] or path, 'date': time.strftime('%F-%H')}
            cls.redis.hincrby(cls.adclick_count_name, key)

    @classmethod
    def activate(cls, deviceid, info):
        """激活
        """
        deviceid = deviceid.replace(':', '').upper()
        if info['activate']:
            if info['source'] == 'youxiduo':
                if not info.get('active_count'):
                    info['active_count'] = info.get('active_count', 0) + 1
                    cls.redis.hset(cls.ad_name, deviceid, info)
                    cls.incr_youxiduo_count()
            else:
                cls.redis.hset(cls.ad_name, deviceid, info)
                # 按source 或者 回调地址url 记录激活数
                path, query = urllib.splitquery(info['callback'])
                key = '%(path)s||%(date)s' % {'path': info['source'] or path, 'date': time.strftime('%F-%H')}
                cls.redis.hincrby(cls.activate_count_name, key)

    @classmethod
    def watch_activate_count(cls):
        """
        return:
             [('waps||2014-06-12', '1'),
             ('limei||2014-06-12', '1'),
             ('waps||2014-06-11', '2')]
        """
        d = {}
        activate_counts = cls.redis.hgetall(cls.activate_count_name)
        click_counts = cls.redis.hgetall(cls.adclick_count_name)
        for k, v in activate_counts.iteritems():
            d[k] = '%(activate_count)s/%(click_count)s' % {'activate_count': v, 'click_count': click_counts.get(k, 0)}
        return sorted(d.iteritems(), key=lambda x: x(x[0].split('||'), x[1]), reverse=1)

    @classmethod
    def incr_youxiduo_count(cls):
        """记录每日激活数
        data = {
            'active_count': 激活数
            'order_count': 订单数
            'order_amount': 流水数
        }
        """
        key = '%s' % time.strftime('%F')
        data = cls.redis.hget(cls.youxiduo_count_name, key)
        data = eval(data) if data else {'order_count': 0, 'order_amount': 0, 'active_count': 0}
        data['active_count'] += 1
        cls.redis.hset(cls.youxiduo_count_name, key, data)

    @classmethod
    def update_youxiduo_count(cls, deviceid, amount):
        """记录对应的充值数据， 每日一统计
        data = {
            'active_count': 激活数
            'order_count': 订单数
            'order_amount': 流水数
        }
        """
        info = cls.get(deviceid)
        try:
            if info and info['source'] == 'youxiduo':
                key = time.strftime('%F')
                data = cls.redis.hget(cls.youxiduo_count_name, key)
                data = eval(data) if data else {'order_count': 0, 'order_amount': 0, 'active_count': 0}
                data['order_count'] += 1
                data['order_amount'] += amount
                cls.redis.hset(cls.youxiduo_count_name, key, data)
        except:
            pass

    @classmethod
    def query_youxiduo_count(cls):
        """查询游戏多激活，订单，流水数
        """
        return cls.redis.hgetall(cls.youxiduo_count_name)


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
        data = cls.redis.hgetall(cls.APP_STORE_ADVER)
        if not data:
            return {}
        result = {}
        for ip, value in data.iteritems():
            result[ip] = pickle.loads(value)
        return result

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