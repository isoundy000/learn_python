# -*- encoding: utf-8 -*-
'''
Created on 2019年11月16日

@author: houguangdong
'''

# socket client end
from socket import *

s = socket(AF_INET, SOCK_STREAM)
remote_host = gethostname()
print 'remote_host:', remote_host
port = 9999
s.connect((remote_host, port))              # 发起连接
print("Connected from", s.getsockname())    # 返回本地IP和端口
print("Connected to", s.getpeername())      # 返回服务端IP和端口
s.send('i am form client\r\n')              # 发送一行字符串（以\r\n 结束）到服务器端
s.send('next message\r\n')

print 'the msg i got from select server is:'
print s.recv(1024)
