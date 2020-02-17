#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/12/31 16:13

import re

f = open('uwsgi.log', 'r+')
z = open('timeout.log', 'w+')
api_use_dict = {}
for line in f.readlines():
    one_line = line.strip('\n')
    if 'view: api' not in one_line:
        continue
    start_index = one_line.find('view: api.')
    end_index = one_line.rfind(' ms')
    new = one_line[start_index + len('view: api.'): end_index]
    api_time_list = new.split(":")
    api = api_time_list[0].strip()
    use_time = api_time_list[1].strip()
    if float(use_time) > 50.0:
        if api not in api_use_dict:
            api_use_dict[api] = use_time
        else:
            if use_time > api_use_dict[api]:
                api_use_dict[api] = use_time

for k, v in api_use_dict.items():
    z.write(str(k)+' -------- '+str(v)+' ms \n')
z.close()
f.close()

print len(api_use_dict), api_use_dict