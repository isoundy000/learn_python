# -*- encoding: utf-8 -*-
'''
Created on 2019年11月15日

@author: houguangdong
'''
from twisted.internet.protocol import Protocol, ServerFactory
from twisted.application import service, internet
from twisted.python import log
import os

# configuration parameters
port = 9999
iface = '127.0.0.1'
poetry_file = 'poetry_server/poetry/ecstasy.txt'


class PoetryProtocol(Protocol):

    def connectionMade(self):
        poem = self.factory.service.poem
        log.msg('sending %d bytes of poetry to %s' % (len(poem), self.transport.getPeer()))
        self.transport.write(poem)
        # self.transport.loseConnection()

    def dataReceived(self, data):
        log.msg('receive client data %s' % data)
        # self.transport.write(data)

    def connectionLost(self, reason=None):
        self.transport.loseConnection()


class PoetryFactory(ServerFactory):

    protocol = PoetryProtocol

    def __init__(self, service):
        self.service = service


class PoetryService(service.Service):

    def __init__(self, poetry_file):
        self.poetry_file = os.path.abspath(poetry_file)

    def startService(self):
        service.Service.startService(self)
        self.poem = open(self.poetry_file).read()
        log.msg('loaded a poem from: %s' % (self.poetry_file,))


top_service = service.MultiService()
poetry_service = PoetryService(poetry_file)
poetry_service.setServiceParent(top_service)

factory = PoetryFactory(poetry_service)
# twisted 提供了一个TCPServer service 用来创建一个和任意factory 相连的 监听tcp 连接的socket .我们没有直接用reactor.listenTCP 的原因是tac 文件的工作是让我们的application准备好,而不是运行它.TCPServer 在被twisted 启动的时候TCPServer会创建这个socket.
tcp_service = internet.TCPServer(port, factory, interface=iface)
tcp_service.setServiceParent(top_service)

# ok,现在我们的service 都被绑定进集合去了.现在我们可以创建我们的Application,并把我们的集合传给它.
application = service.Application("fastpoetry")
top_service.setServiceParent(application)
# 一个tac文件,我们需要用twisted 来运行它.当然,它也是一个python 文件.所以先让我们用python 执行一下它看看会发生什么:
# 启动
# twistd -n --python poetry_server/poetry_server.py
# twistd - y poetry_server / poetry_server.py  守护进程
# twistd --python poetry_server/poetry_server.py 守护进程

# -l poetry_server/peotry.log 指定日志的路径
# twistd -n -l poetry_server/peotry.log --python poetry_server/poetry_server.py

# 现在我们可以测试了,你可以用poetry client 或者netcat:
#        netcat localhost 10000
# mac上  nc 127.0.0.1 9999

# twistd ftp --help
# 你可以用下面的命令运行一个ftp 服务:
# twistd --nodaemon ftp --port 10001