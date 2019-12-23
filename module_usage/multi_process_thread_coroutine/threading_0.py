# -*- encoding: utf-8 -*-
'''
Created on 2019年11月19日 15: 16

@author: houguangdong
'''

# threading
# threading基于Java的线程模型设计。锁（Lock）和条件变量（Condition）在Java中是对象的基本行为（每一个对象都自带了锁和条件变量），而在Python中则是独立的对象。Python Thread提供了Java Thread的行为的子集；没有优先级、线程组，线程也不能被停止、暂停、恢复、中断。Java Thread中的部分被Python实现了的静态方法在threading中以模块方法的形式提供。
# threading 模块提供的常用方法：
# threading.currentThread(): 返回当前的线程变量。
# threading.enumerate(): 返回一个包含正在运行的线程的list。正在运行指线程启动后、结束前，不包括启动前和终止后的线程。
# threading.activeCount(): 返回正在运行的线程数量，与len(threading.enumerate())有相同的结果。
# threading模块提供的类：
# Thread, Lock, Rlock, Condition, [Bounded]Semaphore, Event, Timer, local.

# Thread
# Thread是线程类，与Java类似，有两种使用方法，直接传入要运行的方法或从Thread继承并覆盖run()：

from threading import Thread
import threading
import time
import random
# 方法1：将要执行的方法作为参数传给Thread的构造方法

def func():
    print('func() passed to Thread')

t = threading.Thread(target=func)
# t.start()

# 方法2：从Thread继承，并重写run()
class MyThread(threading.Thread):

    def run(self):
        print('MyThread extended from Thread')

t = MyThread()
# t.start()


print('---------------------------------------')

def foo(arg):
    for i in range(100):
        print(arg,i)
        time.sleep(1)
    print(arg)

t1 = Thread(target=foo, args=("线程1",))
t2 = Thread(target=foo, args=("线程2",))

print(t1.getName())         # 获取线程名
t2.setName("线程二")         # 设置线程名
print(t1.isDaemon())        # 查看是否是守护线程。默认不是守护线程
t1.setDaemon(True)          # 将t1设为守护线程，则在主线程执行完后（输出end后），即会结束
# t1.start()
# t1.join(5)                  # 此时主线程停止执行，t1线程执行5秒
print("end")
print('---------------------------------------')

# Lock
# Lock（指令锁）是可用的最低级的同步指令。Lock处于锁定状态时，不被特定的线程拥有。Lock包含两种状态——锁定和非锁定，以及两个基本的方法。
# 可以认为Lock有一个锁定池，当线程请求锁定时，将线程至于池中，直到获得锁定后出池。池中的线程处于状态图中的同步阻塞状态。
# 构造方法：
# Lock()
# 实例方法：
# acquire([timeout]): 使线程进入同步阻塞状态，尝试获得锁定。
# release(): 释放锁。使用前线程必须已获得锁定，否则将抛出异常。

num = 0

def foo(lock):
    time.sleep(random.randrange(0, 3))
    global num
    # 调用acquire([timeout])时，线程将一直阻塞，
    # 直到获得锁定或者直到timeout秒后（timeout参数可选）。
    # 返回是否获得锁。
    lock.acquire()  # 独占CPU
    print(num)
    num += 1
    lock.release()  # 一定要记得释放锁
    lock = threading.Lock()


lock = threading.Lock()
for i in range(100):
    p1 = Thread(target=foo, args=(lock,))
    # p1.start()


# RLock（可重入锁）是一个可以被同一个线程请求多次的同步指令。RLock使用了“拥有的线程”和“递归等级”的概念，处于锁定状态时，RLock被某个线程拥有。拥有RLock的线程可以再次调用acquire()，释放锁时需要调用release()相同次数。
# 可以认为RLock包含一个锁定池和一个初始值为0的计数器，每次成功调用 acquire()/release()，计数器将+1/-1，为0时锁处于未锁定状态。
# 构造方法：
# RLock()
# 实例方法：
# acquire([timeout])/release(): 跟Lock差不多。

def foo(rlock):
    time.sleep(random.randrange(0, 3))
    global num
    # 第1次请求锁
    rlock.acquire()
    print("test")
    # 第2次请求锁
    rlock.acquire()
    print(num)
    # 第1次释放锁
    rlock.release()
    num += 1
    # 第2次释放锁
    rlock.release()
    lock = threading.RLock()
    lock1 = threading.Lock()


rlock = threading.RLock()
for k in range(100):
    p2 = Thread(target=foo, args=(rlock,))
    # p2.start()


# 在继承的threading.Thread中使用锁
class myThread(threading.Thread):

    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        print('Starting ' + self.name)
        # 获得锁，成功获得锁定后返回True
        # 可选的timeout参数不填时将一直阻塞直到获得锁定
        # 否则超时后将返回False
        threadLock.acquire()
        print_time(self.name, self.counter, 3)
        # 释放锁
        threadLock.release()


def print_time(threadName, delay, counter):
    while counter:
        time.sleep(delay)
        print ("%s: %s" % (threadName, time.ctime(time.time())))
        counter -= 1


threadLock = threading.Lock()
threads = []

# 创建新线程
thread1 = myThread(1, "Thread-1", 1)
thread2 = myThread(2, "Thread-2", 2)

# 开启新线程
thread1.start()
thread2.start()

# 添加线程到线程列表
threads.append(thread1)
threads.append(thread2)

# 等待所有线程完成
for t in threads:
    t.join()
print ("Exiting Main Thread")
print('---------------------------------------')

# Condition
# Condition（条件变量）通常与一个锁关联。需要在多个Contidion中共享一个锁时，可以传递一个Lock/RLock实例给构造方法，否则它将自己生成一个RLock实例。
# 可以认为，除了Lock带有的锁定池外，Condition还包含一个等待池，池中的线程处于状态图中的等待阻塞状态，直到另一个线程调用notify()/notifyAll()通知；得到通知后线程进入锁定池等待锁定。
# 构造方法：
# Condition([lock/rlock])
# 实例方法：
# acquire([timeout])/release(): 调用关联的锁的相应方法。
# wait([timeout]): 调用这个方法将使线程进入Condition的等待池等待通知，并释放锁。使用前线程必须已获得锁定，否则将抛出异常。
# notify(): 调用这个方法将从等待池挑选一个线程并通知，收到通知的线程将自动调用acquire()尝试获得锁定（进入锁定池）；其他线程仍然在等待池中。调用这个方法不会释放锁定。使用前线程必须已获得锁定，否则将抛出异常。
# notifyAll(): 调用这个方法将通知等待池中所有的线程，这些线程都将进入锁定池尝试获得锁定。调用这个方法不会释放锁定。使用前线程必须已获得锁定，否则将抛出异常。
# 例子是很常见的生产者/消费者模式：

# 商品
product = None
# 条件变量
con = threading.Condition()

# 生产者方法
def produce():
    global product
    if con.acquire():
        while True:
            if product is None:
                print('produce')
                product = 'anything'

                # 通知消费者，商品已经生产
                con.notify()

            # 等待通知
            con.wait()
            time.sleep(2)


# 消费者方法
def consume():
    global product

    if con.acquire():
        while True:
            if product is not None:
                print('consume')
                product = None

                # 通知生产者，商品已经没了
                con.notify()

            # 等待通知
            con.wait()
            time.sleep(2)


t1 = threading.Thread(target=produce)
t2 = threading.Thread(target=consume)
# t1.start()
# t2.start()
print('---------------------------------------')


# Semaphore/BoundedSemaphore
# Semaphore（信号量）是计算机科学史上最古老的同步指令之一。Semaphore管理一个内置的计数器，每当调用acquire()时-1，调用release() 时+1。计数器不能小于0；当计数器为0时，acquire()将阻塞线程至同步锁定状态，直到其他线程调用release()。
# 基于这个特点，Semaphore经常用来同步一些有“访客上限”的对象，比如连接池。
# BoundedSemaphore 与Semaphore的唯一区别在于前者将在调用release()时检查计数器的值是否超过了计数器的初始值，如果超过了将抛出一个异常。
# 构造方法：
# Semaphore(value=1): value是计数器的初始值。
# 实例方法：
# acquire([timeout]): 请求Semaphore。如果计数器为0，将阻塞线程至同步阻塞状态；否则将计数器-1并立即返回。
# release(): 释放Semaphore，将计数器+1，如果使用BoundedSemaphore，还将进行释放次数检查。release()方法不检查线程是否已获得 Semaphore。

# 计数器初值为2
semaphore = threading.Semaphore(2)


def func():
    # 请求Semaphore，成功后计数器-1；计数器为0时阻塞
    print('%s acquire semaphore...' % threading.currentThread().getName())
    if semaphore.acquire():
        print('%s get semaphore' % threading.current_thread().getName())
        time.sleep(4)
        # 释放Semaphore，计数器+1
        print('%s release semaphore' % threading.currentThread().getName())
        semaphore.release()


t1 = threading.Thread(target=func)
t2 = threading.Thread(target=func)
t3 = threading.Thread(target=func)
t4 = threading.Thread(target=func)
t1.start()
t2.start()
t3.start()
t4.start()
time.sleep(2)

# 没有获得semaphore的主线程也可以调用release
# 若使用BoundedSemaphore，t4释放semaphore时将抛出异常
print('MainThread release semaphore without acquire')
semaphore.release()
print('---------------------------------------')


# Event
# Event（事件）是最简单的线程通信机制之一：一个线程通知事件，其他线程等待事件。Event内置了一个初始为False的标志，当调用set()时设为True，调用clear()时重置为 False。wait()将阻塞线程至等待阻塞状态。
# Event其实就是一个简化版的 Condition。Event没有锁，无法使线程进入同步阻塞状态。
# 构造方法：
# Event()
# 实例方法：
# isSet(): 当内置标志为True时返回True。
# set(): 将标志设为True，并通知所有处于等待阻塞状态的线程恢复运行状态。
# clear(): 将标志设为False。
# wait([timeout]): 如果标志为True将立即返回，否则阻塞线程至等待阻塞状态，等待其他线程调用set()。


def producer():
    print("厨师：等人来买包子")
    event.wait()                            # 等到set了才执行，否则阻塞
    print("厨师：开始包包子了")
    time.sleep(7)
    event.set()
    print("厨师：你的包子好了")


def consumer():
    print("我要吃包子")
    time.sleep(1)
    event.set()
    print("等着包包子")
    event.wait()
    while True:
        if event.is_set():
            print("真好吃")
            break
        else:
            print("怎么还没好")
            time.sleep(1)

event=threading.Event()

p1 = threading.Thread(target=producer)
p2 = threading.Thread(target=consumer)
p1.start()
p2.start()
print('---------------------------------------')

# Timer
# Timer（定时器）是Thread的派生类，用于在指定时间后调用一个方法。
# 构造方法：
# Timer(interval, function, args=[], kwargs={})
# interval: 指定的时间
# function: 要执行的方法
# args/kwargs: 方法的参数
# 实例方法：
# Timer从Thread派生，没有增加实例方法。


def func():
    print('hello timer!')

# 5秒后执行
timer = threading.Timer(5, func)
timer.start()


# 小提示
# 相同进程中的不同线程可以同时在不同的CPU中运行，但是由于GIL（ 全局解释器锁）的存在，python不具有这个能力。python一个进程同时只能执行一个线程。因此，在python开发时，计算密集型使用多进程，IO密集型使用多线程。如果计算密集的同时又有IO密集，则多线程多进程同时使用。
# 在执行一些sleep/read/write/recv/send这些会导致阻塞的函数时，当前线程会主动放弃GIL，然后调用相应的系统API，完成后再重新申请GIL。因此，GIL也并不是导致Python的多线程完全没用，在一些IO等待的场合，Python多线程还是发挥了作用，当然如果多线程都是用于CPU密集的代码，那多线程的执行效率就明显会比单线程的低。
# 进程的开销通常比线程昂贵, 因为线程自动共享内存地址空间和文件描述符. 意味着, 创建进程比创建线程会花费更多