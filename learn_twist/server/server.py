#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/11/20 12:02
# @version: 0.0.1
# @Author: houguangdong
# @File: server.py
# @Software: PyCharm

from klein import Klein
from learn_twist.netconnect.protoc import LiberateFactory
from learn_twist.server.globalobject import GO
from learn_twist.server.logobj import LogObj

from learn_twist.distributed.root import PBRoot
from learn_twist.distributed.root import BilateralFactory
from learn_twist.distributed.node import RemoteObject
from twisted.python import log
from twisted.internet import reactor
from learn_twist.utils import services
import os
import sys

# typing
from typing import Union
from typing import Dict
from typing import List

reactor = reactor


# def serverStop():
#     log.msg('stop')
#     if GO.stop_handler:
#         GO.stop_handler()
#     reactor.callLater(0.5, reactor.stop)
#     return True


class FFServer:

    def __init__(self):
        self.net_factory = None         # type: Union[LiberateFactory, None]
        self.root = None
        self.web_root = None            # type:  Union[Klein, None]
        self.remote = {}
        self.master_remote = None
        self.server_name = None
        self.remote_ports = []

    def config(self, config: Dict, server_name: str, master_conf: Union[None, Dict] = None):
        GO.json_config = config
        net_port = config.get('net_port')
        web_port = config.get('web_port')
        root_port = config.get('root_port')

        if not server_name:
            server_name = config.get('name')

        log_path = config.get('log')
        app = config.get('app')
        m_reload = config.get('reload')

        self.server_name = server_name
        self.remote_ports = config.get('remote_ports', [])

        if net_port:
            self.net_factory = LiberateFactory()
            net_service = services.CommandService("net_service")
            self.net_factory.add_service_channel(net_service)

            reactor.listenTCP(net_port, self.net_factory)

        if web_port:
            self.web_root = Klein()
            GO.web_root = self.web_root

        if root_port:
            self.root = PBRoot()
            root_service = services.Service("root_service")
            self.root.add_service_channel(root_service)
            reactor.listenTCP(root_port, BilateralFactory(self.root))

        for cnf in self.remote_ports:
            root_name = cnf.get('root_name')
            self.remote[root_name] = RemoteObject(self.server_name)

        if log_path:
            log.addObserver(LogObj(log_path))
        log.startLogging(sys.stdout)

        GO.config(net_factory=self.net_factory, root=self.root, remote=self.remote)
        GO.remote_connect = self.remote_connect

        if master_conf:
            master_port = master_conf.get('root_port')
            master_host = master_conf.get('root_host')
            self.master_remote = RemoteObject(server_name)
            addr = ('localhost', master_port) if not master_host else (master_host, master_port)
            self.master_remote.connect(addr)
            GO.master_remote = self.master_remote

        # command
        # import learn_twist.server.admin

        if app:
            __import__(app)

        if m_reload:
            _path_list = m_reload.split(".")
            GO.reload_module = __import__(m_reload, fromlist=_path_list[:1])


    def remote_connect(self, r_name, r_host):
        for cnf in self.remote_ports:
            _r_name = cnf.get('root_name')
            if r_name == _r_name:
                r_port = cnf.get('root_port')
                if not r_host:
                    addr = ('localhost', r_port)
                else:
                    addr = (r_host, r_port)
                self.remote[r_name].connect(addr)
                break

    def start(self):
        log.msg('%s start...' % self.server_name)
        log.msg('%s pid: %s' % (self.server_name, os.getpid()))
        reactor.run()