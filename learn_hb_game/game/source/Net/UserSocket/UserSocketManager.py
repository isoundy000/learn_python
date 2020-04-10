#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from Source.Log.Write import Log
from Source.DataLock.Lock1 import Lock1
from Source.DataLock.Lock2 import Lock2
from gevent import monkey; monkey.patch_socket()
from gevent.queue import Queue
from Source.UserData.UserDataManager import UserDataManager
from datetime import datetime
from Source.DataBase.Table.Log.t_log_connections import t_log_connections
from Source.DataBase.Table.Log.t_log_onoffline import t_log_onoffline
from Source.TaskQueue.InnerTask import InnerTask


class UserSocketManager:
    """用户socket管理器"""
    _dict = None
    _id = None
    _device = None
    _seq = None
    _lock = None
    _magicCode = 0

    @staticmethod
    def Init(magiccode):
        UserSocketManager._dict = {}    # {sockfileno: {"send": Queue(), "id": None, "close": closeEvent}}
        UserSocketManager._id = {}
        UserSocketManager._device = {}
        UserSocketManager._seq = {}     # {sockfileno: 0}
        UserSocketManager._lock = Lock1()
        UserSocketManager._magicCode = magiccode
        return True

    @staticmethod
    def NewConnection(sockfileno, closeEvent):
        '''
        创建一个连接
        :param sockfileno:
        :param closeEvent:
        :return:
        '''
        Lock2(UserSocketManager._lock)
        UserSocketManager._dict[sockfileno] = {
            "send": Queue(),
            "id": None,             # rid
            "close": closeEvent
        }
        UserSocketManager._seq[sockfileno] = 0

    @staticmethod
    def CloseConnection(sockfileno):
        '''
        关闭用户的连接
        :param sockfileno:
        :return:
        '''
        Log.Write("CloseConnection", sockfileno)
        Lock2(UserSocketManager._lock)
        if UserSocketManager._dict.has_key(sockfileno):
            UserSocketManager._dict[sockfileno]["close"].set()

    @staticmethod
    def SendToConnection(sockfileno, data):
        '''
        按照sockfileno给用户发送数据
        :param sockfileno:
        :param data:
        :return:
        '''
        Lock2(UserSocketManager._lock)
        if not UserSocketManager._dict.has_key(sockfileno):
            return False
        # UserSocketManager._seq[sockfileno] += 1
        # data.setSeq(UserSocketManager._seq[sockfileno])
        # data.setMagicCode(UserSocketManager._magicCode)
        UserSocketManager._dict[sockfileno]["send"].put(data)  # "send": Queue()
        return True

    @staticmethod
    def SendToUser(rid, data, forcesend=False):
        '''
        给玩家发送数据
        :param rid:
        :param data:
        :param forcesend:
        :return:
        '''
        # Log.Write("SendToUser", rid)
        Lock2(UserSocketManager._lock)
        if not UserSocketManager._id.has_key(rid):
            Log.Write("[Error]no user %d" % rid)
            return False
        sockfileno = UserSocketManager._id[rid]
        # todo fix chungeng cut off net resend data
        if not forcesend:
            sockfileno2 = None
            sock2 = data.Socket()
            if sock2:
                sockfileno2 = sock2.fileno()
            # Log.Write("SendToUser", sockfileno2, sockfileno)
            if sockfileno2 and sockfileno != sockfileno2:
                return False
        if not UserSocketManager._dict.has_key(sockfileno):
            Log.Write("[Error]no user %d sock" % rid)
            return False
        # UserSocketManager._seq[sockfileno] += 1
        # data.setSeq(UserSocketManager._seq[sockfileno])
        data.setMagicCode(UserSocketManager._magicCode)
        UserSocketManager._dict[sockfileno]["send"].put(data)       # "send": Queue()
        return True

    @staticmethod
    def SendToAllOnline(data):
        '''
        给所有在线的玩家发送数据
        :param data:
        :return:
        '''
        Lock2(UserSocketManager._lock)
        for k, v in UserSocketManager._dict.items():
            # UserSocketManager._seq[k] += 1
            # data.setSeq(UserSocketManager._seq[k])
            data.setMagicCode(UserSocketManager._magicCode)
            v["send"].put(data.Clone())
        return True

    @staticmethod
    def ConnectionGet(sockfileno):
        '''
        根据sockfileno获取发送给玩家的数据
        :param sockfileno:
        :return:
        '''
        Lock2(UserSocketManager._lock)
        if not UserSocketManager._dict.has_key(sockfileno):
            return None
        return UserSocketManager._dict[sockfileno]["send"].get()

    @staticmethod
    def UserOnline(rid, sockfileno):
        '''
        设置玩家在线信息 玩家新的sockfileno和rid
        :param rid:
        :param sockfileno:
        :return:
        '''
        Lock2(UserSocketManager._lock)
        Log.Write("useronline", ("roleid", rid, "socket", sockfileno))
        if UserSocketManager._id.has_key(rid):
            oldsocket = UserSocketManager._id[rid]
            if sockfileno != oldsocket and UserSocketManager._dict.has_key(oldsocket):
                UserSocketManager._dict[oldsocket]["close"].set()
        UserSocketManager._id[rid] = sockfileno
        UserSocketManager._dict[sockfileno]["id"] = rid
        # t_log_onoffline.On(rid, sockfileno)

    @staticmethod
    def UserOffline(rid):
        '''
        玩家离线 删除sockfileno和连接
        :param rid:
        :return:
        '''
        Lock2(UserSocketManager._lock)
        if UserSocketManager._id.has_key(rid):
            sockfileno = UserSocketManager._id[rid]
            if UserSocketManager._dict.has_key(sockfileno):
                UserSocketManager._dict[sockfileno]["close"].set()
            del UserSocketManager._id[rid]

    @staticmethod
    def SendToOnlines(data):
        '''
        给在线的所有玩家发送数据
        :param data:
        :return:
        '''
        Lock2(UserSocketManager._lock)
        for sockfileno, userSocketData in UserSocketManager._dict.items():
            userSocketData["send"].put(data.Clone())

    @staticmethod
    def Status():
        '''
        统计在线的sock和玩家
        :return:
        '''
        Lock2(UserSocketManager._lock)
        c = len(UserSocketManager._dict)
        u = len(UserSocketManager._id)
        Log.Write("-status-usockcount-", c, u)
        t_log_connections.Now(c, u)

    @staticmethod
    def FindSockByRoleId(roleid):
        '''
        通过rid找sockfileno
        :param roleid:
        :return:
        '''
        Lock2(UserSocketManager._lock)
        if UserSocketManager._id.has_key(roleid):
            return UserSocketManager._id[roleid]
        return None

    @staticmethod
    def FindRoleIdBySock(sockfileno):
        '''
        通过sock找玩家rid
        :param sockfileno:
        :return:
        '''
        Lock2(UserSocketManager._lock)
        if UserSocketManager._dict.has_key(sockfileno):
            return UserSocketManager._dict[sockfileno]["id"]
        return None

    @staticmethod
    def DeviceOnline(uuid, socket):
        Lock2(UserSocketManager._lock)
        UserSocketManager._device[socket] = uuid

    @staticmethod
    def FindDeviceBySocket(socket):
        Lock2(UserSocketManager._lock)
        if not UserSocketManager._device.has_key(socket):
            return None
        return UserSocketManager._device[socket]

    @staticmethod
    def DelConnection(sockfileno):
        '''
        通过sockfileno删除玩家
        :param sockfileno:
        :return:
        '''
        Lock2(UserSocketManager._lock)
        # if UserDataManager._sock.has_key(sockfileno): # for acc
        #     del UserDataManager._sock[sockfileno]     # for acc
        if UserSocketManager._dict.has_key(sockfileno):
            rid = UserSocketManager._dict[sockfileno]["id"]
            InnerTask(50006, {"id": rid})               # for game
            t_log_onoffline.Off(UserSocketManager._dict[sockfileno]["id"], sockfileno)  # for game
            del UserSocketManager._dict[sockfileno]
            if UserSocketManager._id.has_key(rid) and UserSocketManager._id[rid] == sockfileno:
                del UserSocketManager._id[rid]
        del UserSocketManager._seq[sockfileno]

    @staticmethod
    def UserInGame(rid):
        '''
        玩家在线
        :param rid:
        :return:
        '''
        return rid in UserSocketManager._id


UserDataManager.UserSocketManager = UserSocketManager