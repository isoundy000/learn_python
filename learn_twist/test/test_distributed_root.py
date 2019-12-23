# -*- encoding: utf-8 -*-
'''
Created on 2019年11月17日 15:46

@author: houguangdong
'''

from learn_twist.utils import services
from learn_twist.distributed.root import PBRoot, BilateralFactory
from twisted.internet import reactor
from twisted.python import log
import sys
import time
reactor = reactor
log.startLogging(sys.stdout)

root = PBRoot()
ser = services.Service('test')
root.add_service_channel(ser)


def serviceHandle(target):
    ser.map_target(target)


@serviceHandle
def printData1(data, data1):
    print(data, data1)
    print("----------------------------")
    # d = root.call_child_by_name('test_node', 1, u'Root测试')
    return data

@serviceHandle
def printData2(data, data1):
    print(data, data1)
    print("############################")
    # d = root.call_child_by_name('test_node', 1, u'Root测试')
    return data


if __name__ == '__main__':
    reactor.listenTCP(9999, BilateralFactory(root))
    reactor.callLater(5, root.call_child_by_name, 'test_node', 'printOK', 'asdfawefasdf')
    reactor.run()