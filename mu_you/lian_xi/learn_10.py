# -*- encoding: utf-8 -*-

'''
Created on 2018年7月13日

@author: houguangdong
'''

import json
import ujson
import time


def cost_time(func):
    def inner(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        stop_time = time.time()
        print stop_time - start_time
        return result
    return inner


a = {}
for i in xrange(1, 1000000):
    a[i] = 1


@cost_time
def json_dumps(obj):
    return json.dumps(obj)


@cost_time
def ujson_dumps(obj):
    return ujson.dumps(obj)


r1 = json_dumps(a)
r2 = ujson_dumps(a)