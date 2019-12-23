#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/12/8 21:47

from tasks import app
from tasks import add
from celery.result import AsyncResult

# 异步获取任务返回值
# async_task = AsyncResult(id="d00371ec-3672-4b75-a91c-b1cf57e655a5", app=app)
# # 判断异步任务是否执行成功
# if async_task.successful():
#     # 获取异步任务的返回值
#     result = async_task.get()
#     print(result, '1111111111')
# else:
#     print("任务还未执行完成")
# print('------------------------------------------------')

result = add.delay(2, 6)
print(add.__name__)
print(result.ready())                        # 查看任务执行的状态，此刻任务没有执行完成，显示False True表示执行结果结束
# print(result.get(timeout=1))               # 你可以等待任务完成，但这很少使用，因为它把异步调用变成了同步调用:
print(result.get(), '2222222222222222')      # 获取任务的执行结果
print('------------------------------------------------')

from tasks import cut
cc = cut.delay(100, 1)
print(cc.get(), '33333333333333333333333333')
print(cc.backend)
print(result.get(propagate=True), '44444')   # 倘若任务抛出了一个异常， get() 会重新抛出异常， 但你可以指定 propagate 参数来覆盖这一行为:
print(result.traceback)                      # 如果任务抛出了一个异常，你也可以获取原始的回溯信息:
print('------------------------------------------------')

from tasks import hello_world
print(hello_world.delay(), '-----')

# 如果你使用 RabbitMQ 或 Redis 作为中间人，那么你也可以在运行时直接在职程上设置速率限制：
# celery control rate_limit tasks.add 10/m

# Debian 最近把 /dev/shm/ 特殊文件重命名为 /run/shm 。
# 简单的处置方式就是创建一个符号链接：
# ln -s /run/shm /dev/shm

# 如果你提供了 --pidfile 、 --logfile 或 --statedb 参数中的任意一个，那么你必须确保它们指向了启动职程的那个用户可写可读的文件/目录。