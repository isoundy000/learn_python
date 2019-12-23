# -*- encoding: utf-8 -*-
'''
Created on 2019年11月16日

@author: houguangdong
'''

# 2.自定义Protocol--利用LineReceiver类作为父类
# 模块twisted.protocols.basic中包含了几个有用的已存在的protocol，
# 其中的LineReceiver执行dataReceived并在接受到了一个完整的行时调用事件处理器lineReceived。
# 如果当你在接受数据时除了使用lineReceived,还要做些别的，那么你可以使用LineReceiver定义的名为rawDataReceived事件处理器。

from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver


class SimpleLogger(LineReceiver):

    def connectionMade(self):
        print "Got connection from", self.transport.client

    def connectionLost(self, reason=None):
        print self.transport.client, 'disconnected'

    # 注意必须接收到完整的行(即遇到\r\n结束标志)时该函数才能成功执行
    def lineReceived(self, line):
        print line
        length = len(line)
        responsemsg = 'Dear client, I have received ' + str(length) + ' bytes from you\r\n'
        self.transport.write(responsemsg)       # 向客户端发送数据


factory = Factory()
factory.protocol = SimpleLogger
reactor.listenTCP(9999, factory)
reactor.run()