#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# 绝对导入：
# from __future__ import absolute_import

import logging
from celery import shared_task
from celery import Celery
import celery

app = Celery()

@shared_task
def add(x, y):
    return x + y


# 绑定任务  一个绑定任务意味着任务函数的第一个参数总是任务实例本身(self)
@app.task(bind=True)
def add1(self, x, y):
    logging.info(self.request.id)
# 绑定任务在这些情况下是必须的：任务重试（使用 app.Task.retry() )，访问当前任务请求的信息，以及你添加到自定义任务基类的附加功能。

# 任务继承
# 任务装饰器的 base 参数可以声明任务的基类：
class MyTask(celery.Task):

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print('{0!r} failed: {1!r}'.format(task_id, exc))


@app.task(base=MyTask)
def add2(x, y):
    raise KeyError()

# 任务名称
@app.task(name='sum-of-two-numbers')
def add3(x, y):
    return x + y

print add3.name

@app.task(name='tasks.add4')
def add4(x, y):
    return x + y

print add4.name