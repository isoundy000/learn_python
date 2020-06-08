#!/usr/bin/env python
# -*- coding:utf-8 -*-

from Source.Log.Write import Log
import gevent
import gevent.socket
from gevent.event import Event
from gevent import monkey; monkey.patch_socket()
import socket as l_socket
from Source.Config.ConfigManager import ConfigManager
from Source.Net.ServerSocket.ServerSocketManager import ServerSocketManager
from Source.Net.ServerSocket.ServerSocketRead import ServerSocketRead
from Source.Net.ServerSocket.ServerSocketWrite import ServerSocketWrite
from Source.TaskQueue.TaskData import TaskData
from Source.Protocol import shaketoacc_pb2


class AccServerConnection:

    _status = False
    _reconnectEvent = None
    _sock = None

    def _init():
        AccServerConnection._reconnectEvent = Event()
        return True

    Init = staticmethod(_init)

    def _excute():
        appConfig = ConfigManager.Singleton()
        serverInfo = appConfig["Server"]["Info"]
        accServerConfig = appConfig["Server"]["Interface"]["AccServer"]
        address = (accServerConfig["Address"]["ip"], int(accServerConfig["Address"]["port"]))
        magiccode = int(accServerConfig["MagicCode"], 16)
        seqCount = 0
        while True:
            sock = None
            while True:
                AccServerConnection._status = False
                try:
                    Log.Write("try Acc Server connection to %s: %s" % address)
                    sock = gevent.socket.create_connection(address)
                except l_socket.error, e:
                    Log.Write("%s" % str(e))
                    gevent.sleep(2)
                    continue

                AccServerConnection._sock = sock
                AccServerConnection._reconnectEvent.clear()
                Log.Write("Acc Server connection to %s: %s" % address)
                ServerSocketManager.NewConnection(sock.fileno())

                taskData = TaskData(sock)
                taskData.setType(0)         # 给Acc发送消息

                shake_acc = shaketoacc_pb2.ShakeToAcc()     # 反向传递给Acc
                shake_acc.id = int(serverInfo["ID"])
                shake_acc.code = int(serverInfo["Code"], 16)
                shake_acc.port = 0

                taskData.setData(shake_acc.SerializePartialToString())
                shake_acc.Clear()

                ServerSocketManager.SendToConnection(sock.fileno(), taskData)   # 往Acc发送数据

                try:
                    sockread = gevent.spawn(ServerSocketRead, sock, AccServerConnection._reconnectEvent)
                    sockwrite = gevent.spawn(ServerSocketWrite, sock, AccServerConnection._reconnectEvent)

                    AccServerConnection._reconnectEvent.wait()      # 等待事件

                    if not sockread.ready() or not sockread.successful():   # 不在等待或者未成功
                        sockread.kill()                                     # 删掉此socket链接
                    if not sockwrite.ready() or not sockwrite.successful():
                        sockwrite.kill()

                finally:
                    AccServerConnection._sock = None                        # 断开链接
                    ServerSocketManager.DelConnection(sock.fileno())        # 删除链接
                    sock.close()
                    Log.Write("del Server connection to %s: %s" % address)
                    gevent.sleep(1)

    Excute = staticmethod(_excute)

    @staticmethod
    def Status():
        return AccServerConnection._status      # 链接的状态

    @staticmethod
    def setStatus(status):
        AccServerConnection._status = status

    @staticmethod
    def Reconnect():
        '''
        重新连接 任务队列置空
        :return:
        '''
        AccServerConnection._reconnectEvent.set()

    def _start():
        '''
        开始执行Acc任务队列
        :return:
        '''
        gevent.spawn(AccServerConnection.Excute)

    Start = staticmethod(_start)

    @staticmethod
    def SendTask(task):
        '''
        给Acc服务器发送任务
        :param task:
        :return:
        '''
        return ServerSocketManager.SendToConnection(AccServerConnection._sock.fileno(), task)