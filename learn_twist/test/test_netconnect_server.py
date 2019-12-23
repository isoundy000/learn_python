# -*- encoding: utf-8 -*-
'''
Created on 2019年11月17日 18:16

@author: houguangdong
'''

import sys, os
# from twisted.internet import default
# default.install()
from twisted.python.runtime import platform

# print(os.name, '000000000000')                      # posix
if os.name != 'nt':
    try:
        if platform.isLinux():
            try:
                from twisted.internet.epollreactor import install
            except ImportError:
                from twisted.internet.pollreactor import install
        elif platform.getType() == 'posix' and not platform.isMacOSX():
            from twisted.internet.pollreactor import install
        else:
            from twisted.internet.selectreactor import install
    except ImportError:
        from twisted.internet.selectreactor import install
    install()



from twisted.internet import reactor
from twisted.python import log
from learn_twist.utils import services
from learn_twist.netconnect.protoc import LiberateFactory

reactor = reactor
service = services.CommandService("loginService", run_style=services.Service.PARALLEL_STYLE)


def serviceHandle(target):
    '''服务处理
    @param target: func Object
    '''
    service.map_target(target)
    
factory = LiberateFactory()


def doConnectionLost(conn):
    print(conn.transport)


factory.do_conn_lost = doConnectionLost


def serverstart():
    '''服务配置
    '''
    log.startLogging(sys.stdout)
    factory.add_service_channel(service)
    reactor.callLater(10, factory.push_object, 111, 'asdfe', [0])
    reactor.callLater(15, factory.lose_conn, 0)
    reactor.listenTCP(9999, factory)
    reactor.run()


@serviceHandle
def echo_1(_conn, data):
    addr = _conn.transport.client
    print(addr)
    return "欢迎"


if __name__ == "__main__":
    serverstart()
