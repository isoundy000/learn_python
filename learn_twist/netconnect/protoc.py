# -*- encoding: utf-8 -*-
'''
Created on 2019年11月17日 20:19

@author: houguangdong
'''

from twisted.internet import protocol, reactor
from twisted.internet.protocol import connectionDone
from twisted.python import log
from learn_twist.netconnect.datapack import DataPackProto
from learn_twist.netconnect.manager import ConnectionManager

# typing
from typing import Union
from typing import Generator
from learn_twist.utils.services import Service


reactor = reactor


class LiberateProtocol(protocol.Protocol):
    """协议
    """
    buff = b""

    def __init__(self):
        self.data_handler = None  # type: Union[None, Generator]
        self.factory = None  # type: Union[None, LiberateFactory]

    def connectionMade(self):
        """连接建立处理
        """
        self.factory.conn_manager.add_conn(self)
        self.factory.do_conn_made(self)

        self.data_handler = self.data_handle_coroutine()
        self.data_handler.__next__()

    def connectionLost(self, reason=connectionDone):
        """连接断开处理
        @param reason:
        @return:
        """
        log.msg('Client {0} login out.'.format(self.transport.sessionno))
        self.factory.do_conn_lost(self)
        self.factory.conn_manager.drop_conn_by_id(self.transport.sessionno)

    def dataReceived(self, data):
        """数据到达处理
        @param data: 客户端传送过来的数据
        @return:
        """
        self.data_handler.send(data)

    def safe_to_write_data(self, data, command):
        """线程安全的向客户端发送数据
        @param data: str 要向客户端写的数据
        @param command:
        """
        if not self.transport.connected or data is None:
            return
        send_data = self.factory.produce_result(data, command)
        reactor.callFromThread(self.transport.write, send_data)

    def data_handle_coroutine(self):
        """
        """

        def deffer_error_handle(e):
            """ 延迟对象的错误处理
            @param e:
            @return:
            """
            log.err(str(e))
            return

        dpp = self.factory.dpp

        length = dpp.get_head_length()
        while True:
            data = yield
            self.buff += data
            while self.buff.__len__() >= length:
                unpack_data = dpp.unpack(self.buff[:length])
                if not unpack_data.get('result'):
                    log.msg('illegal data package --')
                    self.transport.loseConnection()
                    break
                command = unpack_data.get('command')
                r_length = unpack_data.get('length')
                request = self.buff[length:length + r_length]
                if request.__len__() < r_length:
                    log.msg('some data lose')
                    break
                self.buff = self.buff[length + r_length:]
                d = self.factory.do_data_received(self, command, request)
                if not d:
                    continue
                d.addCallback(self.safe_to_write_data, command)
                d.addErrback(deffer_error_handle)


class LiberateFactory(protocol.ServerFactory):
    """协议工厂
    """

    protocol = LiberateProtocol

    def __init__(self, dpp=DataPackProto()):
        """初始化
        @param dpp: 数据解压对象
        """

        self.service = None                         # type: Union[Service, None]
        self.conn_manager = ConnectionManager()     # type: ConnectionManager
        self.dpp = dpp                              # type: DataPackProto

    def set_dpp(self, dpp: DataPackProto):
        """
        """
        self.dpp = dpp

    def do_conn_made(self, conn):
        """当连接建立时的处理
        """
        pass

    def do_conn_lost(self, conn):
        """连接断开时的处理
        """
        pass

    def add_service_channel(self, service):
        """添加服务通道
        """
        self.service = service

    def do_data_received(self, conn, command_id, data):
        """数据到达时的处理
        """
        log.msg("data received:", conn, command_id, data)
        defer_tool = self.service.call_target(command_id, conn, data)
        return defer_tool

    def produce_result(self, response, command_id):
        """产生客户端需要的最终结果
        @param response: str 分布式客户端获取的结果
        @param command_id: 命令编号
        """
        return self.dpp.pack(response, command_id)

    def lose_conn(self, conn_id):
        """主动端口与客户端的连接
        """
        self.conn_manager.lose_conn(conn_id)

    def push_object(self, topic_id, msg, sends):
        """服务端向客户端推消息
        @param topic_id: int 消息的主题id号
        @param msg: 消息的类容，proto结构类型
        @param sends: 推向的目标列表(客户端id 列表)
        """
        self.conn_manager.push_msg(topic_id, msg, sends)