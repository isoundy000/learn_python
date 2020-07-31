#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/29
import freetime.entity.service as ftsvr
import freetime.util.log as ftlog
import freetime.support.tcpagent.wrapper as ftagent
from freetime.support.tcpagent.protocol import S2AProtocol


"""
继承freetime提供的protocol基类，
实现getTaskletFunc方法，用于识别请求包，返回对应的tasklet入口执行方法
在这里，可以实现消息注册机制，以便更好的管理消息处理方法
"""
class S2AProto(S2AProtocol):
    pass