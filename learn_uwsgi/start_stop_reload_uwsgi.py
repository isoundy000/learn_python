#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# uwsgi服务启动(start)停止(stop)重新装载(reload)
# 1. 添加uwsgi相关文件
# 在之前的文章跟讲到过centos中搭建nginx+uwsgi+flask运行环境，本节就基于那一次的配置进行说明。
# 在www中创建uwsgi文件夹，用来存放uwsgi相关文件
# mkdir uwsgi
# 在uwsgi文件夹中创建uwsgi.pid和uwsgi.status文件，uwsgi.pid文件用来重启和停止uwsgi服务，uwsgi.status用来查看uwsgi的服务状态
# cd uwsgi
# touch uwsgi.pid
# touch uwsgi.status


# 2. 修改uwsgi配置文件
# 基于我们之前配置的uwsgin.ini文件，做如下修改，添加pid文件和status文件的配置
# stats=%(chdir)/uwsgi/uwsgi.status
# pidfile=%(chdir)/uwsgi/uwsgi.pid
# [uwsgi]
# socket = 172.20.10.11:8080
# chdir = /www
# wsgi-file = /www/Code.py
# callable = app
# processes = 4
# threads = 2
# pythonpath = /www
# daemonize = /var/log/uwsgi.log
#
# stats = %(chdir)/uwsgi/uwsgi.status
# pidfile = %(chdir)/uwsgi/uwsgi.pid


# 3. 使用命令
# 完成配置后，可以用如下命令操作uwsgi服务
# 启动
# uwsgi --ini uwsgi.ini
# 执行完成后，我们可以cat一下pid文件，发现里面出现了一个pid号
# 同时我们用ps命令查看一下uwsgi的进程，发现主进程的pid与我们的pid文件里存的是一样的

# 重启
# uwsgi --reload uwsgi/uwsgi.pid
# uwsgi --connect-and-read uwsgi/uwsgi.status
# 这个命令返回一个json串，显示进程和worker的状态很详细

# 停止
# uwsgi --stop uwsgi/uwsgi.pid
# 停止uwsgi服务后，用ps命令查看uwsgi的进程，已经不存在了
# ps aux | grep uwsgi