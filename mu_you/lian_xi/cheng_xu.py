# -*- encoding: utf-8 -*-
'''
Created on 2018年7月23日

@author: houguangdong
'''

import re

a = open('../bug/changwei_result.txt', 'rw+')
dict1 = {}
for line in a.readlines():
    pattern_string = re.match('当前处理的是(\d+)区', line)
    if pattern_string:
        server = int(pattern_string.groups()[0])
        if server not in dict1:
            dict1[server] = {}
    else:
        pattern_string1 = re.match("--------------------------", line)
        if pattern_string1:
            continue
        else:
            rid, times = line.strip("\r\n").strip("))").strip(" ").split("L ")
            rid = int(rid)
            if rid not in dict1[server]:
                dict1[server][rid] = int(times)
            else:
                dict1[server][rid] += int(times)

dict2 = {}
for server, i in dict1.iteritems():
    server = int(server)
    if not i:
        continue
    dict2[server] = i

print dict2
