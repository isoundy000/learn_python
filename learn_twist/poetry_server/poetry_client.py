# -*- encoding: utf-8 -*-
'''
Created on 2019年11月15日

@author: houguangdong
'''
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor
from twisted.python import log
import os

# configuration parameters
port = 9999
ip = '127.0.0.1'


class PoetryProtocol(Protocol):

    def connectionMade(self):
        print 'client mode'
        self.transport.write('ggggg')

    def dataReceived(self, data):
        print data.decode("utf-8")
        self.connectionLost()

    def connectionLost(self, reason=None):
        self.transport.loseConnection()


class PoetryFactory(ClientFactory):

    def __init__(self):
        self.protocol = None

    def startedConnecting(self, connector):
        print("Start to Connect...")

    def buildProtocol(self, addr):
        print("Connected...")
        self.protocol = PoetryProtocol()
        return self.protocol

    def clientConnectionLost(self, connector, reason):
        print("Client Lost connection. Reason: ", reason)
        reactor.stop()

    def clientConnectionFailed(self, connector, reason):
        print("Client Connection is failed, Reason: ", reason)
        reactor.stop()


factory = PoetryFactory()
reactor.connectTCP(ip, port, factory)
reactor.run()