# -*- encoding: utf-8 -*-
'''
Created on 2019年11月12日

@author: houguangdong
'''

from twisted.internet import protocol, reactor
from twisted.application import service


class Echo(protocol.Protocol):

    def dataReceived(self, data):
        self.transport.write(data)


class EchoFactory(protocol.Factory):

    def buildProtocol(self, addr):
        return Echo()