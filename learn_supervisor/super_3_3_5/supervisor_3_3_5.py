#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# /usr/local/bin/supervisord -v
# /usr/local/bin/supervisorctl -c

# Supervisor 配置过程
# (转自https://www.izixia.cn/2016/01/03/supervisor-pei-zhi-guo-cheng/)
# 1.安装
# pip install supervisor 安装后测试是否成功echo_supervisord_conf
# 2.建立配置文件
# 创建目录
# mkdir -m 755 -p /etc/supervisor/
# mkdir -m 755 conf.d
# echo_supervisord_conf > /etc/supervisor/supervisord.conf
# 在conf.d 文件夹中创建配置文件如app.ini
# [program:pmapp]
# command=python3 /home/keith/temp/app.py
# autorestart=true
# stdout_logfile=/home/keith/temp/supervisord_stdout.log
# stderr_logfile=/home/keith/temp/supervisord_stderr.log
# [supervisord]
# app.py的内容如下，功能是一个每五秒在写入一条记录：
#
# import time
#
# def log():
#     while True:
#         with open('a.txt', 'a') as f:
#             s = 'log:%s \n' % time.strftime('%H:%M:%S')
#             f.write(s)
#             print(s)
#         time.sleep(5)
# log()
# 3.添加配置文件到主配置文件
# 打开/etc/supervisor/supervisord.conf 文件，到最后一行可以看到
# ;[include]
# ;files = /relative/dictory/*.ini
# 删除这里的分号，然后添加我们配置文件/etc/supervisor/conf.d/app.ini，修改后如下
# [include]
# files = /etc/supervisor/conf.d/*.ini /etc/supervisor/example.ini
# 多个路径用空格隔开就可以了
# 4.启动supervisor
# supervisor有两个命令，supervisord和supervisorctl，通过supervisord管理启动和配置supervisor本身，通过supervisorctl来管理使用supervisor启动和管理的自身的一些应用，如我们的这里的app.py
# 启动supervisor 用命令
# supervisord -c /etc/supervisor/supervisord.conf
# 关闭supervisor 用命令
# supervisorctl shutdown
# 如果先建的app.ini(控制文件)，在使用启动命令后这些经过配置的程序也会启动
# 启动程序app.py
# supervisorctl start program_name
# 这里的program的name是配置文件ini中的[program:name]，所以这里的program_name是pmapp
# 关闭程序app.py
# supervisorctl stop program_name
# 刷新配置文件 如果启动后，修改了ini文件，可以通过reload命令来刷新
# supervisorctl reload
# 查看supervisor的运行状态
# ps -efH|grep supervisor
# 这里提醒一下如果按以上操作出现以下error:
# Error: .ini file does not include supervisorctl section
# For help, use /usr/local/bin/supervisorctl -h
# 或者
# error: <class 'socket.error'>, [Errno 101] Network is unreachable: file: /usr/lib/python2.7/socket.py line: 571
# 切换到/etc/supervisor目录执行以上的命令
# 执行supervisorctl start APP_NAME 或者执行 supervisorctl 的相关命令，如果出现
# unix:///tmp/supervisor.sock no such file
# 说明 Supervisord 服务还没有启动，检查你的 supervisord.conf 文件最后的注释 ; 取消，files 路径没有问题
# [include]
# files = ./conf.d/*.ini
# 之后在目录 /etc/supervisor 下重新运行
# supervisord -c /etc/supervisor/supervisord.conf
# 最后附上 supervisord 服务运行命令
# 重新 read 配置文件: supervisorctl reread
# 重启服务: supervisorctl reload
# 关闭服务: supervisorctl shutdown