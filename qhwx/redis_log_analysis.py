#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


import re

api_name = re.compile('timeit view:\s+(.*):(.*)\s+ms')
cache_key = re.compile('cache_key:\s+(.*)\s')


file = open('/dddd/xxx.log', 'r')
lines = file.readlines()
api_cache_key_num = {}
for line in lines:
    pass

