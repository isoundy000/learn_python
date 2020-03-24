#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import time
import game_config

from lib.db import ModelBase
from logics import notice
from models.commander import Commander as CommanderM


class Item(ModelBase):
    """# Item 道具包裹

    self.box_num = 50    # 最大格子数
    self.items = {
        1: [99, 99, 1],    # 道具id (int型): 所占用的格子数以及每个格子里的对应的数量  ps：数组长度为占用的格子数
        2: [98],
        3: [1]
    }
    self.exchange_log = {
        1: 3,         # 兑换记录  兑换选项1 兑换了 3次
    }
    """

    def __init__(self, uid=None):
        self.uid = uid
        self._attrs = {
            'box_num': 500,
            'items': {},                        # 道具
            'daily_use': {},                    # 每日使用道具次数{item_id: 1, item_id1: 2}
            'last_day': '',                     # 刷新日期
            'exchange_log': {},                 # 兑换记录
            'protect_expire': 0,                # 保护不被抢的时间
            'rob_log': [],                      # 抢夺记录
            'box_use_counts': {},               # box使用次数记录
            'box_replace_counts': {}            # box替换记录
        }
        super(Item, self).__init__(self.uid)


    def refresh(self):
        # 扩大道具包大小 50->500
        if self.box_num <= 50:
            self.box_num = 500

        today = time.strftime('%Y-%m-%d')
        pass

    @staticmethod
    def get(cls, uid, server=''):
        o = super(Item, cls).get(uid, server)
        o.refresh()
        return o