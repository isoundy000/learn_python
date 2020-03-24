#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from socket import *
# 确定客户端传输协议（服务端和客户端服务协议一样才能进行有效的通信）
client = socket(AF_INET, SOCK_STREAM)           # 这里的SOCK_STREAM代表的就是流式协议TCP，如果是SOCK_DGRAM就代表UDP协议
# 开始连接服务端IP和PORT,建立双向链接
client.connect(('127.0.0.1', 8888))             # 通过服务端IP和PORT进行连接
# 走到这一步就已经建立连接完毕，接下来开始数据通信：
client.send('hello, server'.encode('utf-8'))    # 将发送的信息转码成Bytes类型数据

data = client.recv(1024)        # 每次最大收数据大小为1024字节（1kb）

print(data.decode('utf-8'))     # 将b类型数据转换成字符串格式

# 一次传输完毕
client.close()                  # 关闭客户端连接


# 启动服务端（服务端开始监听客户端的连接请求）
# 启动客户端（客户端给服务端发送连接请求）
# 建立双向链接完成
# 客户端给服务端发送信息 hello，server
# 服务端收到hello，server，将其转换成大写，返回给客户端（此时服务端一轮通信完毕）
# 客户端收到服务端的反馈信息，打印出HELLO，SERVER（此时客户端一轮通信完毕）
# 以上是最基本的一次基于tcp协议通信的过程客户端发，服务端收，服务端处理数据然后发，客户端收到服务端发了的反馈数据。