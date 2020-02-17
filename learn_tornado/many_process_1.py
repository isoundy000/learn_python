#!/usr/bin/env python
# -*- coding:utf-8 -*-
import multiprocessing
print multiprocessing.cpu_count()

import os
import socket
import fcntl
import tornado


def set_close_exec(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFD)
    fcntl.fcntl(fd, fcntl.F_SETFD, flags | fcntl.FD_CLOEXEC)


a = '你好'
sk = socket.socket()
set_close_exec(sk.fileno())
sk.bind(('127.0.0.1', 8888))
sk.listen(1)


def start_child():
    id = os.fork()
    if id == 0:             # 子进程返回0
        print('I am child process (%s) and my parent is %s.' % (os.getpid(), os.getppid()))
        print(a)
        print('---------------', sk.fileno())
    else:
        print('I (%s) just created a child process (%s).' % (os.getpid(), id))      # id 父进程返回子进程的pid
        print('+++++++++++++++', sk.fileno())


print('haha')
start_child()
print('done')

# 3 要开车了：
# sockets = tornado.netutil.bind_sockets(8888)
# tornado.process.for_processes(0)
# server = TCPServer()
# server.add_sockets(sockets)
# tornado.ioloop.IOLoop.current().start()

print os.name != 'nt'  # 非windows