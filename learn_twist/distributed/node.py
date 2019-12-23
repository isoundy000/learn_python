# -*- encoding: utf-8 -*-
'''
Created on 2019年11月16日

@author: houguangdong
'''

from twisted.internet.defer import Deferred
from twisted.python import log
from twisted.spread import pb
from twisted.internet import reactor

from learn_twist.distributed.reference import ProxyReference

# typing
from typing import Tuple
from typing import Union

reactor = reactor


def call_remote(obj, func_name, *args, **kw):
    """远程调用
    @param obj:
    @param func_name:
    @param args:
    @param kw:
    @return:
    """
    log.msg("call remote:", obj, func_name, args, kw)
    return obj.callRemote(func_name, *args, **kw)


class RemoteObject(object):
    """远程调用对象
    """

    def __init__(self, name):
        """初始化远程调用对象
        @param name:
        """
        self._name = name  # type: str
        self._factory = pb.PBClientFactory()  # type: pb.PBClientFactory
        self._reference = ProxyReference()  # type: ProxyReference
        self._addr = None  # type: Union[Tuple[str, int], None]

    def set_name(self, name: str):
        """ 设置节点的名称
        @param name:
        @return:
        """
        self._name = name

    def get_name(self) -> str:
        """ 获取节点的名称
        @return:
        """
        return self._name

    def connect(self, addr):
        """初始化远程调用对象
        @param addr:
        @return:
        """
        self._addr = addr
        reactor.connectTCP(addr[0], addr[1], self._factory)
        self.take_proxy()

    def reconnect(self):
        """重新连接
        @return:
        """
        self.connect(self._addr)

    def add_service_channel(self, service):
        """设置引用对象
        @param service:
        @return:
        """
        self._reference.add_service(service)

    def take_proxy(self):
        """像远程服务端发送代理通道对象
        @return:
        """
        defer_remote = self._factory.getRootObject()
        defer_remote.addCallback(call_remote, 'take_proxy', self._name, self._reference)

    def call_remote(self, command_id, *args, **kw):
        """远程调用
        @param command_id:
        @param args:
        @param kw:
        @return:
        @rtype: Deferred
        """
        defer_remote = self._factory.getRootObject()
        return defer_remote.addCallback(call_remote, 'call_target', command_id, *args, **kw)

    @property
    def reference(self) -> ProxyReference:
        return self._reference