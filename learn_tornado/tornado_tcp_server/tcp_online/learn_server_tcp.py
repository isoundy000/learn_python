#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from socket import *
# 确定服务端传输协议
server = socket(AF_INET, SOCK_STREAM)   # 这里的SOCK_STREAM代表的就是流式协议TCP，如果是SOCK_DGRAM就代表UDP协议
# 固定服务端IP和PORT，让客户端能够通过IP和端口访问服务端
server.bind(('127.0.0.1', 8888))      # ('127.0.0.1', 8080)这里必须用元组形式传入IP和PORT，本地访问本地IP默认为'127.0.0.1'
# 设置半连接池数量（一般为5）
server.listen(5)  # 半连接池：客户端连接请求个数的容器，当前已连接的客户端信息收发未完成前，会有最大5个客户端连接请求进入排队状态，
                  # 等待上一个通信完毕后，就可以连接进入开始通信。
# 双向通道建立成功，可以进行下一步数据的通信了
conn, client_addr = server.accept()
# 进行一次信息的收与发
data = conn.recv(1024)      # 每次最大接收1024字节，收到的数据为二进制Bytes类型
conn.send(data.upper())     # 将收到的数据进行处理，返回新的数据，反馈给客户端（给客户端发数据），发的数据类型也必须是Bytes类型
# 一轮信息收发完毕，关闭已经建立的双向通道
conn.close()