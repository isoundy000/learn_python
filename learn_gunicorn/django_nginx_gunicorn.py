#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


# django+nginx+gunicorn部署配置
# 在部署django开发的站点时，通常有两种选择方式，nginx+django+uwsgi或者django+nginx+gunicorn，本文不讨论apache方式，在linux下通常都使用nginx，速度快，还经常做代理服务器，功能强大。。
# nginx+django+uwsgi个人觉得uwsgi配置较为麻烦，所以选择了gunicorn，一个开源Python WSGI UNIX的HTTP服务器，据说速度快（配置快、运行快）、简单，默认是同步工作，支持Gevent、Eventlet异步，支持Tornado。有兴趣可以自行查阅官方文档
# django+nginx+gunicorn
# 环境安装
# 需要在服务器端安装我们所需要的环境nginx Python nginx gunicorn...
# django等站点需要的依赖将不进行介绍
# nginx
# 在ubuntu上支持apt-get 直接安装，其他系统请自行搜索安装方式
# sudo apt-get install nginx
# gunicorn
# gunicorn只是一个Python的库 这里建议使用pip安装，简单方便
# ps:要么网络好，要么建议更改pip源为豆瓣源
# sudo pip install gunicorn
#
# nginx配置
# 一般网站都配置在80端口上，域名默认解析到80端口，所以nginx配置文件如下，在更改nginx的配置文件之前建议把默认文件进行备份，以备后续出现问题参照使用
# 打开nginx配置文件/etc/ningx/sites-enable/default
# 进行修改为如下内容:
# server {
#     listen 80;
#     server_name 192.168.84.199;
#     server_name_in_redirect off;
#     access_log /home/webserver/web/nginx.access.log;
#     error_log /home/webserver/web/nginx.error.log;
#
#     location / {
#         proxy_pass http://127.0.0.1:8000;
#         proxy_pass_header       Authorization;
#         proxy_pass_header       WWW-Authenticate;
#         proxy_set_header Host $host;
#         proxy_set_header X-Real-IP $remote_addr;
#         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#     }
#
#     location /static/ {
#         root /home/webserver/web/WebServer/;
#     }
# }
# 核心配置文件就上述那么多，重点使将请求转发到django的服务器上
# listen是所需要监听的端口
# server_name是需要绑定的域名，暂时没有域名时，请使用ip
# access_log是确定正常状态下log文件位置
# error_log使确定发生错误时log文件位置
# location / 是当访问到根下的时候，将所有请求转发到127.0.0.1:8000,本文使转发到gunicorn启动的django应用上，
# 中间配置的是需要转发的内容，基本上述内容可以满足大多需求，如需特殊需求请自行查看nginx官方文档
# location /static/ 配置了静态文件所在的路径，静态文件由nginx处理，动态转发到django，
# 如不配置会出现站点引用的所有js css都找不到
#
# gunicorn配置
# gunicorn启动一般有两种方式，可以在项目目录下建立gunicorn.conf.py配置文件，也可以在启动gunicorn时直接加上相关命令
# 需要在项目的settings.py中的INSTALLED_APPS添加gunicorn：
# INSTALLED_APPS = [
#     'gunicorn',  # 部署用
# ]
# gunicorn.conf.py文件
# import multiprocessing
#
# bind = "127.0.0.1:8000"   #绑定的ip与端口
# workers = 2                #核心数
# errorlog = '/home/xxx/xxx/gunicorn.error.log' #发生错误时log的路径
# accesslog = '/home/xxx/xxx/gunicorn.access.log' #正常时的log路径
# #loglevel = 'debug'   #日志等级
# proc_name = 'gunicorn_project'   #进程名
#
#
# 直接使用gunicron启动
# gunicron需要启动后需要长期运行在后台，如果直接启动会在关闭终端后进程就被杀死，这肯定不是我们的需求，所以这里给出两种解决方式
# 使用Linux自带的nohup命令
# 不使用gunicorn配置文件(需进入项目目录)
# sudo nohup gunicorn 项目名.wsgi:application -b 127.0.0.1:8000&
# 使用配置文件方式
# sudo nohup gunicorn 项目名.wsgi:application -c /home/xxx/xxx/gunicorn.conf.py&
#
#
#
# 使用supervistor进程管理器
# supervistor这个工具的用法这里就不在多讲，需要了解可以看我的另一篇博客ubuntu下的进程控制系统—Supervisor,也可以直接查看官方文档
# 用法可以参照我的配置文件:
# [program:x508server]
# command=gunicorn x508server.wsgi:application -b 0.0.0.0:8000  ; 被监控的进程路径
# directory=/home/webserver/web/WebServer/               ; 执行前要不要先cd到目录$
# autostart=true                ; 随着supervisord的启动而启动
# autorestart=true              ; 自动重启。。当然要选上了
# startretries=10               ; 启动失败时的最多重试次数
# exitcodes=0                   ; 正常退出代码
# stopsignal=KILL               ; 用来杀死进程的信号
# stopwaitsecs=10               ; 发送SIGKILL前的等待时间
# redirect_stderr=true          ; 重定向stderr到stdout
# stdout_logfile=/home/webserver/web/logfile.log        ; 指定日志文件
# ; 默认为 false，如果设置为 true，当进程收到 stop 信号时，会自动将该信号发给该进$
# stopasgroup=true             ; send stop signal to the UNIX process
# ; 默认为 false，如果设置为 true，当进程收到 kill 信号时，会自动将该信号发给该进$
# killasgroup=true             ; SIGKILL the UNIX process group (def false)
#
# 1 启动站点
# 加载nginx配置文件重启nginx
# sudo service nginx reload
# sudo service nginx restart
# 2 启动gunicorn
# 如果使用supervistor:
# sudo supervisorctl reload
# 如果使用nohup
# sudo nohup gunicorn 项目名.wsgi:application -b 127.0.0.1:8000&
