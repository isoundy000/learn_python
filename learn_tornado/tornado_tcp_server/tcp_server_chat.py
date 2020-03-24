#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# tornado学习 - TCPServer 实现聊天功能
# 对于TCP服务器，基本的操作tornado.tcpserver.TCPServer已经封装好，只需要重写handle_stream()方法即可。
# 目前只写了一个简单的聊天服务器。其中需要的功能基本功能就是客户端连接服务器之后发出消息，服务器将该消息推送到目前在服务器上连接的每一个客户端。
import tornado
import tornado.ioloop
import tornado.tcpserver
from tornado.iostream import StreamClosedError


class Connection:

    clients = set()
    def __init__(self, stream, address):
        self._stream = stream
        self._address = address

        self.EOF = b'\n'

        self._stream.set_close_callback(self.on_close)
        self.read_message()
        print('{} has entered the room.'.format(address))

    # 声明一个空集合clients用来存储所有连接到服务器的客户端对象。_stream可以抽象成一座架在客户端与服务器间的桥梁，在其上进行数据传输等操作。
    # _address则是客户端地址和端口，是一个元组对象。EOF用来作为客户端发送消息完毕的标识。ser_close_callback()
    # 注册一个回调函数，在stream关闭时会被激活。read_message()
    # 时该连接类的核心方法，负责读取客户端发送信息。

    def read_message(self):
        self._stream.read_until(self.EOF, self.boardcast_message)

    # 负责从缓冲区读取数据，当遇到EOF时，读取完成并且激活回调函数。

    def boardcast_message(self, data):
        try:
            data = tornado.escape.to_unicode(data)
            for conn in Connection.clients:
                conn.send_message(data)
            self.read_message()
        except StreamClosedError as e:
            pass

    # 将客户端发送消息广播到每个连接在服务器的客户端。其中遍历Connection.clients保持监听每一个客户端发送信息。处理异常pass断开stream时的报错。

    def send_message(self, data):
        data = str(self._address + ' said: ' + data)
        self._stream.write(bytes(data.encode('utf-8')))

    # 客户端发送消息，将数据转换为bytes类型，通过stream.write()写入缓冲区。

    def on_close(self):
        Connection.clients.remove(self)

    # 当客户端断开连接时，将其从保存的客户端集合中删除。


# 到这里，服务器端的连接类基本成型。接下来就是TCP服务器, 只要继承tornado.tcpserver.TCPServer类，然后重写handle_stream()方法就行。
class SimpleTCPServer(tornado.tcpserver.TCPServer):

    def handle_stream(self, stream, address):
        Connection(stream, address)


# 接下来就是让服务器运行.
if __name__ == '__main__':
    server = SimpleTCPServer()
    server.listen(8888, '0.0.0.0')
    tornado.ioloop.IOLoop.instance().start()

# 创建一个服务器实例，然后监听8888端口，所有ip。之后运行一个ioloop实例并且start()即可。
#
# 测试效果结果的话，因为我是使用Linux mint，nc命令可以访问给定的地址和端口，所以只需要：
# nc localhost 8888就能访问到服务器。