# -*- encoding: utf-8 -*-
'''
Created on 2019年11月16日

@author: houguangdong
'''
from twisted.python import log
from twisted.spread import pb

from learn_twist.utils.services import Service



class ProxyReference(pb.Referenceable):
    """代理通道
    """

    def __init__(self):
        """初始化
        """
        self._service = Service('proxy')  # type: Service

    def add_service(self, service: Service):
        """添加一条服务通道
        @param service:
        @return:
        """
        self._service = service

    def remote_call_child(self, command, *arg, **kw):
        """代理发送数据
        @param command:
        @param arg:
        @param kw:
        @return:
        """

        return self._service.call_target(command, *arg, **kw)

    @property
    def service(self) -> Service:
        """
        @return:
        """
        return self._service