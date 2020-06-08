 高性能python编程之协程(stackless)-乾颐堂

我们都知道并发（不是并行）编程目前有四种方式，多进程，多线程，异步，和协程。

多进程编程在python中有类似C的os.fork，当然还有更高层封装的multiprocessing标准库，在之前写过的python高可用程序设计方法http://www.cnblogs.com/hymenz/p/3488837.html中提供了类似nginx中master process和worker process间信号处理的方式，保证了业务进程的退出可以被主进程感知。

多线程编程python中有Thread和threading，在linux下所谓的线程，实际上是LWP轻量级进程，其在内核中具有和进程相同的调度方式，有关LWP，COW（写时拷贝），fork，vfork，clone等的资料较多，这里不再赘述。

异步在linux下主要有三种实现select，poll，epoll，关于异步不是本文的重点。

说协程肯定要说yield，我们先来看一个例子：

#coding=utf-8 
import time 
import sys 
# 生产者 
def produce(l): 
    i=0
    while 1: 
        if i < 5: 
            l.append(i) 
            yield i 
            i=i+1
            time.sleep(1) 
        else: 
            return
       
# 消费者 
def consume(l): 
    p = produce(l) 
    while 1: 
        try: 
            p.next() 
            while len(l) > 0: 
                print l.pop() 
        except StopIteration: 
            sys.exit(0) 
l = [] 
consume(l)

在上面的例子中，当程序执行到produce的yield i时，返回了一个generator，当我们在custom中调用p.next()，程序又返回到produce的yield i继续执行，这样l中又append了元素，然后我们print l.pop()，直到p.next()引发了StopIteration异常。

通过上面的例子我们看到协程的调度对于内核来说是不可见的，协程间是协同调度的，这使得并发量在上万的时候，协程的性能是远高于线程的。

import stackless 
import urllib2 
def output(): 
    while 1: 
        url=chan.receive() 
        print url 
        f=urllib2.urlopen(url) 
        #print f.read() 
        print stackless.getcurrent() 
      
def input(): 
    f=open('url.txt') 
    l=f.readlines() 
    for i in l: 
        chan.send(i) 
chan=stackless.channel() 
[stackless.tasklet(output)() for i in xrange(10)] 
stackless.tasklet(input)() 
stackless.run()

关于协程，可以参考greenlet,stackless,gevent,eventlet等的实现。

www.qytang.com/