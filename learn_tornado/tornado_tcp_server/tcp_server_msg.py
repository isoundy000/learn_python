#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# Python实现基于tornado的异步TCPServer和TCPClient即时通信小程序代码
from tornado import ioloop, gen, iostream
from tornado.tcpserver import TCPServer


class MyTcpServer(TCPServer):

    @gen.coroutine
    def handle_stream(self, stream, address):
        try:
            # 每收到一段20字符以内的内容，将之反序回传，如果收到 'over'，就断开连接。
            # 注意，断开连接不用yield 调用；无论是谁断开连接，连接双方都会各自触发一个StreamClosedError。
            while True:
                msg = yield stream.read_bytes(20, partial=True)
                print msg, 'from', address
                stream.write(str(msg))
                yield stream.write(msg[::-1])
                if msg == 'over':
                    stream.close()
        except iostream.StreamClosedError:
            pass


if __name__ == '__main__':
    server = MyTcpServer()
    server.listen(8036)
    server.start()
    ioloop.IOLoop.current().start()