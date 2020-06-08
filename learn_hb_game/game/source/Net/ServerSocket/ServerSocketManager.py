#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


from Source.Log.Write import Log
from Source.DataLock.Lock1 import Lock1
from Source.DataLock.Lock2 import Lock2
from gevent import monkey; monkey.patch_socket()
from gevent.queue import Queue


class ServerSocketManager:

    _dict = None
    _id = None
    _seq = None
    _lock = None
    _magicCode = 0

    def _init(magicCode):
        ServerSocketManager._dict = {}
        ServerSocketManager._id = {}
        ServerSocketManager._seq = {}
        ServerSocketManager._lock = Lock1()
        ServerSocketManager._magicCode = magicCode

    Init = staticmethod(_init)

    def _newconnection(sockfileno):
        '''
        创建一个连接
        :return:
        '''
        Lock2(ServerSocketManager._lock)
        ServerSocketManager._dict[sockfileno] = {
            "send": Queue()
        }
        ServerSocketManager._seq[sockfileno] = 0

    NewConnection = staticmethod(_newconnection)

    def _delconnection(sockfileno):
        '''
        删除连接
        :return:
        '''
        Lock2(ServerSocketManager._lock)
        del ServerSocketManager._dict[sockfileno]

    DelConnection = staticmethod(_delconnection)

    def _send(sockfileno, data):
        '''
        给请求的sock发送数据
        :param data:
        :return:
        '''
        Lock2(ServerSocketManager._lock)
        if not ServerSocketManager._dict.has_key(sockfileno):
            return False
        ServerSocketManager._seq[sockfileno] += 1
        data.setSeq(ServerSocketManager._seq[sockfileno])
        data.setMagicCode(ServerSocketManager._magicCode)
        ServerSocketManager._dict[sockfileno]["send"].put(data)
        return True

    SendToConnection = staticmethod(_send)

    def _send2(serverid, data):
        '''
        给区服发送数据
        :param data:
        :return:
        '''
        Lock2(ServerSocketManager._lock)
        if not ServerSocketManager._id.has_key(serverid):
            Log.Write("[Error]Send To GameServer: %d offline" % serverid)
            return False
        sockfileno = ServerSocketManager._id[serverid]
        if not ServerSocketManager._dict.has_key(sockfileno):
            return False
        ServerSocketManager._seq[sockfileno] += 1
        data.setSeq(ServerSocketManager._seq[sockfileno])
        data.setMagicCode(ServerSocketManager._magicCode)
        ServerSocketManager._dict[sockfileno]["send"].put(data)
        return True

    SendToServer = staticmethod(_send2)

    def _get(sockfileno):
        '''
        获取一个sock连接队列中的数据
        :return:
        '''
        Lock2(ServerSocketManager._lock)
        if not ServerSocketManager._dict.has_key(sockfileno):
            Log.Write("Error", "ServerSocketManager sockfileno cant find", sockfileno)
            return
        return ServerSocketManager._dict[sockfileno]["send"].get()

    ConnectionGet = staticmethod(_get)

    @staticmethod
    def GameServerOnline(serverid, socket):
        '''
        设置区服在线的sock连接
        :param serverid:
        :param socket:
        :return:
        '''
        Lock2(ServerSocketManager._lock)
        Log.Write("[TIP]GameServer: %d online" % serverid)
        ServerSocketManager._id[serverid] = socket