#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/11/28 16:30
# @version: 0.0.1
# @Author: houguangdong
# @File: __add__.py
# @Software: PyCharm


from collections import defaultdict
from typing import Dict


class summable(defaultdict):

    def __add__(self, rhs):
        new = summable()
        for i in (list(self.keys()) + list(rhs.keys())):
            new[i] = self.get(i, 0) + rhs.get(i, 0)
        return new


a = summable()

b = summable(**{10001: 2})

c = summable(**{10001: 1})

d = a + b + c

print(dict(d))