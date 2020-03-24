#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from tornado import ioloop, gen, iostream
from tornado.tcpclient import TCPClient


@gen.coroutine
def Trans():
    stream = yield TCPClient.connect('localhost', 8036)
    try:
        while True:
            DATA = raw_input("Enter your input: ")
            yield stream.write(str(DATA))
            back = yield stream.read_bytes(20, partial=True)
            msg = yield stream.read_bytes(20, partial=True)
            print msg
            print back
            if DATA == 'over':
                break
    except iostream.StreamClosedError:
        pass


if __name__ == '__main__':
    ioloop.IOLoop.current().run_sync(Trans)


# 使用 TCPClient 比 TCPServer 更简单，无须继承，只要用 connect 方法连接到 server，就会返回 iostream 对象了。
# 在本例中，我们向 server 发送一些字符串，它都会反序发回来。最后发个 'over'，让 server 断开连接。
# 当然也可以由 client 断开；值得注意，这段代码与之前的几个例子有个根本的区别，之前都是服务器，被动等待行为发生，而这段代码是一运行就主动发起行为（连接），因此它的运行方式不同于以往，需要我们主动通过 ioloop 的 run_sync 来调用。
# 以往那些实例中的异步处理方法实际是由 Tornado 调用的。在 run_sync 里，tornado 会先启动消息循环，执行目标函数，之后再结束消息循环。