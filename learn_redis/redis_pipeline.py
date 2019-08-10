# -*- encoding: utf-8 -*-
'''
Created on 2018年5月26日

@author: houguangdong
'''

# Python
# Redis
# pipeline操作
# Redis是建立在TCP协议基础上的CS架构，客户端client对redis
# server采取请求响应的方式交互。
#
# 一般来说客户端从提交请求到得到服务器相应，需要传送两个tcp报文。
#
# 设想这样的一个场景，你要批量的执行一系列redis命令，例如执行100次get
# key，这时你要向redis请求100次 + 获取响应100次。如果能一次性将100个请求提交给redis
# server，执行完成之后批量的获取相应，只需要向redis请求1次，然后批量执行完命令，一次性结果，性能是不是会好很多呢？
#
# 答案是肯定的，节约的时间是客户端client和服务器redis
# server之间往返网络延迟的时间。这个时间可以用ping命令查看。
#
# 网络延迟高：批量执行，性能提升明显
#
# 网络延迟低（本机）：批量执行，性能提升不明显
#
# 某些客户端（java和python）提供了一种叫做pipeline的编程模式用来解决批量提交请求的方式。
#
# 这里我们用python客户端来举例说明一下。
#
#
#
# 1、pipeline
#
# 网络延迟
#
# client与server机器之间网络延迟如下，大约是30ms。
#
# 测试用例
#
# 分别执行其中的try_pipeline和without_pipeline统计处理时间。

# -*- coding:utf-8 -*-

import redis
import time
from concurrent.futures import ProcessPoolExecutor

r = redis.Redis(host='127.0.0.1', port=6379)


def try_pipeline():
    start = time.time()
    with r.pipeline(transaction=False) as p:
        p.sadd('seta', 1).sadd('seta', 2).srem('seta', 2).lpush('lista', 1).lrange('lista', 0, -1)
        p.execute()
    print time.time() - start


def without_pipeline():
    start = time.time()
    r.sadd('seta', 1)
    r.sadd('seta', 2)
    r.srem('seta', 2)
    r.lpush('lista', 1)
    r.lrange('lista', 0, -1)
    print time.time() - start


def worker():
    while True:
        try_pipeline()

with ProcessPoolExecutor(max_workers=12) as pool:
    for _ in range(10):
        pool.submit(worker)

# 结果分析
#
# try_pipeline平均处理时间：0.04659
#
# without_pipeline平均处理时间：0.16672
#
# 我们的批量里有5个操作，在处理时间维度上性能提升了4倍！
#
# 网络延迟大约是30ms，不使用批量的情况下，网络上的时间损耗就有0
# .15
# s（30
# ms * 5）以上。而pipeline批量操作只进行一次网络往返，所以延迟只有0
# .03
# s。可以看到节省的时间基本都是网路延迟。
#
#
#
# 2、pipeline与transation
#
# pipeline不仅仅用来批量的提交命令，还用来实现事务transation。
#
# 这里对redis事务的讨论不会太多，只是给出一个demo。详细的描述你可以参见这篇博客。redis事务
#
# 细心的你可能发现了，使用transaction与否不同之处在与创建pipeline实例的时候，transaction是否打开，默认是打开的。


# import redis
# from redis import WatchError
# from concurrent.futures import ProcessPoolExecutor
#
# r = redis.Redis(host='127.0.0.1', port=6379)
#
#
# # 减库存函数, 循环直到减库存完成
# # 库存充足, 减库存成功, 返回True
# # 库存不足, 减库存失败, 返回False
# def decr_stock():
#
#     # python中redis事务是通过pipeline的封装实现的
#     with r.pipeline() as pipe:
#         while True:
#             try:
#                 # watch库存键, multi后如果该key被其他客户端改变, 事务操作会抛出WatchError异常
#                 pipe.watch('stock:count')
#                 count = int(pipe.get('stock:count'))
#                 if count > 0:  # 有库存
#                     # 事务开始
#                     pipe.multi()
#                     pipe.decr('stock:count')
#                     # 把命令推送过去
#                     # execute返回命令执行结果列表, 这里只有一个decr返回当前值
#                     print pipe.execute()[0]
#                     return True
#                 else:
#                     return False
#             except WatchError, ex:
#                 # 打印WatchError异常, 观察被watch锁住的情况
#                 print ex
#                 pipe.unwatch()
#
#
# def worker():
#     while True:
#         # 没有库存就退出
#         if not decr_stock():
#             break
#
#
# # 实验开始
# # 设置库存为100
# r.set("stock:count", 100)
#
# # 多进程模拟多个客户端提交
# with ProcessPoolExecutor(max_workers=2) as pool:
#     for _ in range(10):
#         pool.submit(worker)


if __name__ == '__main__':
    without_pipeline()
    # a()