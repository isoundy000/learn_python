#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/29


import stackless
from freetime.core.protocol import FTHttpRequest, FTHttpChannel
import freetime.entity.service as ftsvr


class MyHttpRequest(FTHttpRequest):

    def handleRequest(self):
        pass


class MyHttpChannel(FTHttpChannel):
    requestFactory = MyHttpRequest