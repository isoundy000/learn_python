#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Python程序退出: os._exit()和sys.exit()
# 概述
# Python程序有两种退出方式： os._exit() 和 sys.exit()。我查了一下这两种方式的区别。
# os._exit() 会直接将python程序终止，之后的所有代码都不会执行。
# sys.exit() 会抛出一个异常: SystemExit，如果这个异常没有被捕获，那么python解释器将会退出。如果有捕获该异常的代码，那么这些代码还是会执行。
# 举个例子
import os

try:
    os._exit(0)
except:
    print('Program is dead.')

# 这个print是不会打印的，因为没有异常被捕获。
import sys

try:
    sys.exit(0)
except:
    print('Program is dead.')
finally:
    print('clean-up')

# 这里两个print都可以打印，因为sys.exit()抛出了异常。
# 结论
# 使用sys.exit()来退出程序比较优雅，调用它能引发SystemExit异常，然后我们可以捕获这个异常做些清理工作。而os._exit()将python解释器直接退出，后面的语句都不会执行。
# 一般情况下用sys.exit()就行；os._exit()可以在os.fork()产生的子进程里使用。