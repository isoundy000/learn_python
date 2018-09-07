# -*- encoding: utf-8 -*-
'''
Created on 2018年7月23日

@author: houguangdong
'''

# i > 5和i > 10的区别

for i in range(10):
    if i > 10:
        break
    else:
        print i
else:
    print '1111111111'


# 如何手动释放Python的内存
from time import sleep, time
import gc


def mem(way=1):
    print time()
    for i in range(10000000):
        if way == 1:
            pass
        else:  # way 2, 3
            del i

    print time()
    if way == 1 or way == 2:
        pass
    else:  # way 3
        gc.collect()
    print time()


if __name__ == "__main__":
    print "Test way 1: just pass"
    mem(way=1)
    sleep(20)
    print "Test way 2: just del"
    mem(way=2)
    sleep(20)
    print "Test way 3: del, and then gc.collect()"
    mem(way=3)
    sleep(20)

# 对于way 1和way 2，结果是完全一样的，程序内存消耗峰值是326772KB，在sleep 20秒时，内存实时消耗是244820KB；
# 对于way 3，程序内存消耗峰值同上，但是sleep时内存实时消耗就只有6336KB了。