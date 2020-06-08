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


class AccServerConnection2:

    _status = False
    _reconnectEvent = None
    _sock = None

    def _init():
        AccServerConnection2._reconnectEvent = Event()
        return True

    Init = staticmethod(_init)

    def _excute():
        appConfig = ConfigManager.Singleton()
        serverInfo = appConfig["Server"]["Info"]
        accServerConfig = appConfig["Server"]["Interface"]["AccServer2"]
        address = (accServerConfig["Address"]["ip"], int(accServerConfig["Address"]["port"]))
        magiccode = int(accServerConfig["MagicCode"], 16)
        seqCount = 0
        while True:
            sock = None
            while True:
                AccServerConnection2._status = False
                try:
                    Log.Write("try Acc Server 2 connection to %s:%s"%address)
                    sock = gevent.socket.create_connection(address)
                except l_socket.error, e:
                    Log.Write("%s" % str(e))
                    gevent.sleep(2)
                    continue

                AccServerConnection2._sock = sock
                AccServerConnection2._reconnectEvent.clear()
                Log.Write("Acc Server 2 connection to %s:%s" % address)
                ServerSocketManager.NewConnection(sock.fileno())

                taskData = TaskData(sock)
                taskData.setType(0)

                shake_acc = shaketoacc_pb2.ShakeToAcc()
                shake_acc.id = int(serverInfo["ID"])
                shake_acc.code = int(serverInfo["Code"], 16)
                shake_acc.port = 0

                taskData.setData(shake_acc.SerializePartialToString())
                shake_acc.Clear()

                ServerSocketManager.SendToConnection(sock.fileno(), taskData)

                try:
                    sockread = gevent.spawn(ServerSocketRead, sock, AccServerConnection2._reconnectEvent)
                    sockwrite = gevent.spawn(ServerSocketWrite, sock, AccServerConnection2._reconnectEvent)

                    # AccServerConnection2._reconnectEvent.wait(300)
                    AccServerConnection2._reconnectEvent.wait()

                    if not sockread.ready() or not sockread.successful():
                        sockread.kill()
                    if not sockwrite.ready() or not sockwrite.successful():
                        sockwrite.kill()

                finally:
                    AccServerConnection2._sock = None
                    ServerSocketManager.DelConnection(sock.fileno())
                    sock.close()
                    Log.Write("del Server connection to %s:%s" % address)

    Excute = staticmethod(_excute)

    @staticmethod
    def Status():
        return AccServerConnection2._status

    @staticmethod
    def setStatus(status):
        AccServerConnection2._status = status

    @staticmethod
    def Reconnect():
        AccServerConnection2._reconnectEvent.set()

    def _start():
        gevent.spawn(AccServerConnection2.Excute)

    Start = staticmethod(_start)

    @staticmethod
    def SendTask(task):
        return ServerSocketManager.SendToConnection(AccServerConnection2._sock.fileno(), task)