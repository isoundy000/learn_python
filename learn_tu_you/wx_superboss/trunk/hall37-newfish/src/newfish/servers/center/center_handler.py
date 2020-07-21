# -*- coding=utf-8 -*-
"""
Created by lichen on 16/12/13.
"""

from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from hall.servers.common.base_checker import BaseMsgPackChecker


@markCmdActionHandler
class CenterTcpHandler(BaseMsgPackChecker):

    def __init__(self):
        pass

