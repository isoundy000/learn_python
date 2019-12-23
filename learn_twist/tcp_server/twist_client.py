# -*- encoding: utf-8 -*-
'''
Created on 2019年11月6日

@author: houguangdong
'''

from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor
import threading
import time
import sys
import datetime


ip = '127.0.0.1'
port = 9999

class Echo(Protocol):

    def __init__(self):
        self.connected = False

    def connectionMade(self):
        self.connected = True

    def connectionLost(self, reason=None):
        self.connected = False

    def dataReceived(self, data):
        print(data.decode("utf-8"))


class EchoClientFactory(ClientFactory):

    def __init__(self):
        self.protocol = None

    def startedConnecting(self, connector):
        print("Start to Connect...")

    def buildProtocol(self, addr):
        print("Connected...")
        self.protocol = Echo()
        return self.protocol

    def clientConnectionLost(self, connector, reason):
        print("Client Lost connection. Reason: ", reason)
        print("Client Lost connection. Reason1: ", reason.getErrorMessage())

    def clientConnectionFailed(self, connector, reason):
        print("Client Connection is failed, Reason: ", reason)
        # reactor.stop()


bStop = False


def routine(factory):
    while not bStop:
        if factory.protocol and factory.protocol.connected:
            # python3 传递不过去是因为编码问题
            # factory.protocol.transport.write("hello, I'm %s %s\n" % (sys.argv[0], datetime.datetime.now()))     # 以非阻塞的方式按顺序依次将数据写到物理连接上
            factory.protocol.transport.writeSequence([b'aa', b'bb', b'cc', '\n'])                # 将一个字符串列表写到物理连接上
            print(factory.protocol.transport.getPeer(), 'server_address')                   # 取得连接中对端的地址信息
            print(factory.protocol.transport.getHost(), 'client_address')                   # 取得连接中本端的地址信息
        print(sys.argv[0], datetime.datetime.now())
        time.sleep(5)


factory = EchoClientFactory()
reactor.connectTCP(ip, port, factory)
threading.Thread(target=routine, args=(factory,)).start()
reactor.run()
bStop = True