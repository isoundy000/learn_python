# -*- encoding: utf-8 -*-
'''
Created on 2018年9月5日

@author: houguangdong
'''

import os

#!/usr/bin/env python
#coding: utf-8

import string
import random

def Cpass(number = 8):
    Passwd = []
    st = string.printable
    for i in range(number):
        Passwd.append(random.choice(st))
    return "".join(Passwd)


# path = "/Users/houguangdong/Downloads/xls/"
# perfix = '(2'
# for i in os.listdir(path):
#     a = i.split('.')
#     c = a[0].replace(a[0], a[0] + perfix)
#     f = ".".join([c, a[1]])
#     os.rename(path + i,  path + f)


# for i in range(300, 501):
    # print 'c%s = Column(Integer, nullable=True, default=0)' % i
    # print "alter table t_top_of_world_role_exchange add column `c%s` int(11) DEFAULT '0';" % i

import subprocess


def c():
    # f = open('/Users/houguangdong/Downloads/aaa.txt', "wb")
    cmd = "curl https://swxx-wx-gs.hortor020.com"
    p = subprocess.Popen(cmd, bufsize=10000, stdout=subprocess.PIPE, close_fds=True)
    out, err = p.communicate()
    print out, err
    # f.write(str(a))


if __name__ == '__main__':
    # print Cpass()
    c()