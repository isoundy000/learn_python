# -*- encoding: utf-8 -*-
'''
Created on 2017年8月30日

@author: houguangdong
'''
# 协程
import greenlet
print dir(greenlet)
from greenlet import greenlet


def test1():
    print 12
    gr2.switch()
    print 34


def test2():
    print 56
    gr1.switch()
    print 78


gr1 = greenlet(test1)
gr2 = greenlet(test2)
gr1.switch()


print dir(greenlet)
# print dir(greenlet.greenlet)


def test3(x, y):
    z = gr4.switch(x + y)
    print ('test3', z)


def test4(u):
    print ("test4", u)
    gr3.switch(10)
    

gr3 = greenlet(test3)
gr4 = greenlet(test4)
print gr3.switch("hello", " world")


def test5(x, y):
    print id(greenlet.getcurrent()), id(greenlet.getcurrent().parent)
    z = gr6.switch(x + y)
    print 'back z', z


def test6(u):
    print id(greenlet.getcurrent()), id(greenlet.getcurrent().parent)
    return 'hehe'


gr5 = greenlet(test5)
gr6 = greenlet(test6)
print id(greenlet.getcurrent()), id(gr5), id(gr6)
print gr5.switch("hello", "world"), 'back to main'


def test7(x, y):
    try:
        z = gr8.switch(x+y)
    except Exception:
        print 'catch Exception in test1'
        

def test8(u):
    assert False
    

gr7 = greenlet(test7)
gr8 = greenlet(test8)
try:
    gr7.switch("hello", "world")
except:
    print 'catch Exception in main'


def test9():
    gr10.switch(1)
    print 'test9 finished'
    
    
def test10(x):
    print 'test10 first', x
    z = gr9.switch()
    print 'test10 back', z
    
    
gr9 = greenlet(test9)
gr10 = greenlet(test10)
gr9.switch()
print 'gr9 is dead?:%s, gr10 is dead?:%s' % (gr9.dead, gr10.dead)
gr10.switch()
print 'gr9 is dead?:%s, gr10 is dead?:%s' % (gr9.dead, gr10.dead)
print gr10.switch(10)


def test_greenlet_tracing():
    def callback(event, args):
        print event, 'from', id(args[0]), 'to', id(args[1])
    
    def dummy():
        g2.switch()
    
    def dummyexception():
        raise Exception('except in coroutine')
    
    main = greenlet.getcurrent()
    g1 = greenlet(dummy)
    g2 = greenlet(dummyexception)
    print 'main id %s, gr1 id %s, gr2 is %s' % (id(main), id(g1), (g2))
    oldtrace = greenlet.settrace(callback)
    try:
        g1.switch()
    except:
        print 'Exception'
    finally:
        greenlet.settrace(oldtrace)
        

from greenlet import GreenletExit
huge = []

def show_leak():
    def test11():
        gr12.switch()
        
#     def test12():
#         huge.extend([x*x for x in range(100)])
#         gr11.switch()
#         print 'finish switch del huge'
#         del huge[:]

    def test12():
        huge.extend([x*x for x in range(100)])
        try:
            gr11.switch()
        finally:
            print 'finish switch del huge'
            del huge[:]
    
    gr11 = greenlet(test11)
    gr12 = greenlet(test12)
    gr11.switch()
    gr11 = gr12 = None
    print 'length of huge is zero ? %s' % len(huge)


if __name__ == '__main__':
    test_greenlet_tracing()
    show_leak()