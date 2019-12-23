#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/11/20 11:39
# @version: 0.0.1
# @Author: houguangdong
# @File: test_dbentrust.py
# @Software: PyCharm

from learn_twist.dbentrust.dbpool import dbpool
from learn_twist.dbentrust.madminmanager import MAdminManager
from learn_twist.dbentrust import mmode
from learn_twist.dbentrust.memclient import mclient
import time


if __name__ == "__main__":

# CREATE TABLE `tb_register` (
#   `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id',
#   `username` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL DEFAULT '' COMMENT '用户名',
#   `password` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL DEFAULT '' COMMENT '用户密码',
#   PRIMARY KEY (`id`,`username`)
#   ) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8
#
    hostname = 'localhost'
    username = 'root'
    password = '123456'
    dbname = 'dong'
    charset = 'utf8'
    tablename = 'users_test'
    aa = {
        'host': "localhost",
        'user': 'root',
        'passwd': '123456',
        'db': 'dong',
        'port': 3306,
        'charset': 'utf8'
    }
    dbpool.initPool(**aa)
    mclient.connection(['127.0.0.1: 11211'], "dong")

    mmanager = MAdminManager()
    m1 = mmode.MAdmin('users_test', 'id', incrkey='id')
    m1.insert()
    print(m1.get('_incrvalue'))
    m2 = mmode.MAdmin('users_test', 'id', incrkey='id')
    print(m2.get('_incrvalue'))