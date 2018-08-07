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