#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/12/28 16:35

i = ['a', 'b']
l = [1, 2]

print(dict([i, l]))


l1 = [1, 2, 3, 6, 87, 3]
l2 = ['aa', 'bb', 'cc', 'dd', 'ee', 'ff']
d = {}
for index in range(len(l1)):
    d[l1[index]] = l2[index]    # 注意，key 若重复，则新值覆盖旧值

print(d)

b = dict(zip(l1, l2))
print(b)

print({l1[i]: l2[i] for i in range(len(l1))})


d = {}
for i in range(len(l1)):
    d.setdefault(l1[i], l2[i])
print(d)

r = range(ord('a'), ord('z') + 1)
a = (i for i in r)
b = map(chr, r)
print(dict(zip(a, b)))