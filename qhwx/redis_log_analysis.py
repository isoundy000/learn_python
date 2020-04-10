#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


import re

api_name = re.compile('timeit view:\s+(.*):(.*\s+ms)')
# cache_key = re.compile('cache_key:\s+(.*|1\.00053)\s')
cache_key = re.compile('cache_key:\s+(.*)\s')

file = open('uwsgi.log', 'r')
lines = file.readlines()
api_cache_key_num = {}
cache_key_num = {}
for line in lines:
    m = api_name.search(line)
    if m:
        if str(m.group(1).strip()) not in api_cache_key_num:
            api_num = [{k: num} for k, num in cache_key_num.items() if num > 1]
            if api_num:
                api_cache_key_num[m.group(1).strip() + '_' + m.group(2).strip()] = api_num
                cache_key_num = {}
    else:
        m = cache_key.search(line)
        if m:
            if m.group(1) not in cache_key_num:
                cache_key_num[m.group(1).strip()] = 1
            else:
                cache_key_num[m.group(1).strip()] += 1


f = open('uwsgi.txt', 'w')
for k, v in api_cache_key_num.items():
    f.write(str(k)+'\n')
    for m in v:
        for c, n in m.items():
            f.write('\t' + str(c) + ':\t' + str(n) + '\n')
f.close()