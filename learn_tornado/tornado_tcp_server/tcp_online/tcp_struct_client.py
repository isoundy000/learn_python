#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import socket
import struct

while True:
    try:
        client = socket.socket()
        client.connect(('127.0.0.1', 8888))
        print('已连接到服务端')
        while True:
            try:
                msg = 'abcdefghijklmnopqrstuvwxyz1234567890'.encode('utf-8')
                head = struct.pack('i', len(msg))
                client.send(head)
                client.send(msg)
            except ConnecionResetError:
                print('服务端已中断连接')
                client.close()
                break

    except ConnectionRefusedError:
        print('无法连接到服务器')
