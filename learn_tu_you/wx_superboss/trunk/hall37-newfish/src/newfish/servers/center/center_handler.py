#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/17

from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from hall.servers.common.base_checker import BaseMsgPackChecker


@markCmdActionHandler
class CenterTcpHandler(BaseMsgPackChecker):

    def __init__(self):
        pass