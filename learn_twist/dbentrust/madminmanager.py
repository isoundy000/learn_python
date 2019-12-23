#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/11/20 11:40
# @version: 0.0.1
# @Author: houguangdong
# @File: madminmanager.py
# @Software: PyCharm

from learn_twist.utils.singleton import Singleton


class MAdminManager:

    __metaclass__ = Singleton

    def __init__(self):
        self.admins = {}

    def register(self, admin):
        self.admins[admin.name] = admin

    def dropAdmin(self, adminname):
        if adminname in self.admins:
            del self.admins[adminname]

    def getAdmin(self, adminname):
        return self.admins.get(adminname)

    def checkAdmins(self):
        for admin in self.admins.values():
            admin.checkAll()



if __name__ == "__main__":
    m = MAdminManager()
    class Madmin():
        def __init__(self, name):
            self.name = name
    c = Madmin('cc')
    m.register(c)
    print(m.getAdmin('cc'))
    m.dropAdmin('cc')

    raise ValueError('ccccc')