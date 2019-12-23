# -*- encoding: utf-8 -*-
'''
Created on 2019年11月19日 11:06

@author: houguangdong
'''

import time
import _thread


def foo(tag, delay):
    count = 0
    while count < 5:
        time.sleep(delay)
        count += 1
        print("%s:%s" % (tag, time.ctime(time.time())))


try:
    _thread.start_new_thread(foo, ("thread1", 10))
    _thread.start_new_thread(foo, ("thread2", 5))
except:
    print("error")


while(1):
    pass