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

    def clear_permissions(self):
        '''
        清理管理员可用权限
        :return:
        '''
        self.permissions = ""

    def set_permissions(self, perms):
        '''
        设置管理员可用权限
        :param perms:
        :return:
        '''
        for perm in perms:
            if perm in self.permissions.split(','):
                continue
            else:
                raw = self.get_permissions()
                raw.append(perm)
                self.permissions = ",".join(raw)

    def get_permissions(self):
        "获取全部权限列表"
        if self.permissions.strip() == "":
            return []
        else:
            return self.permissions.lstrip(',').rstrip(',').split(',')

    def has_permission(self, permission):
        "检查是否具备指定权限"
        permissions = self.get_permissions()
        if permission in permissions:
            return True
        else:
            return False

    def has_permissions(self, *perms):
        '''
        检查是否有权限列表中的权限
        :param perms:
        :return:
        '''
        if self.has_permission("super"):        # 超级用户
            return True

        # 检查是否有权限列表中的权限
        for permission in perms:
            if not self.has_permission(permission):
                return False
        return True

    def set_last_login(self, time, ip):
        '''
        设置最后登录信息
        :param time:
        :param ip:
        :return:
        '''
        self.last_login = time
        self.last_ip = ip

    # 设置左侧目录条目
    def set_left_herf(self, ids):
        self.left_href_list = ids

    # 清空已有的左侧条目
    def clear_left_herf(self):
        self.left_href_list = []

    def set_right_links(self, ids):
        '''
        设置二级菜单栏
        :param ids:
        :return:
        '''
        self.right_links = ids

    def clear_right_links(self):
        '''
        清空二级菜单栏
        :return:
        '''
        self.right_links = {}