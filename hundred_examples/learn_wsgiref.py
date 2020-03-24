#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from wsgiref.simple_server import make_server


def appliaction(environ, start_responese):
    # 定义响应体
    start_responese("200 OK", [('Content-Type', 'text/html')])
    # 获取目录
    pathed = environ.get("PATH_INFO")

    # 判断并且返回login.html页面
    if pathed == "/login":
        with open("login.html", 'r') as f:
            data = f.read()
        return [data.encode("utf8")]


# 封装了socket
server = make_server("", 8800, appliaction)
#等待用户连接
server.serve_forever()