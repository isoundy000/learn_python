#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/11/24 23:03
# @version: 0.0.1
# @Author: houguangdong
# @File: memobject.py
# @Software: PyCharm


import sys
if sys.version[:1] == '3':
    basestring = str


class MemObject:
    '''
    memcached 关系对象
    '''

    def __init__(self, name, mc):
        '''
        @param name: str 对象的名称
        @param _lock: int 对象锁为1时表示对象被锁定无法进行修改
        @param mc:
        '''
        self._client = mc
        self._name = name
        self._lock = 0

    def produceKey(self, keyname):
        '''
        重新生成key
        :param keyname:
        :return:
        '''
        if isinstance(keyname, basestring):
            return ''.join([self._name, ':', keyname])
        else:
            raise ValueError("type error")

    def locked(self):
        '''检测对象是否被锁定'''
        key = self.produceKey('_lock')
        return self._client.get(key)

    def lock(self):
        key = self.produceKey('_lock')
        self._client.set(key, 1)

    def release(self):
        key = self.produceKey('_lock')
        self._client.set(key, 0)

    def get(self, key):
        key = self.produceKey(key)
        return self._client.get(key)

    def get_multi(self, keys):
        '''一次获取多个key的值
        @param keys: list(str) key的列表
        '''
        keynamelist = [self.produceKey(keyname) for keyname in keys]
        olddict = self._client.get_multi(keynamelist)
        newdict = dict(zip([keyname.split(':')[-1] for keyname in olddict.keys()], olddict.values()))
        return newdict

    def update(self, key, values):
        if self.locked():
            return False
        key = self.produceKey(key)
        return self._client.set(key, values)

    def update_multi(self, mapping):
        if self.locked():
            return False
        newmapping = dict(zip([self.produceKey(keyname) for keyname in mapping], mapping.values()))
        return self._client.set_multi(newmapping)

    def mdelete(self):
        '''删除memcache中的数据
        '''
        nowdict = dict(self.__dict__)
        del nowdict['_client']
        keys = nowdict.keys()
        keys = [self.produceKey(key) for key in keys]
        self._client.delete_multi(keys)

    def incr(self, key, delta):
        key = self.produceKey(key)
        return self._client.incr(key, delta)

    def insert(self):
        nowdict = dict(self.__dict__)
        del nowdict['_client']
        newmapping = dict(zip([self.produceKey(keyname) for keyname in nowdict.keys()], nowdict.values()))
        self._client.set_multi(newmapping)