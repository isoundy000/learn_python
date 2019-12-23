# -*- encoding: utf-8 -*-
'''
Created on 2019年11月17日 20:24

@author: houguangdong
'''

from zope.interface import Interface


class IDataPackProto(Interface):

    def get_head_length(self):
        """获取数据包的长度
        """
        pass

    def unpack(self):
        """解包
        """

    def pack(self):
        """打包数据包
        """
