#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/10

from twisted.internet.protocol import ReconnectingClientFactory


class FTReconnectFactory(ReconnectingClientFactory):
    def __init__(self):
        # 强制2s内重连...
        self.maxDelay = 2


    def startedConnecting(self, connector):
        pass


    def buildProtocol(self, addr):
        p = self.protocol()
        p.factory = self
        return p