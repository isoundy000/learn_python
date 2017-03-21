# -*- encoding: utf-8 -*-
'''
Created on 2017年2月27日

@author: houguangdong
'''

a = [{1:1}, {2:2}, {3:3}, {4:4}, {5:5}]
for idx, i in enumerate(a):
    if 3 in i.keys() or 5 in i.keys():
        a.pop(idx)
        print a, '3222'
    print a