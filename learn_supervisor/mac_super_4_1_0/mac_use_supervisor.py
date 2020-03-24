#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# Mac环境下使用supervisor
# supervisor结构
# supervisor主要由Supervisord、Supervisorctl、Web server和XML-RPC interface组成。
# Supervisord：主进程，负责管理进程的server，它会根据配置文件创建指定数量的应用程序的子进程，
# 管理子进程的整个生命周期，对crash的进程重启，对进程变化发送事件通知等。
# 同时通过内置web server和XML-RPC Interface可以轻松实现进程管理。
# Supervisorctl：管理client，用户通过命令行发送消息给supervisord，
# 可以查看进程状态，加载配置文件，启停进程，查看进程标准输出和错误输出，远程操作等。
# Web server：superviosr提供了web server功能，可通过web控制进程。
# XML-RPC interface： XML-RPC接口，提供XML-RPC服务来对子进程进行管理和监控

# 安装
# Windows和Mac下都可以使用包管理工具npm进行安装，打开终端/命令行工具，输入以下代码并执行：
# npm install supervisor -g    //windows
# sudo npm install supervisor -g    //mac
# 使用
# 启动supervisor
# python /usr/bin/supervisord
# 查看一个进程的报错
# sudo supervisorctl tail mysite stderr
# 启动监控的进程
# supervisorctl start all
# 关闭监控的进程
# supervisorctl stop all
# 查看状态
# supervisorctl status
# 重新加载配置文件：
# supervisorctl reload
# 开启 web 管理
# vi /usr/local/etc/supervisord.ini
# 将下面注释去掉
# [inet_http_server] ; inet (TCP) server disabled by default
# port=127.0.0.1:9001 ; (ip_address:port specifier, *:port for all iface)
# username=fengjx ; (default is no username (open server))
# password=fengjx1989 ; (default is no password (open server))
# 重启服务
# $ brew services start supervisor
# 进程管理
# supervisord.ini 的最后一行配置：
# files = /usr/local/etc/supervisor.d/*.ini
# 我们可以吧配置文件写到 /usr/local/etc/supervisor.d/ 目录下，只要以.ini 后缀结尾就行，例如管理nginx的状态：
# vi nginx.ini
# [program:nginx]
# command = sudo /usr/local/bin/nginx
# stdout_logfile=/data/home/supervisor/logs/nginx_stdout.log
# stdout_logfile_maxbytes=10MB
# stderr_logfile=/data/home/supervisor/logs/nginx_stderr.log
# stderr_logfile_maxbytes=10MB
# autostart=true
# autorestart=true
# ;environment = PATH="$PATH:/usr/local/bin"
# 然后，使用 supervisorctl 启动 nginx。
# supervisorctl start nginx
# 参考：
# github上2个基于supervisor二次开发的集中进程管理工具，可在一个页面下管理多台机器的进程：
# https://github.com/mlazarov/supervisord-monitor
# https://github.com/TAKEALOT/nodervisor