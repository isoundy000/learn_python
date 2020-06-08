#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from Source.Log.Write import Log
import gevent.socket
from gevent import monkey; monkey.patch_socket()
import socket as l_socket


def RecvAll(sock, length):
    """
    接收数据
    :param sock: 文件标识符
    :param length: 数据长度
    :return:
    """
    # Log.Write("recvall fileno: %d datalen: %d" % (sock.fileno(), length))
    data = ""
    tmpData = ""
    if length == 0:
        return data
    tmpLength = length
    while True:
        try:
            gevent.socket.wait_read(sock.fileno)  # gevent
            tmpData = sock.recv(tmpLength)
        except l_socket.error, le:
            Log.Write("recv all exception:", le)
            if le.errno == 11 or le.errno == 110 or le.errno == 4:
                continue
            else:
                return None

        if len(tmpData) == 0:
            Log.Write("fileno: %d recv nothing" % sock.fileno())
            return None

        data += tmpData
        tmpLength -= len(tmpData)

        if tmpLength == 0:
            return data


LEN_1M = 1024 * 1024
LEN_10K = 10 * 1024
LEN_4K = 4 * 1024
LEN_2K = 2 * 1024
LEN_1K = 1 * 1024
LEN_LIMITED = LEN_1M


def SendAll(sock, data):
    """
    发送数据
    :param sock: 文件流
    :param data: 发送的数据
    :return:
    """
    # Log.Write("sendall fileno: %d datalen: %d" % (sock.fileno(), len(data)))
    datalen = len(data)
    if datalen <= LEN_LIMITED:
        try:
            gevent.socket.wait_write(sock.fileno())
            sock.sendall(data)
        except l_socket.error, le:
            # if le.errno == 11 or le.errno == 110 or le.errno == 4:
            #     continue
            # else:
            #     return None
            return False
        return True
    else:
        # Log.Write("Send Package Len more 4K, datalen: %d" % (datalen,))
        leftlen = datalen               # 数据
        sendlen = leftlen
        while True:
            if leftlen >= LEN_LIMITED:
                sendlen = LEN_LIMITED
            elif leftlen <= 0:
                return True
            else:
                sendlen = leftlen
            # Log.Write("want send %d" % (sendlen,))
            try:
                gevent.socket.wait_write(sock.fileno())
                frompos = datalen - leftlen
                topos = frompos + sendlen
                senddata = data[frompos: topos]
                # Log.Write("senddata from: %d to: %d len: %d" % (frompos, topos, len(senddata)))
                sendlen = sock.send(senddata)
                leftlen -= sendlen
                # Log.Write("send %d left %d" % (sendlen, leftlen))
            except l_socket.error, le:
                if le.errno == 11 or le.errno == 110 or le.errno == 4:
                    continue
                else:
                    Log.Write("SelfSocket Send Error:" + str(le))
                    return False


def SendAll2(sock, data):
    '''
    发送数据
    :param sock:
    :param data:
    :return:
    '''
    # Log.Write("sendall fileno: %d datalen: %d" % (sock.fileno(), len(data)))
    try:
        gevent.socket.wait_write(sock.fileno())
        sock.sendall(data)
    except l_socket.error, le:
        # if le.errno == 11 or le.errno == 110 or le.errno == 4:
        #     continue
        # else:
        #     return None
        return False
    return True