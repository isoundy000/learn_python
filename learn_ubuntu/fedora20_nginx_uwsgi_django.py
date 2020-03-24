#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# Fedora20 + Nginx + uWSGI + Django环境的搭建
# uwsgi的配置真不是一般的麻烦。。。
# 首先是Nginx的配置：
#
# server {
#     listen       80;
#     server_name  localhost 127.0.0.1;
#
#     # charset koi8-r;
#
#     # access_log  logs/host.access.log  main;
#
#     location / {
#         uwsgi_pass 127.0.0.1:9000;
#         include uwsgi_params;
#         access_log off;
#         root /home/celte/lovenote/my_django/my_django;#####注意此处是要指向settings.py，很容易写掉一个my_django
#     }
# }


# 然后就是uwsgi的配置(uwsgi.ini)
# [uwsgi]
# socket=127.0.0.1:9000
# listen=100
# master=true
# pidfile=/home/celte/lovenote/my_django/uwsgi.pid
# processes=8
# pythonpath=/home/celte/lovenote/my_django/
# chdir=/home/celte/lovenote/my_django/my_django
# module=my_django.wsgi:application
# profiler=true
# memory-report=true
# enable-threads=true
# logdate=true
# limit-as=6048
# daemonize=/home/celte/lovenote/my_django/log/django.log

# 在uwsgi的最开始的配置过程中，日志中出现的问题的解决如下：
# Listen queue size is greater than the system max net.core.somaxconn (128)
# 看日志很明显，是listen数目设置大了，将原来的listen由200改为100,为题解决。
# unavailable modifier requested
# 这个情况需要首先安装分别用以下命令解决
# sudo yum install uwsgi-plugin-python
# sudo pip intsall uwsgi

# 后来在我的电脑中比较奇葩，依然有这个报错，于是，一怒之下将uwsgi给卸载了，结果居然发现还有/usr/bin/uwsgi残留，不懂。于是继续删掉，重装uwsgi，
# 发现给我安装在/usr/sbin/uwsgi，这就比较奇葩，而且在pip install uwsgi后，这个uwsgi重新回到了/usr/bin/uwsgi这个位置。
# 于是开始猜测是uwsgi程序的问题，之前一直采用默认的shell下输入uwsgi来启动uwsgi，可能不行，于是改用/usr/sbin/uwsgi来启动，
# 不过此时依旧不能解决，还需要在启动的后面加上plugin参数，综上，为解决这个问题必须采用如下方式启动uwsgi
#
# /usr/sbin/uwsgi -i /home/celte/lovenote/uwsgi.ini --plugin python
# 于是问题解决。
# no python application found, check your startup logs for errors
# 又是一个蛋疼的问题，找了好久，才发现是module参数配置错误，注意，这里的module的配置一定要定位到wsgi.py文件中的application
# 附uwsgi的进程查看命令以及全部关闭命令
# ps -ax | grep uwsgi
# killall -9 uwsgi