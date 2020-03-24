#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


import socket
import time
import struct
import json


# 进度条显示
def progress(percent, width=30):
    text = ('\r[%%-%ds]' % width) % ('x' * int(percent * width))
    text = text + '%3s%%'
    text = text % (round(percent * 100))
    print(text)


while True:
    try:
        client = socket.socket()
        client.connect(('127.0.0.1', 8888))
        print('%s >:已连接到服务端' % time.strftime('%Y-%m-%d %H:%M:%S'))
        while True:
            try:
                file_name = input('请输入下载文件名称：')
                client.send(file_name.encode('utf-8'))

                head = client.recv(4)       # 收报头
                j_dic_lenth = struct.unpack('i', head)[0]       # 解压报头，获取json格式的文件信息字典的长度
                j_head = client.recv(j_dic_lenth)    # 收json格式的信息字典
                file_info_dic = json.loads(j_head)  # 反序列化json字典，得到文件信息字典
                if not file_info_dic:
                    print('文件不存在')
                    continue
                file_lenth = file_info_dic.get('lenth')
                file_size = file_info_dic.get('size(MB)')
                file_md5 = file_info_dic.get('md5')
                rec_len = 0
                with open('copy_' + file_name, 'wb') as f:
                    while rec_len < file_lenth:
                        data = client.recv(1024)
                        f.write(data)
                        rec_len += len(data)
                        per = rec_len / file_lenth
                        progress(per)
                    print()
                    # print('下载比例：%6s %%'%)
                    if not rec_len:
                        print('文件不存在')
                    else:
                        print('文件[%s]下载成功: 大小：%s MB|md5值：[%s]' % (file_name, file_size, file_md5))
            except ConnectionResetError:
                print('%s >:服务端已终止' % time.strftime('%Y-%m-%d %H:%M:%S'))
                client.close()
                break

    except ConnectionRefusedError:
        print('%s >:无法连接到服务器' % time.strftime('%Y-%m-%d %H:%M:%S'))

# 文件上传同理，只是换成客户端给服务端发送文件，服务端接收。