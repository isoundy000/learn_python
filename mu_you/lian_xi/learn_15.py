# -*- encoding: utf-8 -*-
'''
Created on 2018年9月5日

@author: houguangdong
'''

import os
path = "/Users/houguangdong/Downloads/xls/"
perfix = '(2'
for i in os.listdir(path):
    a = i.split('.')
    c = a[0].replace(a[0], a[0] + perfix)
    f = ".".join([c, a[1]])
    os.rename(path + i,  path + f)


# for i in range(300, 501):
    # print 'c%s = Column(Integer, nullable=True, default=0)' % i
    # print "alter table t_top_of_world_role_exchange add column `c%s` int(11) DEFAULT '0';" % i