# -*- encoding: utf-8 -*-
'''
Created on 2019年11月18日 11:33

@author: houguangdong
'''

from twisted.internet import reactor
import time


def tt(i, j):
    while 1:
        print(i, '-----------------', j)
        time.sleep(1)


reactor.callFromThread(tt, 1, 1)
reactor.callFromThread(tt, 4, 2)
reactor.run()
# 上面代码运行的结果是无限的打印1-------------------1，这个说明了主循环被阻塞住。

# 2. reactor.callInThread
# Method callInThread：
# Run the callable object in a separate thread.
# 此方法是创建独立的线程，用reactor stop方法无法停止它。这里涉及到一个线程池的概念
# reactor.suggestThreadPoolSize(15)来设置线程池的大小，默认是最小是5，最大是10.如果在默认情况下
#
# 3. from twisted.internet import threads
# threads.deferToThread(function),和callInThread一样，区别只是 deferToThread 可以返回一个deferred对象，从而允许你设定回调函数。
# 理解不够，参考一下http://www.cnblogs.com/zhengyun_ustc/archive/2010/05/18/1738357.html，http://gashero.yeax.com/?p=70