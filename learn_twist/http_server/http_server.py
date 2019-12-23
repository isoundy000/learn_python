# -*- encoding: utf-8 -*-
'''
Created on 2019年11月16日

@author: houguangdong
'''

# 4. http请求和响应报文
# 功能：
# 返回客户端的请求信息（http请求报文）

from twisted.protocols import basic
from twisted.internet import protocol, reactor


class HttpEchoProtocol(basic.LineReceiver):

    def __init__(self):
        self.lines = []
        self.gotRequest = False

    def lineReceived(self, line):
        self.lines.append(line)
        if not line and not self.gotRequest:
            print('the msg browser client send to me(http request head) is:')
            for e in self.lines:
                print(e)
            self.sendResponse()
            self.gotRequest = True

    def sendResponse(self):
        # 0121 "\r\n".join(self.lines)  列表中的每一条请求消息字符串均用\r\n连接起来
        responseBody = "Dear Client,the msg you sent to me are as followings:\r\n\r\n" + "\r\n".join(self.lines)
        # send msg to the browser client  0121
        # http response head 0121
        self.sendLine("HTTP/1.0 200 OK")                # 请求成功 0121 （必须） sendLine自动在消息字符串末尾添加\r\n
        self.sendLine("Content-Type: text/plain")
        self.sendLine("Content-Length: %i" % len(responseBody))
        # 下面两行语句[1][2]等价  #0121
        # self.sendLine("")                             # http头结束标志  （必须） \r\n  [1]
        self.transport.write("\r\n")  # [2]
        self.transport.write(responseBody)              # 向客户端发送数据


f = protocol.ServerFactory()
f.protocol = HttpEchoProtocol
reactor.listenTCP(9999, f)
reactor.run()