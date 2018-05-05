# -*- encoding: utf-8 -*-
'''
Created on 2018年1月31日

@author: houguangdong
'''

import os
import socket
import fcntl
import tornado
import Queue
from tornado.netutil import bind_sockets
from SocketServer import TCPServer
from tornado import ioloop
from tornado.ioloop import IOLoop
import functools


# def set_close_exec(fd):
#     flags = fcntl.fcntl(fd, fcntl.F_GETFD)
#     fcntl.fcntl(fd, fcntl.F_SETFD, flags | fcntl.FD_CLOEXEC)
#     
# 
# a = '你好'
# sk = socket.socket()
# set_close_exec(sk.fileno())
# sk.bind(('127.0.0.1', 8888))
# sk.listen(1)
# 
# 
# def start_child():
#     id = os.fork()
#     if id == 0:
#         print('I am child process (%s) and my parent is %s.' % (os.getpid(), os.getppid()))
#         print(a)
#         print('----------', sk.fileno())
#         return
#     else:
#         print('I (%s) just created a child process (%s.)' % (os.getpid(), id))
# 
# 
# print('haha')
# start_child()
# print('done')

# 3 要开车了：
# tornado多进程模式启动：
# sockets = bind_sockets(7777)
# tornado.process.fork_processes(0)
# server = TCPServer()
# server.add_sockets(sockets)
# ioloop.IOLoop.current().start()

# tornado的多进程处理分为以下几个步骤：
# 　　　　1  首先创建套接字，然后绑定并监听
# 　　　　2  执行fork调用，创建子进程(默认创建cpu个数的进程)。
# 　　　　　　2.5 fork完成后，父进程与子进程就开始分工了，父进程负责管理子进程(包括当子进程异常退出时，重新fork一个子进程；关闭所有子进程)，子进程则开始3、4、5步的操作
# 　　　　3  启动tcpserver
# 　　　　4  为所有套接字注册对应的事件以及处理函数　　　
# 　　　　5  运行ioloop这个反应器
# 实际上也就是：
# 　　每一个进程共享套接字(这实际上是个文件描述符)，
# 　　每一个子进程都有一个反应器，
# 　　每一个子进程都在反应器上为相同的套接字注册了相同的事件以及相同的处理函数。
# 那么问题也就来了：
# 　　当某个套接字上要建立连接，实际上每个子进程都能捕获到该事件并执行对应的处理函数，但到底是哪个子进程要执行该操作呢？ 当一个进程处理完了该操作，其他子进程该如何做呢？
# 我们带着以上问题开始剖析：
# 1  首先创建套接字，然后绑定并监听： sockets = bind_sockets(8888)
# bind_sockets()方法位于tornado.netutil文件中，下面来详细剖析一下该方法：


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
#sock.setsockopt    (socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
sock.setblocking(0)
server_address = ("localhost", 12346)
sock.bind(server_address)
sock.listen(5)
fd_map = {}
message_queue_map = {}
fd = sock.fileno()
fd_map[fd] = sock
ioloop = IOLoop.instance()


def handle_client(cli_addr, fd, event):
    print event, IOLoop.WRITE
    s = fd_map[fd]
    if event & IOLoop.READ: # receive the data
        data = s.recv(1024)
        if data:
            print "receive %s from %s" % (data, cli_addr)
            ioloop.update_handler(fd, IOLoop.WRITE)
            message_queue_map[s].put(data)
        else:
            print "closing %s" % cli_addr
            ioloop.remove_handler(fd)
            s.close()
            del message_queue_map[s]
    if event & IOLoop.WRITE:
        try: 
            next_msg = message_queue_map[s].get_nowait()
        except Queue.Empty:
            print "%s Queue Empty" % cli_addr
            ioloop.update_handler(fd, IOLoop.READ) # CHANGE THE SITUATION
        else:
            print "sending %s to %s" % (next_msg, cli_addr)
            s.send(next_msg)
            ioloop.update_handler(fd, IOLoop.READ)
    if event & IOLoop.ERROR:
        print "%s EXCEPTION ON" % cli_addr
        ioloop.remove_handler(fd)
        s.close()
        del message_queue_map[s]


def handle_server(fd, event):
    s = fd_map[fd]
    if event & IOLoop.READ:
        get_connection, cli_addr = s.accept()
        print "connection %s" % cli_addr[0]
        get_connection.setblocking(0)
        get_connection_fd = get_connection.fileno()
        fd_map[get_connection_fd] = get_connection
        handle = functools.partial(handle_client, cli_addr[0])
        ioloop.add_handler(get_connection_fd, handle, IOLoop.READ)
        message_queue_map[get_connection] = Queue.Queue()


io_loop = IOLoop.instance()
io_loop.add_handler(fd, handle_server, io_loop.READ)
try:
    io_loop.start()
except KeyboardInterrupt:
    print "exit"
    io_loop.stop()
        
