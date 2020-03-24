#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from socket import *
import time
server_addr = ('127.0.0.1', 8888)
count = 1
while True:
    if count > 10:
        time.sleep(1)
        print('%s|连接%s超时' % (time.strftime('%Y-%m-%d %H:%M:%S'), server_addr))
        break
    try:
        client = socket(AF_INET, SOCK_STREAM)
        client.connect(('127.0.0.1', 8888))
        count = 1
        print('%s|服务端%s连接成功' % (time.strftime('%Y-%m-%d %H:%M:%S'), server_addr))
        while True:
            try:
                client.send('北鼻'.encode('utf-8'))
                data = client.recv(1024)
                print(data.decode('utf-8'))
                time.sleep(0.5)
            except ConnectionResetError:
                print('%s|服务端%s已中断' % (time.strftime('%Y-%m-%d %H:%M:%S'), server_addr))
                client.close()
                break
    except ConnectionRefusedError:
        print('无法连接到服务端')
        count += 1

# 同时再添加客户端2、客户端3，将发送数据稍微修改一下，实现多客户端并发通信服务端。