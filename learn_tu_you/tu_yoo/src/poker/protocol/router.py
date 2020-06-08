#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6



def sendToUsers(msgpack, userIdList):
    '''
    发送消息至一组用户的客户端
    '''
    pass


def sendTableServer(msgpack, roomId):
    '''
    发送一个消息至指定的桌子处理进程
    '''
    return _communicateTableServer(0, roomId, msgpack, 'S6', 0)


def _communicateTableServer(userId, roomId, msgpack, head1, isQuery, timeout=None, notimeoutex=0):
    pass