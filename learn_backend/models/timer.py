#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
倒计时使用的类，用于其他进程和timer进程沟通
"""
from lib.db import ModelBase


class Timer(ModelBase):
    """
    Timer: 倒计时类，用于其他进程和timer进程沟通
    """
    def __init__(self, uid='timer'):
        self.uid = uid
        self._attrs = {
            'last_update_timestamp': {
                # item_id: timestamp
            },
            'next_update_timestamp': {
                # item_id: timestamp
            },
        }
        super(Timer, self).__init__(self.uid)

    @classmethod
    def get(cls, uid='timer', server_name=''):
        if not server_name:
            raise TypeError('ERROR, NEED SERVER_NAME')
        return super(Timer, cls).get(uid, server_name)