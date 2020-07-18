#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/17

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol.decorator import markHttpHandler, markHttpMethod
from poker.protocol import runhttp
from hall.servers.common.base_http_checker import BaseHttpMsgChecker
from newfish.servers.util.rpc import user_rpc
from newfish.entity import util, user_system


@markHttpHandler
class FishHttpGdssHandler(BaseHttpMsgChecker):

    def checkCode(self):
        code = ""
        datas = runhttp.getDict()
        if "code" in datas:
            code = datas["code"]
            del datas["code"]

        signStr = util.httpParamsSign(datas)
        if code != signStr:
            return -1, "Verify code error"
        return 0, None

    def _check_param_mailId(self, key, params):
        """检查邮件Id参数"""
        mailId = runhttp.getParamInt(key, "")
        if isinstance(mailId, int):
            return None, mailId
        return "ERROR of mailId !" + str(mailId), None

    def _check_param_punishState(self, key, params):
        punishState = runhttp.getParamInt(key, "")
        if isinstance(punishState, int):
            return None, punishState
        return "ERROR of punishState !" + str(punishState), None

    



