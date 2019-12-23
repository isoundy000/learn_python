# -*- encoding: utf-8 -*-
'''
Created on 2019年11月15日

@author: houguangdong
'''


from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory
from twisted.protocols import basic
from twisted.application import service, internet
import pymysql


port = 9999
iface = '127.0.0.1'


class Mornitor_Protocol(basic.LineReceiver):

    def __init__(self):
        db = pymysql.Connection(host='127.0.0.1', database='dong', user='root', password='123456', charset='utf8')
        self.cur = db.cursor()
        data = self.cur.execute("select * from tmp_user;")
        print data

    def ruku(self, line):
        ip = self.transport.getPeer().host
        # 获取客户端IP
        line = line.split(':::')
        # 使用:::分割原始数据
        if line[1] in ['cpu', 'mem', 'disk', 'tcp', 'net', 'process_down']:
            # 根据数据包头来确定使用insert还是update，当是tcp包头的时候插入，其余的更新
            if line[1] == 'tcp':
                sql = "insert into tmp_user values('dd', 'm', 1, 'ff');"
                self.cur.execute(sql)
            else:
                line_again = line[3].split('::')
                sql = "update tmp_user set age = '%s' where name = '%s' % (3, 'dd');"
                self.cur.execute(sql)

    def connectionMade(self):
        print 'Connected'

    def lineReceived(self, line):
        print line
        self.ruku(line)
        # 接受到数据之后执行入库操作！

    def connectionLost(self, reason='connectionDone'):
        self.cur.close()
        print 'The db is close... ok!'


class Minitor_Factory(ServerFactory):
    # 还没想好要初始化什么
    protocol = Mornitor_Protocol

    def __init__(self, service):
        self.service = service


class Fish_Service(service.Service):

    def startService(self):
        service.Service.startService(self)

    def stopService(self):
        return self._port.stopListening()


top_service = service.MultiService()
fish_service = Fish_Service()
factory = Minitor_Factory(Fish_Service)
fish_service.setServiceParent(top_service)

tcp_service = internet.TCPServer(port, factory, interface=iface)
tcp_service.setServiceParent(top_service)

application = service.Application("SmallFish--Monitor")
# this hooks the collection we made to the application
top_service.setServiceParent(application)
# 使用 twisted -y main.py (脚本名称) 就可以以守护进程的方式运行了！