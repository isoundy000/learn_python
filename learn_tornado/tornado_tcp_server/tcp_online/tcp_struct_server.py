#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# 粘包问题
# 解决方法：先发个包含待发送文件大小长度的报头文件>>>>再发送原始文件
# 引入模块struct
import socket
import struct

server = socket.socket()
server.bind(('127.0.0.1', 8888))
server.listen(5)
while True:
    conn, client_addr = server.accept()
    print('客户端已连接')
    while True:
        try:
            head = conn.recv(4)
            size = struct.unpack('i', head)[0]
            data = conn.recv(size)
            print(u'已收到客户端信息：', data.decode('utf-8'))
        except ConnectionResetError:
            print('客户端已中断连接')
            conn.close()
            break