# -*- encoding: utf-8 -*-
'''
Created on 2018年4月10日

@author: houguangdong
'''

class Hou(dict):
    def __init__(self):
        dict.__init__(self)
        self["_a"] = 0
        self["_b"] = []
        self["_c"] = {}
        self["_d"] = False
        self["_f"] = {
            "f1": {},
            "f2": True
        }
        self["__z"] = 0
        self["__k"] = []
        self["g"] = 0


if __name__ == '__main__':
    hou = Hou()
    for i in dir(hou):
        print i
    print hou.viewitems()
    print hou.viewkeys()
    print hou.viewvalues()
    print hou["g"]