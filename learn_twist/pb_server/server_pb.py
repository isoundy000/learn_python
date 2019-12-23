# -*- encoding: utf-8 -*-
'''
Created on 2019年11月11日

@author: houguangdong
'''
# https://blog.csdn.net/yangli91628/article/details/40146335
# Twisted中 pb 透明代理简介
# 透明代理(PB, Perspective Broker)是用于远程方法调用和对象交换协议，该协议是异步和对称的。使用PB，
# 客户端可以直接调用服务器的函数并得到函数的返回结果。
# Twisted针对Server和Client分别提供了pb.PBServerFactory和pb.PBClientFactory供用户使用，
# 其中Factory中的root对象必须继承自pb.Referenceable(pb.root就继承自pb.Referenceable)。
# Sevrer中提供的方法必须以remote_开头， Client使用该方法时不用指定remote。
# 例如下面的例子中服务器端提供了remote_echo方法，客户端使用callRemote("echo", "hi")即可调用该方法。

# 服务器端:
from twisted.spread import pb
from twisted.internet import reactor


port = 9999

class Echoer(pb.Root):

    def remote_echo(self, st):                              # //Server中提供的方法必须以remote_开头
        print(st)
        return st

    def remote_test(self):
        print('33333333')
        return self

    def remote_c(self, a, b):
        print('1111111', a, b)
        return a, b

    def rootObject(self, broker=None):
        print(self)
        return self


if __name__ == '__main__':
    reactor.listenTCP(port, pb.PBServerFactory(Echoer()))    # //Echoer继承于pb.Root
    reactor.run()


# pb.PBServerFactory的构造函数如下:
# def __init__(self, root, unsafeTracebacks=False, security=globalSecurity): (source)
# Parameters	root	                factory providing the root Referenceable used by the broker. (type: object providing or adaptable to IPBRoot. )
#  	        unsafeTracebacks	    if set, tracebacks for exceptions will be sent over the wire. (type: bool )
#  	        security	            security options used by the broker, default to globalSecurity. (type: twisted.spread.jelly.SecurityOptions )