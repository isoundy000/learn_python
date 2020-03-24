#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

try:
    import socketserver                     # python3
except:
    import SocketServer as socketserver     # python2
import time


class MyTcpHandler(socketserver.BaseRequestHandler):

    # 到这里表示服务端已监听到一个客户端的连接请求,将通信交给一个handle方法实现，自己再去监听客户连接请求
    def handle(self):
        # 建立双向通道，进行通信
        print('%s|客户端%s已连接' % (time.strftime('%Y-%m-%d %H:%M:%S'), self.client_address))
        while True:
            try:
                data = self.request.recv(1024)
                msg = '我已收到您的请求[%s]，感谢您的关注！' % data.decode('utf-8')
                self.request.send(msg.encode('utf-8'))
            except ConnectionResetError:
                print('%s|客户端%s已断开连接' % (time.strftime('%Y-%m-%d %H:%M:%S'), self.client_address))
                break


if __name__ == '__main__':
    server = socketserver.ThreadingTCPServer(('127.0.0.1', 8888), MyTcpHandler)     # 绑定服务端IP和PORT，并产生并发方法对象
    print('等待连接请求中...')
    server.serve_forever()     # 服务端一直开启