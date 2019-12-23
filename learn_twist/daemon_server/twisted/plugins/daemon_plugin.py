# -*- encoding: utf-8 -*-
'''
Created on 2019年11月16日

@author: houguangdong
'''


from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory
from twisted.protocols import basic
from twisted.application import service, internet
from zope.interface import implements
from twisted.python import usage, log
from twisted.plugin import IPlugin
import pymysql


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


class Mornitor_Factory(ServerFactory):

    def __init__(self, s):
        self.service = s

    protocol = Mornitor_Protocol


class Fish_Service(service.Service):

    def __init__(self):
        self._port = 9999

    def startService(self):
        service.Service.startService(self)


class Options(usage.Options):

    optParameters = [
        ['port', 'p', 9999, 'The port number to listen on.'],
        ['iface', None, 'localhost', 'The interface to listen on.'],
    ]


class Fish_Service_Make(object):

    implements(service.IServiceMaker, IPlugin)

    tapname = "smallfish"                           # 这里给插件取个好听的名字
    description = "A monitor daemon!"               # 插件的描述
    options = Options                               # 可供插件选择的选项

    def makeService(self, options):
        top_service = service.MultiService()        # 定义service容器

        fish_service = Fish_Service()               # 实例化自己定义的service
        fish_service.setServiceParent(top_service)  # 把自定义的service丢进容器

        factory = Mornitor_Factory(fish_service)    # 工厂化自定义服务
        tcp_service = internet.TCPServer(int(options['port']), factory, interface=options['iface'])  # tcp连接工厂化，一些连接参数通过option获取

        tcp_service.setServiceParent(top_service)   # 把tcp sevice丢进容器
        return top_service


service_maker = Fish_Service_Make()


# 要使用twisted + 插件名称的方式运行程序有几点要求：
# 1.插件程序必须在python的搜索路径
# export PYTHONPATH=$PYTHONPATH:/home/user/yourpath
# 2.插件程序必须处于twisted/plugins 这样的目录结构下
# your projects/
# ├──
# twisted
# └── plugins
#     └──xxxx_plugin.py