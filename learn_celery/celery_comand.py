#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/12/8 17:25
# 启动两个worker来分别指定taskA、taskB，开两个窗口分别执行下面语句。
# celery -A tasks worker -l info -n workerA.%h -Q for_task_A
# celery -A tasks worker -l info -n workerB.%h -Q for_task_B
# celery -A tasks worker -l info -n worker.%h -Q default
# celery -A tasks worker -l info -n workerC.%h -Q videos
# 参数-A指定了Celery实例的位置，这个实例是在tasks.py文件中，Celery会自动在该文件中查找Celery对象实例。

# 启动定时任务
# celery -A tasks beat


# concurrency 表示开启多少个线程
# celery -A tasks worker -l info --concurrency=40 -n worker1.%h -Q for_task_A
# celery -A tasks worker -l info --concurrency=40 -n worker2 -Q for_task_B
# The hostname argument can expand the following variables:
# %h: Hostname including domain name.
# %n: Hostname only.
# %d: Domain name only.

# Stopping the worker
# ps aux | grep 'worker' | awk '{print $2}' | xargs kill -9

# Restarting the worker
# kill -HUP $pid


# 启动多个celery worker，这样即使一个worker挂掉了其他worker也能继续提供服务
# // 启动三个worker：w1,w2,w3
# celery multi start w1 -A project -l info
# celery multi start w2 -A project -l info
# celery multi start w3 -A project -l info
# // 立即停止w1,w2，即便现在有正在处理的任务
# celery multi stop w1 w2
# // 重启w1
# celery multi restart w1 -A project -l info
# // celery multi stopwait w1 w2 w3    # 待任务执行完，停止

# // 启动多个worker，但是不指定worker名字
# // 你可以在同一台机器上运行多个worker，但要为每个worker指定一个节点名字，使用--hostname或-n选项
# // concurrency指定处理进程数，默认与cpu数量相同，因此一般无需指定
# $ celery -A proj worker --loglevel=INFO --concurrency=10 -n worker1@%h
# $ celery -A proj worker --loglevel=INFO --concurrency=10 -n worker2@%h
# $ celery -A proj worker --loglevel=INFO --concurrency=10 -n worker3@%h