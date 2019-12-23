# -*- encoding: utf-8 -*-
'''
Created on 2019年11月17日 20:19

@author: houguangdong
'''

from twisted.python import log
import struct
import six
from zope.interface import implementer

from learn_twist.utils.interfaces import IDataPackProto
from learn_twist.utils.const import const


class DataPackError(Exception):
    """An error occurred binding to an interface"""

    def __str__(self):
        s = self.__doc__
        if self.args:
            s = '%s: %s' % (s, ' '.join(self.args))
        s = '%s.' % s
        return s


zero_byte = six.int2byte(0)


@implementer(IDataPackProto)
class DataPackProto(object):
    """数据包协议
    """

    def __init__(self,
                 head_0: int = 0,
                 head_1: int = 0,
                 head_2: int = 0,
                 head_3: int = 0,
                 proto_version: int = 0,
                 server_version: int = 0):
        """
        @param head_0: 协议头0
        @param head_1: 协议头1
        @param head_2: 协议头2
        @param head_3: 协议头3
        @param proto_version: 协议头版本号
        @param server_version: 服务版本号
        """

        self.head_0 = head_0
        self.head_1 = head_1
        self.head_2 = head_2
        self.head_3 = head_3
        self.proto_version = proto_version
        self.server_version = server_version

    def set_head_0(self, head_0):
        self.head_0 = head_0

    def set_head_1(self, head_1):
        self.head_1 = head_1

    def set_head_2(self, head_2):
        self.head_2 = head_2

    def set_head_3(self, head_3):
        self.head_3 = head_3

    def set_proto_version(self, proto_version):
        self.proto_version = proto_version

    def set_server_version(self, server_version):
        self.server_version = server_version

    @staticmethod
    def get_head_length():
        """获取数据包的长度
        """
        return 17

    def unpack(self, data_pack):
        """解包
        @param data_pack:
        @return:
        """
        try:
            ud = struct.unpack(const.struct_fmt, data_pack)
        except DataPackError as de:
            log.err(de)
            return {'result': False, 'command': 0, 'length': 0}
        head_0 = six.byte2int(ud[0])
        head_1 = six.byte2int(ud[1])
        head_2 = six.byte2int(ud[2])
        head_3 = six.byte2int(ud[3])
        proto_version = six.byte2int(ud[4])
        server_version = ud[5]
        length = ud[6] - 4
        command = ud[7]
        if head_0 != self.head_0 or head_1 != self.head_1 or head_2 != self.head_2 or head_3 != self.head_3 or \
                proto_version != self.proto_version or server_version != self.server_version:
            return {'result': False, 'command': 0, 'length': 0}
        return {'result': True, 'command': command, 'length': length}

    def pack(self, response, command: int):
        """打包数据包
        """

        log.msg(response, command, type(response))

        head_0 = six.int2byte(self.head_0)
        head_1 = six.int2byte(self.head_1)
        head_2 = six.int2byte(self.head_2)
        head_3 = six.int2byte(self.head_3)
        proto_version = six.int2byte(self.proto_version)
        server_version = self.server_version

        if not isinstance(response, bytes):
            response = bytes(response, encoding='utf8')

        length = response.__len__() + 4
        data = struct.pack(const.struct_fmt,
                           head_0, head_1, head_2, head_3, proto_version, server_version, length, command)

        data = data + response
        return data