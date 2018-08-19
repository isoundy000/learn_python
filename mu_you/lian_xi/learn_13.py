# -*- encoding: utf-8 -*-
'''
Created on 2018年7月23日

@author: houguangdong
'''
SingleEnemyCheckOrder = [0]

def SingleEnmeyCheckOrderInit():
    for pos in range(1, 15):
        checkOrder = None
        if pos > 7:
            pos -= 7
            checkOrder = SingleEnemyCheckOrder[pos]
        else:
            checkOrder = []
            def ComputeFirstRowPosFirst(l1, pos):
                def Appendnique(l2, i):
                    if i not in l2:
                        l2.append(i)
                Appendnique(l1, pos)
                if pos - 1 > 0:
                    Appendnique(l1, pos - 1)
                if pos + 1 < 8:
                    Appendnique(l1, pos + 1)
                Appendnique(l1, pos + 7)
            ComputeFirstRowPosFirst(checkOrder, pos)
            for i in range(1, 7):
                if pos - i > 0:
                    ComputeFirstRowPosFirst(checkOrder, pos - i)
                if pos + i < 8:
                    ComputeFirstRowPosFirst(checkOrder, pos + i)
        SingleEnemyCheckOrder.append(checkOrder)
        print SingleEnemyCheckOrder

        
SingleEnmeyCheckOrderInit()   

import time
for pos in range(1, 7):
    for i in range(-1, 2):
        print pos + i
        print pos + i + 7
    print '-----------'



class CampOfWarData:

    __instance = None

    @staticmethod
    def singleton():
        print '3333333'
        if not CampOfWarData.__instance:
            print '44444444'
            CampOfWarData.__instance = CampOfWarData()
        print '55555555'
        return CampOfWarData.__instance

    def __init__(self):
        print '000000'
        self.__init_config()

    def __init_config(self):
        print '111111'
        pass

    def _c(self):
        print '7777777'
        pass


b = CampOfWarData.singleton()
c = CampOfWarData.singleton()
print b, c
print b._c()


def f():
    return 1, 2


z = f()
for i in z:
    print i


class B:

    def __new__(cls, *args, **kwargs):
        cls._attrs_base = {
            'version': 0
        }
        return object.__new__(cls)

    def __init__(self):
        self.base = {}
        if hasattr(self, '_attrs'):
            self.base.update(self._attrs)
            print self.base, '3333333'
        else:
            print '11111111'


class C():

    base = {}

    def __init__(self):
        if hasattr(self, '_attrs'):
            self.base.update(self._attrs)
            print('111111')
        else:
            print('22222222')

c = C()
print c.base
c1 = C()
c1._attrs = {'level': 1}
print c1.base