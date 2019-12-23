#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/12/7 12:14
import memcache

# mc = memcache.Client(['127.0.0.1:12121'])
# mc.set('k', 'v')
# print(mc.get('k'))
mc1 = memcache.Client([('10.0.0.98:12000', 1), ('127.0.0.1:12121', 2)])
mc1.set('k1', 'v1')
print(mc1.get('k1'))
# mc1.add('k2', 'k2')