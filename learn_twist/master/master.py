#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/11/21 10:58
# @version: 0.0.1
# @Author: houguangdong
# @File: master.py
# @Software: PyCharm


import sys
import json
import subprocess
from klein import Klein
from twisted.internet import reactor
from learn_twist.utils import services
from learn_twist.distributed.root import PBRoot
from learn_twist.distributed.root import BilateralFactory
from learn_twist.server.globalobject import GO
from learn_twist.web.delayrequest import DelaySite
from twisted.python import log
from learn_twist.server.logobj import LogObj
from twisted.internet.pollreactor import install

# typing
from typing import Union

reactor = reactor   # type:install


MULTI_SERVER_MODE = 1
SINGLE_SERVER_MODE = 2
MASTER_SERVER_MODE = 3


class Master:

    def __init__(self):
        self.config_path: str = ''
        self.main_path: str = ''
        self.root: Union[PBRoot, None] = None
        self.web_root: Union[Klein, None] = None

    def config(self, config_path: str, main_path: str) -> None:
        """
        :param config_path:
        :param main_path:
        :return:
        """
        self.config_path = config_path
        self.main_path = main_path

    def master_app(self):
        with open(self.config_path, 'r') as f:
            GO.json_config = config = json.loads(f.read())

        # config
        master_cnf = config.get('master')
        root_port = master_cnf.get('root_port')
        web_port = master_cnf.get('web_port')
        master_log = master_cnf.get('log')

        self.root = PBRoot()
        root_service = services.Service("root_service")
        self.root.add_service_channel(root_service)
        GO.root = self.root
        # import learn_twist.master.rootapp

        self.web_root = Klein()
        GO.web_root = self.web_root
        # import learn_twist.master.webapp

        if master_log:
            log.addObserver(LogObj(master_log))
        log.startLogging(sys.stdout)

        reactor.listenTCP(web_port, DelaySite(self.web_root.resource()))
        reactor.listenTCP(root_port, BilateralFactory(self.root))

    def start(self):
        sys_args = sys.argv
        if len(sys_args) > 2 and sys_args[1] == "single":
            server_name = sys_args[2]
            if server_name == "master":
                mode = MASTER_SERVER_MODE
            else:
                mode = SINGLE_SERVER_MODE
        else:
            mode = MULTI_SERVER_MODE
            server_name = ""

        if mode == MULTI_SERVER_MODE:
            self.master_app()
            with open(self.config_path, 'r') as f:
                config = json.loads(f.read())
            servers_conf = config.get('servers')
            log.msg(servers_conf)
            for server_name in servers_conf.keys():
                cmd = 'python %s %s %s' % (self.main_path, server_name, self.config_path)
                log.msg('cmd:', cmd)
                subprocess.Popen(cmd, shell=True)
            reactor.run()
        elif mode == SINGLE_SERVER_MODE:
            sername = server_name
            cmds = 'python %s %s %s' % (self.main_path, sername, self.config_path)
            subprocess.Popen(cmds, shell=True)
        else:
            self.master_app()
            reactor.run()