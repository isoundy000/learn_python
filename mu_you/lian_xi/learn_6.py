# -*- encoding: utf-8 -*-
'''
Created on 2018年5月11日

@author: houguangdong
'''

# python
# 协程库gevent学习 - -gevent数据结构及实战(三)
# gevent学习系列第三章，前面两章分析了大量常用几个函数的源码以及实现原理。这一章重点偏向实战了，按照官方给出的gevent学习指南，我将依次分析官方给出的7个数据结构。以及给出几个相应使用他们的例子。
#
# 事件：
# 事件是一个可以让我们在Greenlet之间异步通信的形式贴上一个gevent指南上面的例子：


import gevent
from gevent.event import Event

'''
Illustrates the use of events
'''

evt = Event()


def setter():
    '''After 3 seconds, wake all threads waiting on the value of evt'''
    print('A: Hey wait for me, I have to do something')
    gevent.sleep(3)
    print("Ok, I'm done")
    evt.set()


def waiter():
    '''After 3 seconds the get call will unblock'''
    print("I'll wait for you")
    evt.wait()  # blocking
    print("It's about time")


def main():
    gevent.joinall([
        gevent.spawn(setter),
        gevent.spawn(waiter),
        gevent.spawn(waiter),
    ])


if __name__ == '__main__':
    main()

# 这里setter和waiter一共起了三个协程。分析一下运行顺序应该很容易了解evt是干嘛的：
# 首先回调之行到运行setter
# 打印str然后gevent.sleep(3)。
# 然后执行第二个回调waitter()
# 执行到evt.wait()
# 的时候阻塞住然后切换，怎么切换的细节要分析的话又是一大波。总之就是切换了
# 然后执行第三个回调waitter()
# 执行到evt.wait()
# 又被阻塞了，这个时候继续执行下一个回调就会回到setter里面，因为没有人在他前面往hub.loop里注册了
# 然后这里执行"ok, i'm done"
# ok我撸完了，运行evt.set()
# 将flag设置为True.然后另外两个被阻塞的waitter的evt.wait()
# 方法在看到flag已经为True之后不再继续阻塞运行并且结束。
# 可以看到，Event可以协同好几个Greenlet同时工作，并且一个主Greenlet在操作的时候可以让其他几个都处于等待的状态，可以实现一些特定的环境和需求。


from gevent.event import AsyncResult

a = AsyncResult()


def setter1():
    """
    After 3 seconds set the result of a.
    """
    gevent.sleep(3)
    a.set('Hello!')


def waiter1():
    """
    After 3 seconds the get call will unblock after the setter
    puts a value into the AsyncResult.
    """
    print(a.get())


gevent.joinall([
    gevent.spawn(setter),
    gevent.spawn(waiter),
])

# Event还有一个扩展AsyncResult， 这个扩展可以在set的时候带上数据传递给各waiter去get。这里get还是会阻塞，但是等待的就是不flag了，而是一个值或一个报错相关更详细的api或更多功能可以参考文档http: // www.gevent.org / gevent.event.html。
# 2: 队列：
# 队列是一个排序的数据集合，它有常见的put / get操作， 但是它是以在Greenlet之间可以安全操作的方式来实现的。
# 举例来说，如果一个Greenlet从队列中取出一项，此项就不会被同时执行的其它Greenlet再取到了。可以理解成基于greenlet之间的安全队列吧还是先贴上一个官方的例子：
from gevent.queue import Queue
tasks = Queue()


def worker(n):
    while not tasks.empty():
        task = tasks.get()
        print('Worker %s got task %s' % (n, task))
        gevent.sleep(0)

    print('Quitting time!')


def boss():
    for i in xrange(1, 25):
        tasks.put_nowait(i)


gevent.spawn(boss).join()

gevent.joinall([
    gevent.spawn(worker, 'steve'),
    gevent.spawn(worker, 'john'),
    gevent.spawn(worker, 'nancy'),
])
# 首先初始化一个Queue()
# 实例。这里会先运行boss()
# 调用put_nowait()
# 方法不阻塞的往队列里面放24个元素。然后下面依次从Queue里对数字进行消费，起了三个协程分别命名了不同的名字，使用get方法依次消费队列里面的数字直到消费完毕。
# put和get操作都有非阻塞的版本，put_nowait和get_nowait不会阻塞， 然而在操作不能完成时抛出gevent.queue.Empty或gevent.queue.Full异常。同时Queue队列可以支持设置最大队列值，查看队列现在元素数量qsize(), 队列是否为空empty()，队列是否满了full()
# 等api在使用的时候最好也参考一下文档：http: // www.gevent.org / gevent.queue.html

# 3.Group / Pool
# gevent文档翻译为组合池：
# 组(group)
# 是一个运行中greenlet的集合，集合中的greenlet像一个组一样
# 会被共同管理和调度。 它也兼饰了像Python的multiprocessing库那样的
# 平行调度器的角色。
# 我的理解是，在一个组(group)
# 里面的greenlet会被统一管理和调度。
# 先看指南上的例子：

from gevent.pool import Group


def talk(msg):
    for i in xrange(3):
        print(msg)


g1 = gevent.spawn(talk, 'bar')
g2 = gevent.spawn(talk, 'foo')

group = Group()
group.add(g1)
group.add(g2)
group.join()
# 这个例子非常简单。就是spawn了好几个talk，然后都加到组里面。最后使用group.join()
# 来等待所有spawn完成，每完成一个就会从group里面去掉。由于没有返回值等问题，这个demo非常简单，来看下一个稍微复杂一点的我这里把这个例子分成三个分析.

# 第一个例子Group().map()：
from gevent import getcurrent
from gevent.pool import Group

group = Group()


def hello_from(n):
    print('Size of group %s' % len(group))
    print('Hello from Greenlet %s' % id(getcurrent()))
    return n


x = group.map(hello_from, xrange(3))
print type(x)
print x
# 这里使用了group.map()
# 这个函数来取得各spawn的返回值。map()
# 是由第二个参数控制迭代次数，并且传递给第一个参数值而运行的。拿这个函数举例，这里会返回一个list构成这个list的对象就是将迭代的参数传进函数运行之后的返回值。这里得到的结果是[0, 1, 2]


# 第二个例子Group().imap():
from gevent.pool import Group


def intensive(n):
    gevent.sleep(3 - n)
    return 'task', n


print('Ordered')
ogroup = Group()
x = ogroup.imap(intensive, xrange(3))
print x

for x in ogroup.imap(intensive, xrange(3)):
    print x

# 这里imap与map不一样的地方可能熟悉python基础库的同学很容易看出来，map返回list对象, 而imap返回一个iterable对象。所以如果要取得里面的值比如想打印就必须写成像代码最后一行那种。(
# 或者直接包一个list让他变成map函数😂)。另外提一下imap的内部实现，其实是继承了Greenlet对象，在里面启了spawn()。imap里面还有一个挺好用的参数maxsize默认情况是没有设置的当设置了之后，会将迭代变成一批一批的执行，这里再举一个例子：


def intensive(n):
    gevent.sleep(2)
    return 'task', n


print('Ordered')
ogroup = Group()
x = ogroup.imap(intensive, xrange(20), maxsize=3)
print x

# 这里运行的时候，会将并行控制到3个，执行也是每2秒执行3个，而不是不设置的时候2秒之后将输出所有的结果。
# 第三个例子Group().imap_unordered():
# 这个就很厉害了，我们直接上例子：

from gevent.pool import Group


def intensive(n):
    gevent.sleep(3 - n)
    return 'task', n


igroup = Group()
for i in igroup.imap_unordered(intensive, xrange(3)):
    print(i)

# 运行了可以看到输出是：
# ('task', 2)
# ('task', 1)
# ('task', 0)
# 先返回的先回来，这个如果是imap运行的话，会先等上3秒钟开始返回0然后1
# 2
# 一次返回。
# 最后我们再谈一下Pool对象，指南上的例子没啥意思。Group是Pool类的父类。pool是可以指定池子里面最多可以拥有多少greenlet在跑而且申明也很简单：

from gevent.pool import Pool

x = Pool(10)
# 其他就是继承了一些Group中的用法.
# 最后我用一个我利用这一章中讲解到的一些数据结构写的生产消费者模型结束gevent数据结构及实战三的讲解：
import gevent.monkey

gevent.monkey.patch_all()
import requests
from gevent.queue import Queue, Full, Empty
from gevent.pool import Pool

# if Queue() have no parameter It's unlimited
# out jd_queue just put in 100 msg.......
msg_queue = Queue(100)
jd_pool = Pool(10)
jd_msg = "Boom"
test_url = "http://www.xiachufang.com"


def deal_with():
    while True:
        try:
            now_id = gevent.getcurrent()
            msg = msg_queue.get_nowait()
            print "handle " + msg
            print 'now start with now_id: %s' % now_id
            requests.get(test_url)
            print 'now end with now_id: %s' % now_id
        except Empty:
            gevent.sleep(0)


def product_msg(jd_msg):
    while True:
        try:
            msg_queue.put_nowait(jd_msg)
            print msg_queue.qsize()
        except Full:
            gevent.sleep(5)


jd_pool.add(gevent.spawn(product_msg, jd_msg))
for i in xrange(10):
    jd_pool.add(gevent.spawn(deal_with))
jd_pool.join()