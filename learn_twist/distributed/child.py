# -*- encoding: utf-8 -*-
'''
Created on 2019年11月16日

@author: houguangdong
'''
# typing
from typing import Union
from twisted.spread.pb import RemoteReference


class Child(object):
    """子节点对象
    """

    def __init__(self, child_id: str, child_name: str):
        """初始化子节点对象
        @param child_id: 节点ID
        @param child_name: 节点name
        """
        self._id = child_id         # type: str
        self._name = child_name     # type: str
        self._transport = None      # type: Union[None, RemoteReference]

    @property
    def child_id(self):
        return self._id

    @property
    def child_name(self):
        return self._name

    def set_transport(self, transport):
        """设置子节点的通道
        @param transport:
        @return:
        """
        self._transport = transport

    def call_back_child(self, *args, **kw):
        """回调子节点的接口
        @param args:
        @param kw:
        @return:
        """
        recv_data = self._transport.callRemote('call_child', *args, **kw)
        return recv_data