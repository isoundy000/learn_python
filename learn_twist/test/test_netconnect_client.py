# -*- encoding: utf-8 -*-
'''
Created on 2019年11月18日 12:21

@author: houguangdong
'''

import time

from learn_twist.utils.const import const
from socket import AF_INET, SOCK_STREAM, socket
import sys
if sys.version[:1] == "3":
    from _thread import start_new
# else:
#     from thread import start_new

import struct
HOST = 'localhost'
PORT = 9999
BUFSIZE = 1024
ADDR = (HOST, PORT)
client = socket(AF_INET, SOCK_STREAM)
client.connect(ADDR)


def sendData(sendstr, commandId):
    HEAD_0 = chr(0).encode('utf-8')         # latin1
    HEAD_1 = chr(0).encode('utf-8')
    HEAD_2 = chr(0).encode('utf-8')
    HEAD_3 = chr(0).encode('utf-8')
    ProtoVersion = chr(0).encode('utf-8')
    ServerVersion = 0
    sendstr = sendstr
    data = struct.pack(const.struct_fmt, HEAD_0, HEAD_1, HEAD_2,
                       HEAD_3, ProtoVersion, ServerVersion,
                       len(sendstr) + 4, commandId)
    send_data = data + sendstr
    return send_data


def resolveRecvData(data):
    head = struct.unpack(const.struct_fmt, data[:17])
    length = head[6]
    data = data[17: 17 + length]
    return data

s1 = time.time()


def xrange(x):
    n = 0
    while n < x:
        yield n
        n += 1


def start():
    for i in xrange(10):
        data = sendData(b'asdfe', 1)
        client.sendall(data)


for i in range(10):
    start_new(start, ())


while True:
    pass
