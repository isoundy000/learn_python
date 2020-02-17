#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime
import cPickle as pickle
from hashlib import md5
from lib.db import ModelBase


class Admin(object):
    """
    管理员
    """
    _client = ModelBase.get_redis_client('admin', 'master')     # 获取一个指定的redis客户端
    ADMIN_PREFIX = 'genesis_admin_'                             # admin 存储hash表

    def __init__(self, username=None):

        self.username = username        # 管理员账号
        self.password = ""              # 管理员密码
        self.email = ""                 # 邮件
        self.last_ip = "0.0.0.0"
        self.last_login = datetime.datetime.now()
        self.is_staff = True            # 是否是雇员
        self.permissions = ""           # 管理员可用权限
        self.left_href_list = []        # 每个账户的左侧大纲条目
        self.right_links = []           # 右侧二级地址

    @classmethod
    def get(cls, username):
        # type: (object) -> object
        d = cls._client.hget(cls.ADMIN_PREFIX, username)
        if d:
            o = cls()
            o.__dict__.update(pickle.loads(d))
            return o

    @classmethod
    def get_all_user(cls):
        d = cls._client.hgetall(cls.ADMIN_PREFIX)
        return {k: pickle.loads(v) for k, v in d.iteritems()}

    def save(self):
        d = self.__dict__
        self._client.hset(self.ADMIN_PREFIX, self.username, pickle.dumps(d))

    def set_password(self, raw_password):
        "设置密码"
        # self.password = md5(raw_password).hexdigest()
        self.password = raw_password

    def check_password(self, raw_password):
        "检查密码"
        # return _check_password(raw_password, self.password)
        return self.password == raw_password



    def set_last_login(self, time, ip):
        self.last_login = time
        self.last_ip = ip