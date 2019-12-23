# -*- encoding: utf-8 -*-
'''
Created on 2019年11月17日 18:16

@author: houguangdong
'''

import time

from learn_twist.utils import const


class Connection(object):
    """
    """
    def __init__(self, _conn):
        """transport 连接的通道
        """
        self.instance = _conn
        self.last_heart_beat_time = 0
        self.set_time()

    def lose_conn(self):
        """断开与客户端的连接
        """
        self.instance.transport.connectionLost('lost connection')

    def safe_to_write_data(self, topic_id, msg):
        """发送消息
        """
        self.instance.safe_to_write_data(msg, topic_id)

    @property
    def dynamic_id(self):
        return self.instance.transport.sessionno

    @dynamic_id.setter
    def dynamic_id(self, value: int):
        self.instance.transport.sessionno = value

    @property
    def time_out(self):
        """判断链接是否过期"""
        if time.time() - self.last_heart_beat_time > const.TIME_OUT:
            return True
        return False

    def set_time(self):
        """设置当前时间为上次心跳时间"""
        self.last_heart_beat_time = time.time()