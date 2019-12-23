# -*- encoding: utf-8 -*-
'''
Created on 2019年11月11日

@author: houguangdong
'''

from twisted.spread import pb
from twisted.internet import reactor
from twisted.python import util


port = 9999
ip = '127.0.0.1'


def call_remote(obj, func_name, *args, **kw):
    """远程调用
    @param obj:
    @param func_name:
    @param args:
    @param kw:
    @return:
    """
    # log.msg("call remote:", obj, func_name, args, kw)
    return obj.callRemote(func_name, *args, **kw)


factory = pb.PBClientFactory()
reactor.connectTCP(ip, port, factory)
d = factory.getRootObject()
# d.addCallback(lambda object: object.callRemote("echo", "hi"))  # //客户端使用callRemote("echo", "hi")即可调用服务端的remote_echo()方法, 并将"hi"作为参数传入。
# d.addCallback(lambda aa: aa.callRemote("c", 'c', 'ff'))
# d.addCallback(lambda result: call_remote(result, 'c', 'c', 'g'))
# d.addErrback(lambda reason: 'error: ' + str(reason.value))
# f = d.addCallback(util.println)
# print f, 'zzzzz'
d.addCallback(lambda _: reactor.stop())
reactor.run()

# 远程方法调用除了可以返回和传递字符串、词典、列表等简单对象外，还可以传递pb.Referenceable对象。象上面的例子中，可以先调用callRemote("test")来获得一个新的pb.Referenceable对象，然后在对该对象使用callRemote方法。
# def callRemote(self, _name, *args, **kw): (source)
# Asynchronously invoke a remote method.  (异步调用远程方法)
# Parameters	_name	the name of the remote method to invoke (type: string )   (远程方法要调用的名字)
#  	         args	arguments to serialize for the remote function  元组参数
#  	         kw	keyword arguments to serialize for the remote function. 字典参数
# Returns	a Deferred which will be fired when the result of this remote call is received. (type: twisted.internet.defer.Deferred )