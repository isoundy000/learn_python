#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/11/21 23:26
# @version: 0.0.1
# @Author: houguangdong
# @File: test_server_master.py
# @Software: PyCharm

import os

if os.name != 'nt':
    from twisted.internet import epollreactor
    epollreactor.install()


def println(a):
    print(a)


if __name__ == "__main__":
    from learn_twist.master.master import Master
    master = Master()
    master.config('config.json', 'test_server_main.py')
    master.start()