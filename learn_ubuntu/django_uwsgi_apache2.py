#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# django+uwsgi+apache2，djangouwsgi
# 之前项目是用 mod-python 部署django.由于django 自1.5 版本以后将不再支持 mod-python,故比较之后，选择了一个比较成功的 uWSGI 作为替代方案。
# 看到网上大部分资料都是基于 nginx + uwsgi 部署的，故把自己的使用过程记录下来以便跟大家分享。
# 我们的系统平台是 Linux ，以下为具体操作过程：
# 1. 安装 uwsgi
# pip install uwsgi 使用 python pip 来安装，如果安装失败，可能是python版本问题(apt-get install py
# 2. 安装 apache2 的 uwsgi 模块
#      通过执行 apt-cache search mod-uwsgi 找到 libapache2-mod-uwsgi 模块，执行 apt-get install libapache2-mod-uwsgi 进行安装
#      安装成功以后 可以进入/etc/apache2/mods-available 目录查看是否存在uwsgi.load， 如果存在，说明uwsgi 已经可用,否则的话还需要在 http.conf 里配置load module部分
# 3. 关键一步，对 uwsgi 以及 apache2 的相关部分进行配置
#   a. uwsgi.ini
#       mkdir /etc/uwsgi
#       vi /etc/uwsgi/uwsgi.ini
#       uwsgi log: mkdir /var/log/uwsgi
#       一般情况下我是把 /var/log/uwsgi 权限设置为可执行，此目录下的文件任何用户均可以创建
# ini 内容如下
# [uwsgi]
# # Django-related settings
# # the base directory (full path)
# chdir           = /django/project/
# # Django's wsgi file
# module          = project.wsgi
# # the virtualenv (full path)  生产环境可忽略
# #home            = /path/to/virtualenv
# # env
# env DJANGO_SETTINGS_MODULE=server.settings
#
# # process-related settings
# # master
# master          = true
# # maximum number of worker processes
# processes       = 4
# # the socket (use the full path to be safe
# #socket          = /var/log/mysite.sock
# socket          = 127.0.0.1:8090
# # ... with appropriate permissions - may be needed
# # chmod-socket    = 664
# # max requests
# max-requests    = 100
#
# # clear environment on exit
# vacuum          = true
#
# # daemon
# daemonize    =/var/log/uwsgi/uwsgi.log
#
#   b. apache2 部分配置， 在/etc/apache2/ 目录下
#
#   需要配置相关的location 部分, 如果你的这部分配置在 httpd.conf 中，那么就在此修改，如果没有，就查找sites-available 目录default 查找。
#
# <Location "/">
#     SetHandler uwsgi-handler
#     uWSGISocket 127.0.0.1:8090
# </Location>
# 4. 上述配置成功完成以后，需要启动相关服务
#      首先启动 uwsgi
#     uwsgi --ini /etc/uwsgi/uwsgi.ini
#     然后启动 apache
#     sudo /etc/init.d/apache2 restart
# 5. tail -f /var/log/uwsgi/uwsgi.log
# 一切正常，大功告成啦！