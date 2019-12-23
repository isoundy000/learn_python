#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/12/8 15:56

from tasks import *
# 可以在应用程序中使用 delay()或者 apply_async()方法来调用任务。
# 然后使用delay()方法将任务发送到消息中间件，我们之前开启的那个Worker会一直监控任务队列，知道有任务到来，就会执行
# re1 = taskA.delay(100, 200)
# result.ready()                # 查看任务执行的状态，此刻任务没有执行完成，显示False
# print(re1.get())                # 获取任务的执行结果

# re2 = taskB.delay(1, 2, 3)
# print(re2.get())

re3 = add.delay(1, 2)
print(re3.status)
print(re3.get())