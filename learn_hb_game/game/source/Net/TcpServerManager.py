#!/usr/bin/env python
# -*- coding:utf-8 -*-

from Source.Log.Write import Log
from gevent import monkey; monkey.patch_all()
from gevent.server import StreamServer
from gevent.pywsgi import WSGIServer


class TcpServerManager:

    _servers = None

    def _init():
        TcpServerManager._servers = {}
        return True

    Init = staticmethod(_init)

    def _create(tag, address, func, max):
        '''
        创建一个tcp连接
        :param address: 连接地址
        :param func: 函数
        :param max: 最大值
        :return:
        '''
        instance = StreamServer(address, func)
        instance.max_accept = max               # 最大的连接数
        instance.max_delay = 0.1
        instance.start()

        TcpServerManager._servers[tag] = {
            "address": address,
            "max": max,
            "instance": instance,
            "status": True                      # 状态
        }
        return True

    Create = staticmethod(_create)

    def _wait():
        '''
        挂起|等待一下
        :return:
        '''
        while True:
            bHaveRun = False
            for tag in TcpServerManager._servers.keys():
                serverInfo = TcpServerManager._servers[tag]
                if serverInfo["status"]:
                    # Log.Write("check %s" % (tag))
                    # if serverInfo["instance"]._stopped_event.wait(1):
                    if serverInfo["instance"]._stop_event.wait(1):
                        serverInfo["status"] = False
                    else:
                        bHaveRun |= True

            if not bHaveRun:
                return True

    Wait = staticmethod(_wait)

    def _kill():
        '''
        断开一个tcp连接
        :return:
        '''
        for tag in TcpServerManager._servers:
            serverInfo = TcpServerManager._servers[tag]
            if serverInfo["status"]:
                # serverInfo["instance"].kill()
                serverInfo["instance"].close()              # 关闭连接
                serverInfo["status"] = False                # 改变状态

    Kill = staticmethod(_kill)

    @staticmethod
    def CreateWSGI(tag, address, func):
        '''
        创建WSGI
        :param tag: manager
        :param address: 地址
        :param func: 函数
        :return:
        '''
        instance = WSGIServer(address, func)
        instance.start()
        TcpServerManager._servers[tag] = {
            "address": address,
            "instance": instance,
            "status": True
        }
        return True