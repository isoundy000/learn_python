# -*- encoding: utf-8 -*-
'''
Created on 2018年5月26日

@author: houguangdong
'''
# 对每一个人微笑，不试图劝服他人，不因对人失望而愤怒，务实，低调，做自己
# gevent 创建tcp 服务器
# 最近学习写游戏服务器了，看了下，决定用gevent来写，比较简单，效率也还不错。
from gevent.server import StreamServer
# from tool import addressbook_pb2
BUFSIZE = 1024


def handle(socket, address):
    print socket.fileno()
    data = socket.recv(BUFSIZE)
    print "\n"
    print data
    socket.send("Hello client!\n")


# server = StreamServer(('127.0.0.1', 5000), handle)
# server.serve_forever()
# 简单的一个tcp服务端，显示收到的数据，并回传一个数据。


# gevent开发http服务器与tcp服务器
# 感觉上gevent相关的东西也都了解的差不多了。。。最后收一下尾，看看怎么来利用gevent来实际的开发吧。。。
# 先来说http服务器相关的。。。因为gevent中带有WSGI的server实现。。。所以，可以很方便的利用gevent来开发http服务器。。。
# 例如如下代码，采用gevent加tornado的方式。。。。（tornado其实自带的有I/O循环，但是用gevent可以提高其性能。。）代码如下：
from gevent import monkey
monkey.patch_all()
from gevent.wsgi import WSGIServer
import gevent
import tornado
import tornado.web
import tornado.wsgi


class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        self.write('hello world 111')


def app(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    return ["<b>hello world 222</b>"]


# 至于说如何来开发基于TCP的server，因为gevent自带了streamserver，其实gevent的WSGI的server也是基于streamserver来开发的。。。非常的简单，只需要提供一个handle就好了。。。每当listener收到了一个socket，它都将会创建一个协程，然后调用handle来处理。。所以只需要同步的方式来写代码就好了。。。代码如下：
def handle1(sock, address):
    sock.recv(1000)
    sock.send("HTTP/1.1 200 OK\r\n\r\nfafdsa")


def connection_handler(socket, address):
    for l in socket.makefile('r'):      # 以读的方式读取收到的文件
        socket.sendall(l)


if __name__ == "__main__":
    application = tornado.wsgi.WSGIApplication(handlers=[("/get", IndexHandler)])
    # server = gevent.wsgi.WSGIServer(('127.0.0.1', 8000), app)
    # server = gevent.wsgi.WSGIServer(('127.0.0.1', 8000), application)
    # server = StreamServer(('', 8000), handle1)  # 实现起来确实很简单，感觉跟代码比nodejs都还要精炼一些。。
    server = StreamServer(('0.0.0.0', 8000), connection_handler)
    server.serve_forever()