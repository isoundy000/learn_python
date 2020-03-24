#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import socket

client = socket.socket(type=socket.SOCK_DGRAM)
server_addr = ('127.0.0.1', 8888)

client.sendto(b'hello server baby', server_addr)
msg, addr = client.recvfrom(1024)
print(msg, addr)

# udp特点 >>> 无链接,类似于发短信，发了就行对方爱回不回，没有任何关系
# 将服务端关了，客户端起起来照样能够发数据。因为不需要考虑服务端能不能收到


# 验证udp协议有无粘包问题
# import socket
# client = socket.socket(type=socket.SOCK_DGRAM)
# server_addr = ('127.0.0.1', 8888)
# client.sendto(b'hello',server_addr)
# client.sendto(b'hello',server_addr)
# client.sendto(b'hello',server_addr)


# UDP协议下通信利用socketserver模块实现多客户端并发通信
# 客户端1、2、3、4...
from _socket import *

client = socket(AF_INET, SOCK_DGRAM)

while True:
    client.sendto(b'dddddddd', ('127.0.0.1', 8889))
    data, addr = client.recvfrom(1024)
    print(data.decode('utf-8'))