#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


# 真正应用场景可以是上传或者下载一个大文件的时候，这时就必须要提前知道接收的文件实际大小，
# 做到100%精确的接收每一个数据，这时就需要收数据前获取即将收到的文件大小，然后对症下药，做到精确接收，
# 但实现方法不一定非要用struct模块，struct模块只是解决粘包问题中的一个官方正式的方法，自己还可以有自己的想法，
# 比如先直接把要发送文件的大小已字符串的格式发送过去，然后再发送这个文件，目的只有一个，知道我接收的文件的大小，精准接收文件。
# 下面写一个客户端从服务端下载文件的实例，供大家参考：（假设下载文件在服务端文件同一级）

import socket
import time
import struct
import json

# 计算当前文件夹下文件的md5值、大小
import os, hashlib


def get_info(file_name):
    file_info = {}
    base_dir = os.path.dirname(__file__)
    file_dir = os.path.join(base_dir, file_name)
    if os.path.exists(file_dir):
        # md5计算时文件数据是放在内存中的, 当我们计算一个大文件时，可以用update方法进行分步计算，
        # 每次添加部分文件数据进行计算，减少内存占用。
        with open(file_dir, 'rb') as f:
            le = 0
            d5 = hashlib.md5()
            for line in f:
                le += len(line)
                d5.update(line)
            file_info['lenth'] = le         # 将文件长度加入报头字典
            file_md5 = d5.hexsigest()
            file_info['md5'] = file_md5     # 将文件md5加入报头字典
            file_size = os.path.getsize(file_dir) / float(1024 * 1024)
            file_info['size(MB)'] = round(file_size, 2)     # 将文件大小加入报头字典
            return file_info
    else:
        return file_info


server = socket.socket()
server.bind(('127.0.0.1', 8888))
server.listen(5)
while True:
    conn, client_addr = server.accept()
    print('%s >:客户端(%s)已连接' % (time.strftime('%Y-%m-%d %H:%M:%S'), client_addr))
    while True:
        try:
            download_filename = conn.recv(1024).decode('utf-8')
            download_file_info_dic = get_info(download_filename)
            j_head = json.dumps(download_file_info_dic)             # 将文件信息字典转成json字符串格式
            head = struct.pack('i', len(j_head))
            conn.send(head)
            conn.send(j_head.encode('utf-8'))
            if not download_file_info_dic:
                continue
            with open(download_filename, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    conn.send(data)
                # for line in f:
                #     conn.send(line)

        except ConnectionResetError:
            print('%s >:客户端(%s)已断开' % (time.strftime('%Y-%m-%d %H:%M:%S'), client_addr))
            conn.close()
            break