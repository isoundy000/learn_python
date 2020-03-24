#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# UDP协议介绍
# UDP叫数据报协议，意味着发消息都带有数据报头
# udp的server不需要就行监听也不需要建立连接
# 在启动服务之后只能被动的等待客户端发送消息过来，客户端发送消息的时候，要带上服务端的地址
# 服务端在回复消息的时候，也需要带上客户端的地址

# 1.udp协议客户端允许发空
# 2.udp协议不会粘包
# 3.udp协议服务端不存在的情况下，客户端照样不会报错
# 4.udp协议支持并发

# 简单的UDP协议数据传输

import socket

server = socket.socket(type=socket.SOCK_DGRAM)
server.bind(('127.0.0.1', 8888))

msg, addr = server.recvfrom(1024)
print(msg.decode('utf-8'))
server.sendto(b'hello', addr)
server.close()


# 验证udp协议有无粘包问题
# import socket
# server = socket.socket(type=socket.SOCK_DGRAM)
# server.bind(('127.0.0.1', 8888))
# print(server.recvfrom(1024))
# print(server.recvfrom(1024))
# print(server.recvfrom(1024))


# 小知识点补充:
# windows电脑和max电脑的时间同步功能，其实就是基于udp朝windows，max服务器发送请求获取标准时间

# UDP协议下通信利用socketserver模块实现多客户端并发通信
try:
    import socketserver                     # python3
except:
    import SocketServer as socketserver     # python2


class MyUdpHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data, sock = self.request
        sock.sendto(data.upper(), self.client_address)


if __name__ == '__main__':
    server = socketserver.ThreadingUDPServer(('127.0.0.1', 8889), MyUdpHandler)
    server.serve_forever()