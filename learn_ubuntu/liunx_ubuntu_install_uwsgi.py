#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# linux-ubuntu安装配置uwsgi

# 对于 Python2.x 版本:（测试通过）
# 第一步:sudo apt-get install python-dev
# 第二步:sudo apt-get install python-pip
# 第三部:sudo pip install uwsgi

# 对于 Python3.x 版本:
# 第一步:sudo apt-get install python3-dev
# 第二步:sudo apt-get install python3-pip
# 第三部:sudo pip3 install uwsgi

# 测试uwsgi，创建test.py
def application(env, start_response):
    start_response('200 OK', [('Content-Type','text/html')])
    return [b"Hello uwsgi!"]

# uwsgi运行该文件
# uwsgi --http-socket :8088 --wsgi-file test.py
# http://192.168.129.129:8088/

# 第二种方式使用配置文件运行uwsgi，可以简化命令，配置文件的格式我喜欢使用ini的格式
# 任意地方创建uwsgi.ini，内容如下：
# [uwsgi]
# http-socket= :8088
# chdir=/home/xlf
# wsgi-file=test.py

# 可以这样运行
# 到uwsgi.ini目录下
# 执行 uwsgi --ini ./uwsgi.ini