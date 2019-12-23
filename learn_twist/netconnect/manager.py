# -*- encoding: utf-8 -*-
'''
Created on 2019年11月17日 21:06

@author: houguangdong
'''

import collections

from twisted.python import log

from learn_twist.netconnect.connection import Connection
from learn_twist.utils.const import const

# typing:
from typing import Dict
from typing import List


class ConnectionManager(object):
    """连接管理器
    @param _connections: dict {connID:conn Object}管理的所有连接
    """

    def __init__(self):
        """初始化
        """
        self._connections = {}  # type: Dict[int, Connection]
        self._queue_conns = collections.OrderedDict()

    def get_now_conn_cnt(self) -> int:
        """获取当前连接数量
        """
        return len(self._connections.items())

    @property
    def queue_num(self):
        return len(self._queue_conns)

    @property
    def connect_ids(self):
        return self._connections.keys()

    def has_conn(self, dynamic_id):
        """是否包含连接"""
        return dynamic_id in self._connections.keys()

    def add_conn(self, conn):
        """加入一条连接
        """
        _conn = Connection(conn)
        if _conn.dynamic_id in self._connections.keys():
            raise Exception("系统记录冲突")
        # 连接数达到上限，将连接缓存到队列中
        if const.MAX_CONNECTION <= len(self._connections):
            self._queue_conns[_conn.dynamic_id] = _conn
            return
        self._connections[_conn.dynamic_id] = _conn

    def drop_conn_by_id(self, dynamic_id: int):
        """更加连接的id删除连接实例
        """
        if dynamic_id in self._connections:
            del self._connections[dynamic_id]
        if dynamic_id in self._queue_conns:
            del self._queue_conns[dynamic_id]

    def get_conn_by_id(self, dynamic_id: int):
        """根据ID获取一条连接
        """
        return self._connections.get(dynamic_id, None)

    def lose_conn(self, dynamic_id):
        """根据连接ID主动端口与客户端的连接
        """
        conn = self.get_conn_by_id(dynamic_id)
        if conn:
            conn.lose_conn()

    def change_id(self, new_id, cur_id):
        print("self._connections", self._connections, cur_id, new_id)
        if cur_id not in self._connections:
            return False

        connection = self._connections[cur_id]
        if new_id in self._connections:
            old_connection = self._connections[new_id]
            old_connection.lose_conn()
            old_connection.dynamic_id = 0

        del self._connections[cur_id]
        self._connections[new_id] = connection
        connection.dynamic_id = new_id
        return True

    def pop_queue(self):
        if len(self._queue_conns) <= 0:
            return
        tmp = self._queue_conns.popitem(False)
        self._connections[tmp[0]] = tmp[1]
        return tmp[1]

    def push_msg(self, topic_id: str, msg: bytes, sends: List):
        """主动推送消息
        """
        try:
            for dynamic_id in sends:
                conn = self.get_conn_by_id(dynamic_id)
                if conn:
                    conn.safe_to_write_data(topic_id, msg)
                conn = self._queue_conns.get(dynamic_id, None)
                if conn:
                    conn.safe_to_write_data(topic_id, msg)
        except Exception as e:
            log.err(str(e))

    def check_timeout(self):
        for k, v in self._connections.items():
            if v.time_out:
                v.lose_conn()

    # def loop_check(self):
    #     loop = gevent.get_hub().loop
    #     t = loop.timer(0.0, const.TIME_OUT / 2)
    #     t.start(self.check_timeout)