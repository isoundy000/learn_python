# -*- encoding: utf-8 -*-
'''
Created on 2019年11月16日

@author: houguangdong
'''

from twisted.python import log
from twisted.spread import pb
from learn_twist.distributed.child import Child
from learn_twist.distributed.manager import ChildesManager


# typing
from typing import Union
from learn_twist.utils.services import Service
from twisted.spread.pb import RemoteReference


class BilateralBroker(pb.Broker):

    def connectionLost(self, reason):
        client_id = self.transport.sessionno
        log.msg("node [%d] lose" % client_id)
        self.factory.root.drop_child_session_id(client_id)
        pb.Broker.connectionLost(self, reason)


class BilateralFactory(pb.PBServerFactory):
    protocol = BilateralBroker


class PBRoot(pb.Root):
    """PB 协议
    """

    def __init__(self, dns_manager=ChildesManager()):
        """
        @param dns_manager:
        """

        self.service = None  # type: Union[None, Service]
        self.childes_manager = dns_manager  # type: ChildesManager

    def add_service_channel(self, service):
        """添加服务通道
        @param service:
        @return:
        """
        self.service = service

    def remote_take_proxy(self, name, transport: RemoteReference):
        """设置代理通道
        @param name:
        @param transport:
        @return:
        """
        log.msg('node [%s] takeProxy ready' % name)
        log.msg(transport)
        child = Child(name, name)
        self.childes_manager.add_child(child)
        child.set_transport(transport)
        self.do_child_connect(name, transport)

    def do_child_connect(self, name, transport):
        """
        当node节点连接时的处理
        """
        pass

    def remote_call_target(self, command, *args, **kwargs):
        """远程调用方法
        @param command: int 指令号
        @param args: 调用参数
        @param kwargs: 调用参数
        """
        data = self.service.call_target(command, *args, **kwargs)
        return data

    def drop_child(self, *args, **kwargs):
        """
        @param args:
        @param kwargs:
        @return:
        """
        self.childes_manager.drop_child(*args, **kwargs)

    def drop_child_by_id(self, child_id):
        """删除子节点记录
        @param child_id:
        @return:
        """
        self.do_child_lost_connect(child_id)
        self.childes_manager.drop_child_by_id(child_id)

    def drop_child_session_id(self, session_id):
        """删除子节点记录
        @param session_id:
        @return:
        """
        child = self.childes_manager.get_child_by_session_id(session_id)
        if not child:
            return
        child_id = child.child_id
        self.do_child_lost_connect(child_id)
        self.childes_manager.drop_child_by_id(child_id)

    def do_child_lost_connect(self, child_id):
        """
        当node节点连接时的处理
        """
        pass

    def call_child(self, child_id, *args, **kwargs):
        """
        调用子节点的接口
        @param child_id: int 子节点的id
        """
        return self.childes_manager.call_child(child_id, *args, **kwargs)

    def call_child_by_name(self, child_name, *args, **kwargs):
        """调用子节点的接口
        @param child_name: 子节点的name
        """
        return self.childes_manager.call_child_by_name(child_name, *args, **kwargs)