#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/12/8 18:39

import time
from celery import Celery

# Celery的第一个参数是当前模块名称，这个参数是必须的，
# 第二个参数是中间人关键字参数，指定我们所使用的的消息中间人的URL，这里我们使用的是RabbitMQ。
# app = Celery('tasks', broker='amqp://guest@localhost//')
# 1：celery 没有设置 backend 参数，设置后，才能有任务结果的保存
app = Celery()                          # 独立的职程(Worker)进程
app.config_from_object("celeryconfig")  # 你可以调用 config_from_object() 来让 Celery 实例加载配置模块：

# 要验证你的配置文件可以正确工作，且不包含语法错误，你可以尝试导入它：
# python -m celeryconfig

# 例如你可以通过修改 CELERY_TASK_SERIALIZER 选项来配置序列化任务载荷的默认的序列化方式：
app.conf.CELERY_TASK_SERIALIZER = 'json'

# 如果你一次性设置多个选项，你可以使用 update
app.conf.update(
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    # CELERY_TIMEZONE='Europe/Oslo',
    CELERY_ENABLE_UTC=True,
)



@app.task
def hello_world():
    return 'hello world'


@app.task
def taskA(x, y):
    return x + y


@app.task
def taskB(x, y, z):
    return x + y + z


@app.task(name='add', ignore_result=False, serializer='json')
def add(x, y):
    return x + y


@app.task
def cut(a, b):
    return a - b



# 视频压缩
@app.task
def video_compress(video_name):
    time.sleep(2)
    print(u'Compressing the:', video_name)
    return 'success'


@app.task
def video_upload(video_name):
    time.sleep(1)
    print(u'正在上传视频')
    return 'success'


# 压缩照片image_compress
@app.task
def image_compress(image_name):
    time.sleep(2)
    print('Compressing the:', image_name)
    return 'success'


# 其他任务
@app.task
def other(str):
    time.sleep(3)
    print('Do other things')
    return 'success'