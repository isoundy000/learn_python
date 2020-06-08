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


class WorldWarServerConnection:

    _status = False
    _reconnectEvent = None
    _sock = None

    def _init():
        WorldWarServerConnection._reconnectEvent = Event()
        return True

    Init = staticmethod(_init)

    def _excute():
        appConfig = ConfigManager.Singleton()
        serverInfo = appConfig["Server"]["Info"]
        if "WorldWarServer" not in appConfig["Server"]["Interface"]:
            return
        accServerConfig = appConfig["Server"]["Interface"]["WorldWarServer"]
        address = (accServerConfig["Address"]["ip"], int(accServerConfig["Address"]["port"]))
        magiccode = int(accServerConfig["MagicCode"], 16)
        seqCount = 0
        while True:
            sock = None
            while True:
                WorldWarServerConnection._status = False
                try:
                    Log.Write("try WorldWar Server connection to %s: %d" % address)
                    sock = gevent.socket.create_connection(address)
                except l_socket.error, e:
                    Log.Write("%s" % str(e))
                    gevent.sleep(2)
                    continue

                WorldWarServerConnection._sock = sock
                WorldWarServerConnection._reconnectEvent.clear()
                Log.Write("WorldWar Server connection to %s: %s" % address)
                ServerSocketManager.NewConnection(sock.fileno())

                taskData = TaskData(sock)
                taskData.setType(90000)
                shake_acc = shaketoacc_pb2.ShakeToAcc()
                shake_acc.id = int(serverInfo["ID"])
                shake_acc.code = int(serverInfo["Code"], 16)
                shake_acc.port = 0
                taskData.setData(shake_acc.SerializePartialToString())
                shake_acc.Clear()
                ServerSocketManager.SendToConnection(sock.fileno(), taskData)

                taskData = TaskData(sock)
                taskData.setType(90012)
                ServerSocketManager.SendToConnection(sock.fileno(), taskData)

                try:
                    sockread = gevent.spawn(ServerSocketRead, sock, WorldWarServerConnection._reconnectEvent)
                    sockwrite = gevent.spawn(ServerSocketWrite, sock, WorldWarServerConnection._reconnectEvent)

                    WorldWarServerConnection._reconnectEvent.wait()

                    if not sockread.ready() or not sockread.successful():
                        sockread.kill()
                    if not sockwrite.ready() or not sockwrite.successful():
                        sockwrite.kill()

                except:
                    Log.Write(traceback.format_exc())

                finally:
                    WorldWarServerConnection._sock = None
                    ServerSocketManager.DelConnection(sock.fileno())
                    sock.close()
                    Log.Write("del WorldWar Server connection to %s: %s" % address)
                    gevent.sleep(1)

    Excute = staticmethod(_excute)

    @staticmethod
    def Status():
        return WorldWarServerConnection._status

    @staticmethod
    def setStatus(status):
        WorldWarServerConnection._status = status

    @staticmethod
    def Reconnect():
        WorldWarServerConnection._reconnectEvent.set()

    def _start():
        gevent.spawn(WorldWarServerConnection.Excute)

    Start = staticmethod(_start)

    @staticmethod
    def SendTask(task):
        return ServerSocketManager.SendToConnection(WorldWarServerConnection._sock.fileno(), task)