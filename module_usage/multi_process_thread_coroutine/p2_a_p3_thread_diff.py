# -*- encoding: utf-8 -*-
'''
Created on 2019年11月18日 12:21

@author: houguangdong
'''

# 无论如何python都是有thread模块的，这个错误在python2不会发生。
# 但是我们用的是python3，查看了python3的改动后。
# 原来问题出现在这里：
# python3中，由于thread有两个很致命的问题，所以python3更推荐用threading代替thread，所以，thread被改名为_thread
import _thread

# 我们可以考虑这样的问题：
# 兼容python2和python3的写法：
import sys
# 如果版本号是3
if(sys.version[:1] == "3"):
    import _thread as thread
else:
    # 否则，也就是python2
    import thread


# 此时我们可以尝试创建一个线程。
def runth():
    print("thread running...")

a = _thread.start_new_thread(runth, ())
print(a)
# 可以看到thread模块正常使用


# dir()方法查看已导入模块。
print(dir())