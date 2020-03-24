#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import socket
import threading
import tornado.iostream
import tornado.ioloop
from tornado.escape import to_unicode
# tornado学习 - TCPClient 实现聊天功能
# 之前完成了一个简单的聊天服务器，连接服务器使用的是系统自带nc命令，接下来就是通过自己实现TCPClient.
# 客户端与服务器功能大致相仿，相对与服务器只是少了转发消息环节。
# 首先，定义TCPClient类，主要初始化host、port、stream属性。


class SimpleTCPClient:

    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._stream = None
        self.EOF = b' end'

    # 刚创建client实例时还未与服务器连接，所以_stream初始值为None。EOF设置为消息的结尾，当读到这个标识时表示一条消息输出完毕。

    def get_stream(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self._stream = tornado.iostream.IOStream(sock)
        self._stream.set_close_callback(self.on_close)

    # 获取socket, 通过tornado.iostream.IOStream创建_stream。
    # socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    # 中，其中第一个参数是namespace即使用的地址，这里的AF_INET表示使用IPv4地址，
    # 第二个参数是style，即socket的连接类型，这里使用的SOCK_STREAM是流式类型基于TCP。
    # 第三个参数是protocol指使用的协议类型，一般情况下使用0表示系统根据情况决定。

    def connect(self):
        self.get_stream()
        self._stream.connect((self._host, self._port), self.start)

    # 定义连接服务器的方法，先获取_stream然后连接服务器地址和指定端口，最后注册回调函数就是开始客户端运行的函数。

    def start(self):
        t1 = threading.Thread(target=self.read_msg)
        t2 = threading.Thread(target=self.send_msg)
        t1.daemon, t2.daemon = True, True
        t1.start()
        t2.start()

    # 使用多线程同时通知收发消息。这里存在一个问题，使用多线程时，如果退出程序就必须要结束线程，否则会抛出异常，
    # 但是程序何时结束取决于用户。为了解决这个问题，将线程设置为daemon线程，daemon线程可以在主程序结束时自动结束。

    def read_msg(self):
        self._stream.read_until(self.EOF, self.show_msg)

    def show_msg(self, data):
        print(to_unicode(data))
        self.read_msg()

    # 接受并显示消息。当数据中读取到结束标识，调用打印消息的方法，消息打印完毕后再调用读取方法，以此保持接收消息的状态。

    def send_msg(self):
        while True:
            data = input()
            self._stream.write(bytes(data) + self.EOF)

    # 发送消息。使用while循环保持输入状态，当输入完成讲消息转换为byte型，与消息结束标识拼接之后发送。

    def on_close(self):
        print('exit ...')
        quit()

    # 用户退出时关闭_stream会激活这个函数。


if __name__ == '__main__':
    try:
        client = SimpleTCPClient('localhost', 8888)
        client.connect()
        tornado.ioloop.IOLoop.instance().start()
    except:
        pass

