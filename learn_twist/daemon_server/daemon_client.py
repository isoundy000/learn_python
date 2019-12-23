# -*- encoding: utf-8 -*-
'''
Created on 2019年11月15日

@author: houguangdong
'''


from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory
from twisted.protocols import basic
from twisted.application import service, internet
import pymysql


port = 9999
ip = '127.0.0.1'


class Mornitor_Protocol(basic.LineReceiver):

    def __init__(self):
        pass

    def connectionMade(self):
        print 'client Connected'

    def lineReceived(self, line):
        pass

    def connectionLost(self, reason='connectionDone'):
        print 'The client is close... ok!'


class Minitor_Factory(ClientFactory):
    # 还没想好要初始化什么
    protocol = Mornitor_Protocol

    def __init__(self):
        self.protocol = None


iface = '127.0.0.1'
factory = Minitor_Factory()
reactor.connectTCP(ip, port, factory)
reactor.run()