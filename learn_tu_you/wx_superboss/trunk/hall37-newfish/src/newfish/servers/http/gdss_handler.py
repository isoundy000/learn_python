# -*- coding=utf-8 -*-
"""
Created by lichen on 2019-11-11.
"""

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
        """检查惩罚状态的参数"""
        punishState = runhttp.getParamInt(key, "")
        if isinstance(punishState, int):
            return None, punishState
        return "ERROR of punishState !" + str(punishState), None

    @markHttpMethod(httppath="/_gdss/newfish/user/mail/list")
    def doGetUserMailList(self, userId):
        """
        GM工具查询玩家邮件接口
        """
        mo = MsgPack()
        ec, result = self.checkCode()
        if ec == 0:
            result = user_rpc.getUserMailList(userId)
            ftlog.debug("doGetUserMailList->", result)
        if ec != 0:
            mo.setError(ec, result)
        else:
            mo.setResult("mails", result)
        return mo

    @markHttpMethod(httppath="/_gdss/newfish/user/mail/remove")
    def doRemoveUserMail(self, userId, mailId):
        """
        GM工具删除玩家邮件接口
        """
        mo = MsgPack()
        ec, result = self.checkCode()
        if ec == 0:
            result = user_rpc.removeUserMail(userId, mailId)
        if ec != 0:
            mo.setError(ec, result)
        else:
            mo.setResult("mails", result)
        return mo

    @markHttpMethod(httppath="/_gdss/newfish/user/getChatPunish")
    def doGetChatPunish(self, userId):
        """
        GM工具获取玩家聊天惩罚状态
        """
        mo = MsgPack()
        ec, result = self.checkCode()
        if ec == 0:
            result = user_system.getChatPunish(userId)
        if ec != 0:
            mo.setError(ec, result)
        else:
            mo.setResult("punishState", result)
        return mo

    @markHttpMethod(httppath="/_gdss/newfish/user/setChatPunish")
    def doSetChatPunish(self, userId, punishState):
        """
        GM工具设置玩家聊天惩罚状态
        """
        mo = MsgPack()
        ec, result = self.checkCode()
        if ec == 0:
            result = user_system.setChatPunish(userId, punishState)
        if ec != 0:
            mo.setError(ec, result)
        else:
            mo.setResult("code", result)
        return mo