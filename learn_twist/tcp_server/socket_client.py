# -*- encoding: utf-8 -*-
'''
Created on 2019年11月16日

@author: houguangdong
'''

from socket import *

s = socket(AF_INET, SOCK_STREAM)

remote_host = gethostname()
print 'remote_ip', remote_host
port = 9999
s.connect((remote_host, port))      # 发起连接

'''
socket对象的getpeername()和getsockname()方法都返回包含一个IP地址和端口的二元组
（这个二元组的形式就像你传递给connect和bind的）。
getpeername返回所连接的远程socket的地址和端口，getsockname返回关于本地socket的相同信息。
'''
print "Connected from", s.getsockname()     # 返回本地IP和端口
print "Connected to", s.getpeername()       # 返回服务端IP和端口

s.send('i am form client')

# print 'what i got from select server is: '
# print s.recv(1024)

'''
send,sendto,recv和recvfrom方法都有一个可选的参数flags，默认值为0。
你可以通过对socket.MSG_*变量进行组合（按位或）来建立flags的值。
这些值因平台而有所不同，但是最通用的值如下所示：

MSG_OOB:处理带外数据（既TCP紧急数据）。
MSG_DONTROUTE:不使用路由表；直接发送到接口。
MSG_PEEK:返回等待的数据且不把它们从队列中删除。

'''