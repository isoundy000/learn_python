#!/usr/bin/env python
# -*- coding:utf-8 -*-


class AreaStatus(object):
    """# AreaStatus: 地块儿的状态"""
    def __init__(self, r, c, s=0):
        self.r = r  # 地块儿所处行
        self.c = c  # 地块儿所处列
        self.s = int(s) # 地块儿状态, -1是不拥有，0是可见，1是拥有，2是可收复
        super(AreaStatus, self).__init__()

    def __repr__(self):
        """# __repr__: 专为json化准备
        """
        return str(self.s)