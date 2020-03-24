#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


from socket import *
import struct


while True:
    try:
        client = socket(AF_INET, SOCK_STREAM)
        client.connect(('127.0.0.1', 8888))
        while True:
            try:
                cmd = input('>>>>>>>:').strip().encode('utf-8')
                client.send(cmd)
                head = client.recv(4)
                size = struct.unpack('i', head)[0]
                cur_size = 0
                result = b''
                while cur_size < size:
                    data = client.recv(1024)
                    cur_size += len(data)
                    result += data
                print(result.decode('gbk'))   # windows系统默认编码是gbk，解码肯定也要用gbk
            except ConnectionResetError:
                print('服务端已中断')
                client.close()
                break

    except ConnectionRefusedError:
        print('无法连接服务端')


# 通过客户端输入命令，在服务端执行shell命令，通过服务端执行subprocess模块达到远程shell命令操作，此过程主要需要考虑2个难点，①解决命令产生结果数据的发送粘包问题，②注意返回结果的shell命令结果是gbk编码，接收后需要用gbk解码一下。