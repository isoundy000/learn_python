#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import itertools

import redis
import hashlib

import settings
from lib.utils.debug import print_log_maker
from lib.utils.debug import print_log
import cPickle as pickle

REDIS_CLIENT_DICT = {}      # 每个db都有一个pool


def make_redis_client(redis_config):
    """# make_redis_client: docstring
    args:
        redis_config:    ---    arg
    returns:
        0    ---
    """
    try:
        if cmp(redis.VERSION, (2, 10, 1)) >= 0:
            pool = redis.BlockingConnectionPool(retry_on_timeout=True, **redis_config)
        else:
            pool = redis.BlockingConnectionPool(**redis_config)
    except:
        pool = redis.BlockingConnectionPool(**redis_config)

    redis_client = redis.Redis(connection_pool=pool)

    return redis_client


def get_redis_client_key(redis_config):
    """
    组装 Redis 客户端在 pool 中的 Key
    """
    return '_'.join([redis_config['host'], str(redis_config['port']), str(redis_config['db'])])


def init_client_dict():
    """# init_pool: 每个redis库一个client，放在
    args:
        :    ---    arg
    returns:
        0    ---
    """
    for server_name, server_config in settings.SERVERS.iteritems():
        for redis_config in server_config['cache_list']:
            client_key = get_redis_client_key(redis_config)
            REDIS_CLIENT_DICT[client_key] = make_redis_client(redis_config)


# init_client_dict()


def get_redis_client(redis_config):
    """
    args:
        redis_config:
                {'db': 4,
                 'host': '10.6.7.25',
                 'password': 'F8974044A778',
                 'port': 6379,
                 'socket_timeout': 5}
    """
    client_key = get_redis_client_key(redis_config)

    if client_key not in REDIS_CLIENT_DICT:
        client = make_redis_client(redis_config)
        REDIS_CLIENT_DICT[client_key]= client

    return REDIS_CLIENT_DICT[client_key]


def dict_diff(old, new):
    """# dict_diff: 比较两个字典
    args:
        old, new:    ---    arg
    returns:
        0    ---
    """
    old_keys = set(old.keys())
    new_keys = set(new.keys())

    remove_keys = old_keys - new_keys   # 要被删除的key
    add_keys = new_keys - old_keys      # 要添加的key
    same_keys = new_keys & old_keys

    update = {}

    for k in same_keys:
        new_data = new[k]
        if old[k] != new_data:
            update[k] = new_data

    for k in add_keys:
        update[k] = new[k]

    return update, remove_keys


class ModelTools(object):
    """# ModelTools: 一堆工具"""

    @classmethod
    def print_log(cls, *args, **kargs):
        print_log_maker(2)(*args, **kargs)

    @classmethod
    def get_server_name(cls, user_id):
        x = user_id[-7:]

        if not x.isdigit():
            return user_id[:-5]

        return user_id[:-7]

    @classmethod
    def get_redis_client(cls, key, server_name):
        """# get_redis_client: 获得一个redis客户端
        args:
            key, server_name:    ---    arg
        returns:
            0    ---
        """
        cache_list = settings.SERVERS[server_name]['cache_list']
        sid = int(hashlib.md5(str(key)).hexdigest(), 16) % len(cache_list)
        cache_config = cache_list[sid]

        client_key = get_redis_client_key(cache_config)
        client = REDIS_CLIENT_DICT.get(client_key)

        if client is None:
            client = make_redis_client(cache_config)
            REDIS_CLIENT_DICT[client_key] = client

        return client

    @classmethod
    def _key_prefix(cls, server_name=''):
        if not server_name:
            server_name = cls.SERVER_NAME
        return "%s||%s||%s" % (cls.__module__, cls.__name__, server_name)

    @classmethod
    def _key_to_uid(cls, _key, server_name=''):
        return _key.replace(cls._key_prefix(server_name) + '||', '')

    def make_key(self, uid='', server_name=''):
        """# make_key: docstring
        args:
            :    ---    arg
        returns:
            0    ---
        """
        if not uid:
            uid = self.uid

        if not server_name:
            server_name = self._server_name

        if not server_name:
            server_name = self.SERVER_NAME

        return self.__class__.make_key_cls(uid, server_name)

    @classmethod
    def make_key_cls(cls, uid, server_name, special_name=''):
        if special_name:
            return cls._key_prefix(server_name) + "||%s" % str(uid) + "||%s" % str(special_name)
        return cls._key_prefix(server_name) + "||%s" % str(uid)

    @classmethod
    def run_data_version_update(cls, _key, o):
        next_dv = o._data_version__ + 1
        data_update_func = getattr(o, 'data_update_func_%d' % next_dv, None)

        while data_update_func and callable(data_update_func):
            o._data_version__ = next_dv
            data_update_func()
            if settings.DEBUG:
                print '%s.%s complate' % (_key, data_update_func.__name__)
            next_dv += 1
            data_update_func = getattr(o, 'data_update_func_%d' % next_dv, None)

    def get_father_redis(self, key=''):
        """如果合服，获取合服后的redis
        """
        if not key:
            key = self.uid
        if not getattr(self, "_server_name", None):
            self._server_name = self.get_server_name(self.uid)

        father_server_name = settings.get_father_server(self._server_name)
        return self.get_redis_client(key, father_server_name)


class ModelBase(ModelTools):
    """# TestModel: docstring"""
    SERVER_NAME = None
    _need_diff = ()         # 开关，判断是否需要对数据进行对比，如果需要，则元组中的元素为需要diff的key的名字

    def __new__(cls, *args, **kwargs):
        """# __new__: docstring
        args:
            cls, *args, **kwargs:    ---    arg
        returns:
            0    ---
        """
        cls._attrs_base = {
            '_data_version__': 0,
        }
        return object.__new__(cls)

    def __init__(self, uid=None):
        if not self._attrs:
            raise ValueError, '_attrs_base must be not empty'

        self._attrs_base.update(self._attrs)
        self.__dict__.update(self._attrs_base)
        self.uid = str(uid)
        self._model_key = None
        self._server_name = None
        self.redis = None
        self.weak_user = None
        self._old_data = {}

        self._diff = {      # 数据的变化
                            # attr_key: {
                            #     'update': {key, data},    # 新加入的和修改的数据
                            #     'remove': set(keys),      # 删除的key
                            # }
        }
        super(ModelBase, self).__init__()

    def _client_cache_update(self):
        """# _client_cache_update: 前端cache更新机制中，数据的处理方法，有些数据是需要特殊处理的
        args:
            :    ---    arg
        returns:
            0    ---
        """
        return self._diff

    @classmethod
    def _all_model_keys(cls, server_name):
        redis = cls.get_redis_client(cls.make_key_cls('-_-!!', server_name=server_name), server_name)

        return redis.keys(cls._key_prefix(server_name) + '||*')

    def save(self, uid='', server_name=''):
        """# save: docstring
        args:
            :    ---    arg
        returns:
            0    ---
        """
        _key = self._model_key

        if server_name:
            if server_name not in settings.SERVERS:
                raise KeyError('ERROR SERVER NAME: %s' % server_name)

        if not _key:
            if not server_name or self._server_name:
                server_name = self.SERVER_NAME

            if server_name not in settings.SERVERS:
                raise KeyError('ERROR SERVER NAME: %s' % server_name)

            self._server_name = server_name
            _key = self.make_key(uid, server_name)

            self.print_log('CANT FIND self._model_key, %s instead. ' % _key)

        redis = self.redis
        # pipeline = redis.pipeline(transaction=False)

        r = {}

        for k in self._attrs_base:
            data = getattr(self, k)
            r[k] = data

            if k in self._need_diff:
                old_v = self._old_data[k]
                if data != old_v:
                    if isinstance(data, dict):      # 如果是字典就dict_diff
                        update_data, remove_keys = dict_diff(old_v, data)
                    elif isinstance(data, list):    # 如果是列表就list_diff
                        update_data = data
                        remove_keys = {}
                    else:
                        update_data = data
                        remove_keys = {}
                    self._diff[k] = {
                        'update': update_data,
                        'remove': remove_keys,
                    }
                else:
                    if isinstance(data, dict):      # 如果是字典就dict_diff
                        update_data, remove_keys = dict_diff({}, data)
                    elif isinstance(data, list):    # 如果是列表就list_diff
                        update_data = data
                        remove_keys = {}
                    else:
                        update_data = data
                        remove_keys = {}
                    self._diff[k] = {
                        'update': update_data,
                        'remove': remove_keys,
                    }

        s = pickle.dumps(r, pickle.HIGHEST_PROTOCOL)
        if settings.COMPRESS_SWITCH and settings.MIN_COMPRESS > 0 and len(s) >= settings.MIN_COMPRESS:
            s = "\x01" + s.encode("zip")

        redis.set(_key, s)

        if settings.DEBUG:
            print 'model save : ', _key

    @classmethod
    def get(cls, uid, server_name='', need_init=True):
        """
        获得数据
        server_name = 用于指定数据库列表
        need_init : 如果数据库中没有这个数据，是否需要初始化
        """
        if not server_name:
            server_name = cls.SERVER_NAME

        if not server_name:
            server_name = cls.get_server_name(uid)

        if server_name not in settings.SERVERS:
            raise KeyError('ERORR SERVER NAME: %s, UID: %s' % (server_name, str(uid)))

        o = cls(uid)
        o._server_name = server_name
        o._model_key = _key = cls.make_key_cls(uid, o._server_name)
        o.redis = cls.get_redis_client(_key, o._server_name)
        o.inited = False            # 是否是初始化

        r = o.redis.get(_key)
        if not r:
            if not need_init:
                return None

            o.uid = uid
            o.inited = True
            # print '%s inited' % _key
            return o

        if r[0] == '\x01':
            decode_data = r[1:].decode("zip")
            data = pickle.loads(decode_data)
            old_data = pickle.loads(decode_data)
        else:
            data = pickle.loads(r)
            old_data = pickle.loads(r)
        for k in cls._attrs_base:
            v = data.get(k)
            if v is None:
                v = o._attrs_base[k]
                if k in cls._need_diff:
                    o._old_data[k] = v
            else:
                if k in cls._need_diff:
                    o._old_data[k] = old_data[k]

            setattr(o, k, v)

        cls.run_data_version_update(_key, o)

        if settings.DEBUG:
            print 'model get : ', _key

        return o

    def reset(self, save=True):
        """# reset: docstring 重置数据
        args:
            :    ---    arg
        returns:
            0    ---
        """
        self.__dict__.update(self._attrs)
        if save:
            self.save()

    def reload(self):
        self.__dict__.update(self.get(self.uid).__dict__)