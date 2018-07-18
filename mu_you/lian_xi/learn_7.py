# -*- encoding: utf-8 -*-
'''
Created on 2018年5月12日

@author: houguangdong
'''

# python
# 协程库gevent学习 - -gevent数据结构及实战(四)
# 一不留神已经到第四部分了，这一部分继续总结数据结构和常用的gevent类，废话不多说继续。
# 1.Timeout错误类
# 晚上在调试调用第三方接口的时候，发现有些接口耗时非常多，觉得应该有个超时接口来限制他们的过长时间的不结束。我开始尝试了requests上面的timeout参数，整个代码流程里面使用到了monkey_patch()
# 但是有个问题，我发现requests.timeout参数在gevent协作的时候表现很奇怪，似乎无法像同步程序这样表现出预想的状况。于是去gevent官方文档里面找寻timeout相关的模块，发现是有的gevent.Timeout继承自BaseException。
# 我们还是用例子讲解，由于gevent指南上没有介绍这个，我自己写了一个例子先看例子：

import gevent
from gevent import Timeout


class NIBAOZHA(BaseException):
    pass


def haha():
    x = gevent.Timeout(1, NIBAOZHA)
    x.start()
    try:
        print 'kaishila'
        # gevent.sleep(4)  # exception will be raised here, after *seconds* passed since start() call
        gevent.sleep(2)
        print 'nimei'

    except NIBAOZHA:
        print 'timeout'
    finally:
        x.cancel()


def xixi():
    print 'xiba'
    gevent.sleep(5)
    print 'zhihou'


gevent.joinall([gevent.spawn(xixi),
                gevent.spawn(haha),
                ])

# Timeout是一个错误类，主要用法是实例化它，然后制定一个超时时间如果有想要抛出的异常第二个参数填写想要抛出的异常。
# 如果当前greenlet在Timeout调用完start()
# 之后超过了超时时间，就会抛出相应的异常，没有指定异常的话就会抛出gevent.Timeout异常。
# 这一段代码里面可能有个地方会引起的注意，为什么要用finally? 因为如果在try里面之前有其他地方抛出了被捕获的异常，可能导致后面抛出无法预料到的timeout异常，所以最好关闭掉这个没有被触发的超时异常。
# 文档里面还介绍了一些方便的写法例如实现了上下文管理协议等
# 详见：
# http: // www.gevent.org / gevent.html  # timeouts
#
# 2.锁和信号量(locks and semaphores)：
# 信号量是一个允许greenlet从底层互相协作用的一个东西，可以限制并发访问互斥的资源。
# 信号量有两个方法，acquire和release。在信号量是否已经被
# acquire或release，和拥有资源的数量之间不同，被称为此信号量的范围(the bound of thesemaphore)。
# 如果一个信号量的范围已经降到0，那么会阻塞acquire操作直到有其他家伙释放。
# 以上的话摘自gevent学习指南，我相信第一次看的朋友绝对一脸蒙比。。什么意思？
# 下面先来看代码，然后我来翻译一下这个意思：

from gevent import sleep
from gevent.pool import Pool
from gevent.coros import BoundedSemaphore

sem = BoundedSemaphore(2)


def worker1(n):
    sem.acquire()
    print('Worker %i acquired semaphore' % n)
    sleep(0)
    sem.release()
    print('Worker %i released semaphore' % n)


def worker2(n):
    with sem:
        print('Worker %i acquired semaphore' % n)
        sleep(0)
    print('Worker %i released semaphore' % n)


pool = Pool()
pool.map(worker1, xrange(0, 2))
pool.map(worker2, xrange(3, 6))

# 对比一下和下面代码的运行结果：

from gevent import sleep
from gevent.pool import Pool
from gevent.lock import BoundedSemaphore

sem = BoundedSemaphore(2)


def worker1(n):
    # sem.acquire()
    print('Worker %i acquired semaphore' % n)
    sleep(0)
    # sem.release()
    print('Worker %i released semaphore' % n)


def worker2(n):
    # with sem:
    print('Worker %i acquired semaphore' % n)
    sleep(0)
    print('Worker %i released semaphore' % n)


pool = Pool()
pool.map(worker1, xrange(0, 2))
pool.map(worker2, xrange(3, 6))
# 其实不用再多说什么你也应该了解了，当我们使用底层同步元语对象BoundSemaphore(2)
# 初始化两个范围之后，就意味着，同时只能有两个greenlet去拿到这两个锁，在这两个锁被aquire之后，其他人必须等待其被relase，否则无法再继续并发更多的greenlet。上面对比就是个好例子，第一组代码的运行先spawn两个greenlet去拿到锁然后释放锁，这里似乎没有什么不一样。但是work2中你会发现，有锁的话你只能看到3，4
# 一起运行然后再运行5。如果没有sem, 3, 4, 5
# 将会同时运行。而且从代码来看，semaphore还支持上下文管理器，看起来还蛮友好的，更多api和介绍参考文档：http: // www.gevent.org / gevent.lock.html
#
# 3.线程局部变量(ThreadLocals)：
# Gevent也允许你指定局部于greenlet上下文的数据。 在内部，它被实现为以greenlet的getcurrent()
# 为键， 在一个私有命名空间寻址的全局查找。
# 一言不合先上代码：

import gevent
from gevent.local import local

x = local()


def f1():
    x.x = 1
    print x.x
    print x.__dict__


def f2():
    x.y = 2
    print(x.y)

    try:
        print x.__dict__
    except AttributeError:
        print("x is not local to f2")


g1 = gevent.spawn(f1)
g2 = gevent.spawn(f2)

gevent.joinall([g1, g2])
# 这里先初始化了一个线程本地对象local，给x。然后x会把保存给它的属性当作线程本地变量给存储起来。当其他greenlet去访问它的时候是无法访问到的，它只在自己的greenlet的命名空间中有效。这样可以让我们用来做一些有趣的事情，比如打印属于该greenlet的log日志，将日志存储在greenlet本地local()
# 中从而与其它greenlet互不影响，在协程切换的时候也能打出完整日志。还有这是不是很容易让我们联想到常用python
# web应用框架flask的requests实现？一个requests就是一个http访问，在整个访问过程中我们可以从requests对象里面拿到很多参数，但是它和其他的requests互不影响，这就是线程本地变量的作用。
# 另外再提一点, genvent.local还可以被继承实现基于当前greenlet能访问的一组属性的自己的类，来看代码：

import gevent
from gevent.local import local


class MyLocal(local):
    __slots__ = ('number', 'x')

    # number = 2
    initialized = False

    def __init__(self, **kw):
        if self.initialized:
            raise SystemError('__init__ called too many times')
        self.initialized = True
        self.__dict__.update(kw)

    def squared(self):
        return self.number ** 2


stash = MyLocal()


def f1():
    stash.x = 1
    stash.number = 3
    print stash.x
    print stash.number


def f2():
    stash.y = 2
    print(stash.y)

    try:
        print stash.x
        print stash.number
    except AttributeError:
        print("x is not local to f2")


g1 = gevent.spawn(f1)
g2 = gevent.spawn(f2)

gevent.joinall([g1, g2])
# 这里Mylocal继承了gevent的local，这里重点介绍一下__slots__在这里的用法，我们知道在常规的类里面指定__slots__的意思往往是只允许该类下的属性只允许有__slots__里面这些，超出的就会报出Attribute
# error的错误。但是继承了local的__slots__在这里却是指，申明了的属性将会穿透所有greenlet变成一个全局可读的，并不再是线程本地的，这里注意下。 其他的都没有什么好说的了。
# 就这样吧，我将最后的actors模式和gevent子进程还有一些要说的话留在第五讲。