#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import string
import cPickle as pickle
import datetime
import random
import settings
import game_config

from lib.utils import rand_string, generate_rank_score
from lib.db import ModelBase
from lib.db import ModelTools
from models.config import ServerConfig
from lib.utils import md5

STR_SOURCE = '0123456789'       # '0123456789abcdefghijklmnopqrstuvwxyz'


def new_uid(server_name):
    """# new_uid: 生成一个新得uid
    args:
        :    ---    arg
    returns:
        0    ---
    """
    s = server_name + rand_string(7, STR_SOURCE)
    redis = User.get_redis_client('111', server_name)
    m_key = User.make_key_cls(s, server_name)

    while redis.exists(m_key):
        s = random.sample(STR_SOURCE, 7)
        s = server_name + ''.join(s)
        m_key = User.make_key_cls(s, server_name)

    return s


class UidServer(ModelTools):
    """# UidServer: 保存全服的uid和account，server对应关系
        in redis:
            {
                h1a: {
                    h1a: {
                        server: h1,
                        account: aa
                    }
                }
            }
    """
    SERVER_NAME = 'master'
    def __init__(self, uid):
        self.uid = uid
        self._attrs = {
            'server': '',
            'account': '',
        }
        super(UidServer, self).__init__()

    @classmethod
    def make_key_cls(cls, uid, server_name):
        return super(UidServer, cls).make_key_cls(uid[:3], cls.SERVER_NAME)

    def save(self):
        """# save: docstring
        args:
            :    ---    arg
        returns:
            0    ---
        """
        key = self.make_key(self.uid, self.SERVER_NAME)
        d = {}
        for k in self._attrs:
            d[k] = getattr(self, k)
        s = pickle.dumps(d)
        redis = self.get_redis_client(key, self.SERVER_NAME)
        redis.hset(key, self.uid, s)

    @classmethod
    def get(cls, uid):
        key = cls.make_key_cls(uid, cls.SERVER_NAME)
        redis = cls.get_redis_client(uid, cls.SERVER_NAME)
        s = redis.hget(key, uid)
        if s is not None:
            r = pickle.loads(s)
        else:
            r = {}
        o = cls(uid)
        o._server_name = cls.SERVER_NAME
        for k, v in o._attrs.iteritems():
            setattr(o, k, r.get(k, v))
        return o

    @classmethod
    def all_uid_server(cls,):
        pass


class UnameUid(ModelBase):
    """# UnameUid: account(user_name)->uid索引表"""
    SERVER_NAME = 'master'

    def __init__(self, uid=None):
        self.uid = uid              # uid表示user_name
        self._attrs = {
            'passwd': '',
            'servers': {},          # 参加的分服, server:uid
            'init_platform': '',    # 创建用户时候，使用的平台
            'cur_platform': '',     # 最近一次登录，使用的平台
            'current_server': '',   # 当前在玩儿的分服
            'sid': '',              # session_id
            'expired': '',          # session过期时间
        }
        super(UnameUid, self).__init__(self.uid)
        self._server_name = self.SERVER_NAME

    @classmethod
    def get(cls, uid):
        o = super(UnameUid, cls).get(uid, cls.SERVER_NAME)
        return o

    @classmethod
    def check_exist(cls, account):
        '''
        检查是否没有这个账户
        '''
        r = cls.get_redis_client('yyy', cls.SERVER_NAME)
        key = cls.make_key_cls(account, cls.SERVER_NAME)
        return r.exists(key)



class User(ModelBase):

    _attrs = {}
    _base_attrs = {
        'name': '',
        'account': '',
        'cur_platform': '',
        'role': 1,
        'is_new': 1,
        'level': 1,
        'exp': 0,
        'coin': 0,
        'silver': 0,
        'regist_time': 0,  # 注册时间戳
    }

    _attrs['is_ban'] = 0        # 封号
    _attrs['ip'] = ''           # 用户ip
    _attrs['device_mem'] = ''   # 用户内存
    _attrs['device_mark'] = ''  # mac 地址


    _attrs.update(_base_attrs)

    def __init__(self, uid=None):
        self.uid = uid
        super(User, self).__init__(uid)

        now = time.time()

        self.food_update_time = now
        self.metal_update_time = now
        self.energy_update_time = now