#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# supervisor的版本
# /usr/local/opt/supervisor/bin/supervisord -v     4.1.0

# supervisor 管理进程 基本用法
# 1. 我们使用brew管理,先搜索一下确认是否有我们需要的软件包
# brew search supervisor
# 2. 执行安装
# brew install supervisor
# 3. 启动程序
# brew services start supervisor
# 4. ps 查看进程是否启动成功
# ps aux|grep supervisor
# /usr/local/Cellar/supervisor/3.3.4/libexec/bin/python2.7 /usr/local/opt/supervisor/bin/supervisord -c /usr/local/etc/supervisord.ini --nodaemon
# grep --color=auto --exclude-dir=.bzr --exclude-dir=CVS --exclude-dir=.git --exclude-dir=.hg --exclude-dir=.svn supervisor
# 5. supervisord.ini 配置
# /usr/local/etc/supervisord.ini
# 配置文件末尾有一个载入配置的路径
# [include]
# files = /usr/local/etc/supervisor.d/*.ini
# 然后我们新建一个supervisor.d目录
# mkdir supervisor.d
# 然后我们进入到这个目录中,新建一个xxx.ini文件,就可以写我们自己的配置了,就像nginx server目录下一样的道理
# 6.配置项,参数详情:https://blog.51cto.com/lixcto/1539136
# [program:weatherApi]
# directory = /Users/davis/python_prduction/weather
# command = /usr/local/bin/python3.7 /Users/davis/python_prduction/weather/index.py
# autostart = true
# startsecs = 3
# autorestart = true
# startretries = 3
# user = davis
# redirect_stderr = true
# stdout_logfile_backups = 20
# stdout_logfile=/Users/davis/logs/weather_api_success.log
# stdout_logfile_maxbytes=10MB
# 然后保存退出,/usr/local/etc,退到这个路径
# supervisorctl -c supervisord.ini
# reload
# start weatherApi 启动
# stop weatherApi 停止