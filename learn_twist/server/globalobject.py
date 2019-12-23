#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/11/20 12:07
# @version: 0.0.1
# @Author: houguangdong
# @File: globalobject.py
# @Software: PyCharm

from klein import Klein
from learn_twist.utils.singleton import Singleton
from learn_twist.netconnect.protoc import LiberateFactory
from learn_twist.distributed.root import PBRoot
from learn_twist.distributed.node import RemoteObject

# typing
from typing import Union
from typing import Dict
from typing import List


class GlobalObject(metaclass=Singleton):
    """
    单例,进程公共数据
    """

    def __init__(self):
        self.net_factory = None  # type: Union[LiberateFactory, None]
        self.root = None  # type: Union[PBRoot, None]
        self.remote = {}  # type: Dict[str, RemoteObject]
        self.db = None
        self.stop_handler = None
        self.web_root = None  # type:  Union[Klein, None]
        self.master_remote = None  # type: Union[RemoteObject, None]
        self.reload_module = None
        self.remote_connect = None
        self.json_config = {}
        self.remote_map = {}    # type: Dict[str, Dict[str, Union[str, List]]]

    def config(self, net_factory, root, remote):
        self.net_factory = net_factory
        self.root = root
        self.remote = remote


GO = GlobalObject()


def master_service_handle(target):
    """
    """
    GO.master_remote.reference.service.map_target(target)


def net_service_handle(target):
    """
    """
    GO.net_factory.service.map_target(target)


def root_service_handle(target):
    """
    """
    GO.root.service.map_target(target)


class WebServiceHandle(object):
    """这是一个修饰符对象
    """
    def __init__(self, url=None):
        """
        @param url: str http 访问的路径
        """
        self._url = url

    def __call__(self, cls):
        """
        """
        from twisted.web.resource import Resource
        if self._url:
            child_name = self._url
        else:
            child_name = cls.__name__
        path_list = child_name.split('/')
        temp_res = None
        path_list = [path for path in path_list if path]
        path_len = len(path_list)
        for index, path in enumerate(path_list):
            if index == 0:
                temp_res = GO.web_root
            if index == path_len - 1:
                res = cls()
                temp_res.putChild(path, res)
                return
            else:
                res = temp_res.children.get(path)
                if not res:
                    res = Resource()
                    temp_res.putChild(path, res)
            temp_res = res


class RemoteServiceHandle(object):
    """
    """

    def __init__(self, remote_name):
        """
        """
        self.remote_name = remote_name

    def __call__(self, target):
        """
        """
        GO.remote[self.remote_name].reference.service.map_target(target)