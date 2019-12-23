#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/12/8 15:55

from kombu import Exchange, Queue
from celery.schedules import crontab
# 配置市区
CELERY_TIMEZONE = 'Asia/Shanghai'

# broker_url = 'amqp://guest:guest@localhost:5672//'
BROKER_URL = 'redis://localhost:6379/13'                # 职程(Worker)进程

CELERY_RESULT_BACKEND = 'redis://localhost:6379/12'
# URL 的格式为:
# redis://:password@hostname:port/db_number
# 使用一个数据库存储后端，你必须配置 result_backend 设置为一个连接的URL，并且带 db+ 前缀：
# result_backend = 'db+scheme://user:password@host:port/dbname'

# cache后端设置
# 缓存后端支持 pylibmc 和 python-memcached 库。后者只有在 pylibmc 没有安装时才会被使用。
# 使用一个 Memcached 服务器
# result_backend = 'cache+memcached://127.0.0.1:11211'
# 使用多个 Memcached 服务器：
# result_backend = """
#     cache+memcached://172.19.26.240:11211;172.19.26.242:11211/
# """.strip()

# 可见性超时时间定义了等待职程在消息分派到其他职程之前确认收到任务的秒数
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}      # 1 hour.


# 再出现worker接受到的message出现没有注册的错误时, 使用下面一句能解决
# # 5、task注册
# # 关于任务的名字可以看看这篇文档http://docs.jinkan.org/docs/celery/userguide/tasks.html
# # celery可以自动生成名字，如果任务没有注册，就会出错。搜索后发现有人使用下面方法解决。
CELERY_IMPORTS = ("tasks",)

# 2、创建队列和交换机
# 关于交换机和队列可以先看看http://rabbitmq.mr-ping.com/
# 定义一个默认的交换机
default_exchange = Exchange('default', type='direct')        # type直连

# 定义一个媒体交换机
media_exchange = Exchange('media', type='direct')
# 通过CELERY_ROUTES来为每一个task指定队列，如果有任务到达时，通过任务的名字来让指定的worker来处理。
# 创建三个队列, 一个是默认队列, 一个是video, 一个image
CELERY_QUEUES = (
    Queue('default', default_exchange, routing_key='default'),
    Queue("for_task_A", Exchange("for_task_A"), routing_key="for_task_A"),
    Queue("for_task_B", Exchange("for_task_B"), routing_key="for_task_B"),
    Queue('videos', media_exchange, routing_key='media.video'),
    Queue('images', media_exchange, routing_key='media.image'),
)

CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_EXCHANGE = 'default'
CELERY_DEFAULT_ROUTING_KEY = 'default'

# 要证明配置文件的强大，比如这个例子展示了如何把“脏活”路由到专用的队列：路由
CELERY_ROUTES = {
    'tasks.taskA': {"queue": "for_task_A", "routing_key": "for_task_A"},
    'tasks.taskB': {"queue": "for_task_B", "routing_key": "for_task_B"},
    'tasks.image_compress': {'queue': 'images', 'routing_key': 'media.image'},
    'tasks.video_upload': {'queue': 'videos', 'routing_key': 'media.video'},
    'tasks.video_compress': {'queue': 'videos', 'routing_key': 'media.video'},
}

CELERYBEAT_SCHEDULE = {
    'taskA_schedule': {
        'task': 'tasks.taskA',
        'schedule': 2,
        'args': (5, 6)
    },
    'taskB_scheduler': {
        'task': "tasks.taskB",
        "schedule": 10,
        "args": (10, 20, 30)
    },
    'add_schedule': {
        "task": "add",
        "schedule": 50,
        "args": (1, 2)
    },
    'cut_schedule': {
        "task": "tasks.cut",
        "schedule": crontab(minute=1),
        "args": (2, 1)
    }
}