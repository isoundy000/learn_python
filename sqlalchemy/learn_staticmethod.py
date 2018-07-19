#!/usr/bin/env python
#coding: utf-8

a = ['game_59', 'game_42', 'game_77', 'game_76', 'game_75', 'game_74', 'game_73', 'game_71', 'game_79', 'game_78']
b = ['game_59', 'game_42', 'game_77', 'game_76', 'game_75', 'game_79', 'game_78']
c = -1
d = []

d = list(set(a) - set(b))
print d


class B():
    c = None


class A():
    _queue = None

    def _init():
        print '111111111'
        A._queue = B()

    def _push(task):
        print '2222222222%s' % task
        A._queue.put(task)

    Push = staticmethod(_push)

    Init = staticmethod(_init)

a = A()
A.Init()
# A.Push()