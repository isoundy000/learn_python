#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


import time
import datetime

import settings
import game_config
from lib.db import ModelBase
from lib.utils import weight_choice

from models.config import ServerConfig

MESSAGES_LEN = 30


class Shop(ModelBase):
    """用户商店数据模型
    """
    def __init__(self, uid=None):
        self.uid = uid
        self._attrs = {

        }
        super(Shop, self).__init__(uid)

    @classmethod
    def get(cls, uid, server):
        o = super(Shop, cls).get(uid, server)
        o.refresh_data()
        fredis = o.get_father_redis()
        setattr(o, "fredis", fredis)
        return o

    def refresh_data(self):
        """按天刷新数据
        """
        pass

    @classmethod
    def update_outlets(cls, server_name):
        """定时刷新钻石商城
        """
        pass