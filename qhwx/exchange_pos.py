#!/usr/bin/env python
#-*- coding: UTF-8 -*-


def b(pos, cid):
    if cid in a:
        a[a.index(cid)] = 0
    a[pos - 1] = cid
    return a


def f(c, d):
    tmp_value = [0, 0, 0, 0]
    tmp_percent = [0, 0, 0, 0]
    for i in range(3):
        tmp_value = map(lambda (a, b): a + b, zip(tmp_value, c))
        tmp_percent = map(lambda (a, b): a + b, zip(tmp_percent, d))
    return tmp_value, tmp_percent


class C:

    @classmethod
    def a(self):
        print '111111111'



######################################################################
class A:

    def __init__(self, pos):
        self.pos = pos
        self.effects = {}

    @classmethod
    def _install(cls, pos):
        a = cls(pos)
        return a

    def z(self):
        print self.pos, isinstance(self, A)
        return self.pos


class B:

    def __init__(self, pos):
        self.pos = pos
        self.effects = {}

    @classmethod
    def _install(cls, pos):
        b = cls(pos)
        b.effects[pos] = A._install(pos)
        return b

    def f(self):
        print self.pos, isinstance(self, B), '111111111', self.effects.get(self.pos)
        print self.effects.get(self.pos).z()


class D:

    def __init__(self):
        self.ao_effect = {}

    @classmethod
    def _install(cls):
        d = cls()
        for i in range(1, 13):
            d.ao_effect[i] = B._install(i)
        return d

    def get_d(self, pos):
        print self.ao_effect.get(pos)
        self.ao_effect.get(pos).f()


from functools import wraps

def c(func):
    @wraps(func)
    def wapper(*k):
        print k, '111111'
        func()
    return wapper

def d(func):
    @wraps(func)
    def wapper(*k):
        print k, '222222'
        func()
    return wapper


def z(func):
    @wraps(func)
    def wapper(*k):
        print k, '333333'
        func()
    return wapper

def ff():
    return 1

def zz():
    return 2

cc = {
    0: ff,
    1: zz
}


print cc.get(0, None), '--------'

@z
@d
@c
def k():
    print '000000'


class LianXi:

    def __enter__(self):
        return 1, 2

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

lian_xi = LianXi()
with lian_xi as lx:
    c, d = lx[0], lx[1]
    print c, d, 'ffffffffffffffffffff'

######################################################################


if __name__ == '__main__':
    a = [0, 0, 0, 0, -1, -1, -1, -1]
    b(1, 1005)
    print a
    b(2, 1006)
    print a
    b(2, 1007)
    print a
    b(1, 1006)
    print a
    b(1, 1007)
    print a
    b(2, 1005)
    b(3, 1006)
    b(3, 1007)
    print a
    print f([1, 2, 3, 4], [1, 2, 3, 4])
    c = C()
    print c.a() == C.a()
    d = D._install()
    d.get_d(5)
    k()