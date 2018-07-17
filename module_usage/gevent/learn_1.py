# -*- encoding: utf-8 -*-
'''
Created on 2018年5月11日

@author: houguangdong
'''
import gevent
from gevent.event import Event

evt = Event()
def setter():
    print "A: Hey wait for me, I have to do something"
    gevent.sleep(3)
    print "OK, I'm done"
    evt.set()
    
