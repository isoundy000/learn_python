# -*- encoding: utf-8 -*-
'''
Created on 2019年11月17日 15:46

@author: houguangdong
'''

from learn_twist.utils import services
from learn_twist.distributed.node import RemoteObject
from twisted.internet import reactor
from twisted.python import util, log
import sys

log.startLogging(sys.stdout)

reactor = reactor

addr = ('localhost', 9999)  #目标主机的地址
remote = RemoteObject('test_node')

service = services.Service('reference', services.Service.SINGLE_STYLE)  # 实例化一条服务对象
remote.add_service_channel(service)


def serviceHandle(target):
    service.map_target(target)


@serviceHandle
def printOK(data):
    print(data)
    print("############################")
    return "call printOK_01"


def apptest(commandId, *args, **kwargs):
    d = remote.call_remote(commandId, *args, **kwargs)
    d.addCallback(lambda a: util.println(a))
    return d


def startClient():
    reactor.callLater(1, apptest, 'printData1', u"node测试1", u"node测试2")
    remote.connect(addr)       # 连接远程主机
    reactor.run()


if __name__ == '__main__':
    startClient()