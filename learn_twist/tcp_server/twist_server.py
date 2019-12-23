# -*- encoding: utf-8 -*-
'''
Created on 2019年11月8日

@author: houguangdong
'''
# https://blog.csdn.net/nginxs/article/details/77197505
# 需要切换到虚拟python3环境
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

clients = []

port = 9999


class Spreader(Protocol):

    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):                           # 在transport对象和服务器之间建立一条连接   接口方法connectionMade 连接建立起来后调用
        self.factory.numProtocols = self.factory.numProtocols + 1
        # python3 传递不过去是因为编码问题
        self.transport.write(                           # 以非阻塞的方式按顺序依次将数据写到物理连接上
            "欢迎来到Spread Site, 你是第%s个客户端用户!\n" % self.factory.numProtocols
        )
        print("new connect: %d" % self.factory.numProtocols)
        self.transport.writeSequence([b'f', b'g', b'k'])   # 将一个字符串列表写到物理连接上
        print(self.transport.getPeer(), 'client_peer')   # 取得连接中对端的地址信息
        print(self.transport.getHost(), 'server_host')   # 取得连接中本端的地址信息
        print(self.transport.client, 'client_ip and port') # 客户端主机名和端口
        clients.append(self)

    def dataReceived(self, data):                       # 接收数据时调用
        if data == 'close':
            self.transport.loseConnection()             # 将所有挂起的数据写入，然后关闭连接
            for client in clients:
                if client != self:
                    client.transport.write(data)
        else:
            print(data, '999999')

    def connectionLost(self, reason=None):              # 关闭连接时调用
        self.factory.numProtocols = self.factory.numProtocols - 1
        clients.remove(self)
        print("lost connect: %d" % (self.factory.numProtocols))


class SpreadFactory(Factory):

    def __init__(self):
        self.numProtocols = 0

    def buildProtocol(self, addr):
        return Spreader(self)



endpoint = TCP4ServerEndpoint(reactor, port)
endpoint.listen(SpreadFactory())                           # endpoint.listen(SpreadFactory())
reactor.run()

# 在这里很重要的一个函数就是buildProtocol, 此函数就是在工厂模式中创建协议的.我们是基于基类Factory来实现这个函数的, 下面我们看看派生自Protocol的协议类Spread,Spread的__Init__参数中，我们给它传入的是自定义的SpreadFactory, 然后我们看下基类Protocol的源代码
