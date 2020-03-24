#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# 通过subprocess模块，实现远程shell命令行命令
try:
    import socketserver                     # python3
except:
    import SocketServer as socketserver     # python2
import struct
import subprocess


class MyTcpHandler(socketserver.BaseRequestHandler):

    def handle(self):
        while True:
            print('客户端<%s,%s>已连接' % self.client_address)
            try:
                cmd = self.request.recv(1024).decode('utf-8')
                res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout = res.stdout.read()
                stderr = res.stdout.read()
                head = struct.pack('i', len(stdout + stderr))
                self.request.send(head)
                self.request.send(stdout)
                self.request.send(stderr)
            except ConnectionResetError:
                print('客户端<%s,%s>已中断连接' % self.client_address)
                self.request.close()
                break


if __name__ == '__main__':
    server = socketserver.ThreadingTCPServer(('127.0.0.1', 8888), MyTcpHandler)
    server.serve_forever()