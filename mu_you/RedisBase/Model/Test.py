#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'ghou'


from RedisBase.Common.RedisString import RedisString


class Test(RedisString):

    def __init__(self, key_name='test', syst='2'):
        self._attrs = {
            'level1': 0,
            'level2': 0,
            'level3': 0,
            'exp': 0,
            'name': '',
            'data': {

            },
        }
        self._key = self.init_key(key_name, syst)
        super(Test, self).__init__('user')

    def see_type(self):
        '''
        返回 key 的数据类型，数据类型有：
        none (key不存在)
        string (字符串)
        list (列表)
        set (集合)
        zset (有序集)
        hash (哈希表)
        :return:
        '''
        return self.redis.type(self._key)


a = Test()
a.level1 = 5
a.name = u'张三'
a.save()
b = Test('test', '1')
print b._key
b = b.get()
print dir(b)
print b.level1
print b.level2
print b.level3
print b.exp
print b.name
print b.data