# -*- encoding: utf-8 -*-
'''
Created on 2019年11月16日

@author: houguangdong
'''


from twisted.python import log
from zope.interface import Interface, implementer


# typing
from typing import Dict
from learn_twist.distributed.child import Child


class _ChildesManager(Interface):
    """节点管理器接口
    """

    def __init__(self):
        """初始化接口
        """

    def get_child_by_id(self, child_id):
        """根据节点id获取节点实例
        @param child_id:
        @return:
        """

    def get_child_by_name(self, child_name):
        """根据节点的名称获取节点实例
        @param child_name:
        @return:
        """

    def add_child(self, child):
        """添加一个child节点
        @param child:
        @return:
        """

    def drop_child(self, *arg, **kw):
        """删除一个节点
        @param arg:
        @param kw:
        @return:
        """

    def call_child(self, *args, **kw):
        """调用子节点的接口
        @param args:
        @param kw:
        @return:
        """

    def call_child_by_name(self, *args, **kw):
        """调用子节点的接口
        @param args:
        @param kw:
        @return:
        """

    def drop_child_by_id(self, child_id):
        """删除一个child 节点
        @param child_id:
        @return:
        """

    def drop_child_session_id(self, session_id):
        """根据session_id删除child节点
        """


@implementer(_ChildesManager)
class ChildesManager(object):
    """子节点管理器
    """

    def __init__(self):
        """初始化子节点管理器
        """
        self._childes = {}  # type: Dict[str, Child]

    def get_child_by_id(self, child_id):
        return self._childes.get(child_id)

    def get_child_by_name(self, child_name):
        """根据节点的名称获取节点实例
        @param child_name:
        @return:
        """
        for child_id, child in self._childes.items():
            if child.child_name == child_name:
                return self._childes[child_id]
        return None

    def add_child(self, child: Child):
        """添加一个child节点
        @param child:
        @return:
        """
        child_id = child.child_id
        if child_id in self._childes.values():
            raise "child node %s exists" % child_id
        self._childes[child_id] = child

    def drop_child(self, child: Child):
        """删除一个child 节点
        @param child:
        @return:
        """
        child_id = child.child_id
        try:
            del self._childes[child_id]
        except Exception as e:
            log.msg(str(e))

    def drop_child_by_id(self, child_id):
        """删除一个child 节点
        @param child_id:
        @return:
        """
        try:
            del self._childes[child_id]
        except Exception as e:
            log.msg(str(e))

    def call_child(self, child_id, *args, **kw):
        """调用子节点的接口
        @param child_id:
        @param args:
        @param kw:
        @return:
        """
        child = self._childes.get(child_id, None)
        if not child:
            log.err("child %s doesn't exists" % child_id)
            return
        return child.call_back_child(*args, **kw)

    def call_child_by_name(self, child_name, *args, **kw):
        """调用子节点的接口
        @param child_name:
        @param args:
        @param kw:
        @return:
        """
        child = self.get_child_by_name(child_name)
        log.msg('gggggggggggggggg', child)
        if not child:
            log.err("child %s doesn't exists" % child_name)
            return
        return child.call_back_child(*args, **kw)

    def get_child_by_session_id(self, session_id):
        """根据sessionID获取child节点信息
        """
        for child in self._childes.values():
            if child._transport.broker.transport.sessionno == session_id:
                return child
        return None

    @property
    def childes(self):
        return self._childes

