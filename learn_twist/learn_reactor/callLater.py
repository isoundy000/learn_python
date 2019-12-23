# -*- encoding: utf-8 -*-
'''
Created on 2019年11月18日 11:41

@author: houguangdong
'''

# 在 Twisted中，有一个全局用于实现事件循环的对象为reactor。
# 反应器具体的工作包括：定时任务、线程、建立网络连接、监听连接。

# 1、定时器简单实例
from twisted.internet import reactor
import time


def printTime():
    print('Current time is', time.strftime("%H:%M:%S"))


def stopReactor():
    print("Stopping reactor")
    reactor.stop()


# 使用reactor.callLater函数定时执行函数。reactor.callLater函数包含两个必须参数，等待的秒数，和需要调用的函数
reactor.callLater(1, printTime)
reactor.callLater(2, printTime)
reactor.callLater(3, printTime)
reactor.callLater(4, printTime)
reactor.callLater(5, stopReactor)

print('Running the reactor')
reactor.run()
print('Reactor stopped.')
