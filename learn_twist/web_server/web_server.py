# -*- encoding: utf-8 -*-
'''
Created on 2019年11月16日

@author: houguangdong
'''

# 3.使用twisted框架创建Web服务器
from twisted.internet import protocol, reactor
from twisted.protocols import basic


class SimpleLogger(basic.LineReceiver):

    def connectionMade(self):
        print('Got connection from', self.transport.client)

    def connectionLost(self, reason=None):
        print(self.transport.client, 'disconnected')

    def lineReceived(self, line):
        print('data from client are as followings:')
        print(line)
        responseData = "Welcome to Twisted World！\r\n".encode('utf-8')
        self.transport.write(responseData)
        self.transport.loseConnection()                 # 终止连接


# 实例化protocol.ServerFactory()
'''
protocol.py
class ServerFactory(Factory):
    """Subclass this to indicate that your protocol.Factory is only usable for servers.
    """
'''
factory = protocol.ServerFactory()      # ***0120 protocol.ServerFactory()
factory.protocol = SimpleLogger
reactor.listenTCP(9999, factory)
reactor.run()