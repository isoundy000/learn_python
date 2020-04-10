#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import hashlib
import logging
import json
import os
import tornado.websocket
from tornado.escape import json_encode
from tornado.escape import json_decode
import tornado.web
import tornado.gen
import tornado.ioloop
import urllib
from tornado.httpclient import AsyncHTTPClient
from tornado.httputil import url_concat

from common.cjsonencoder import CJsonEncoder
from common.configmanager import ConfigManager

from handlers.configfilehandler import set_online_and_reload_config
from basehandler import BaseHandler
from logic.users import UsersObject
from logic.partner import PartnerObject



class AjaxValidateHandler(BaseHandler):

    def get(self):
        user_name = self.get_argument("username").strip()
        pass_word = hashlib.md5(self.get_argument("password").strip()).hexdigest()
        user_object = UsersObject()
        data = user_object.validate_user(user_name, pass_word)
        if data["status"] == 0:
            p_data = PartnerObject().get_one(data["channel"])
            if p_data and p_data["name"]:
                channel = p_data["name"]
            else:
                channel = u"所有渠道"
            self.set_cookie("user_session", user_name, expires_days=None)
            self.set_cookie("user_role1", str(data["role1"]), expires_days=None)
            self.set_cookie("user_role2", str(data["role2"]), expires_days=None)
            self.set_cookie("user_role3", str(data["role3"]), expires_days=None)
            self.set_cookie("user_role4", str(data["role4"]), expires_days=None)
            self.set_cookie("user_role5", str(data["role5"]), expires_days=None)
            self.set_cookie("user_upload", str(data["upload"]), expires_days=None)
            self.set_cookie("user_channel", str(data["channel"]), expires_days=None)
            self.set_cookie("user_custom", str(data["custom"]), expires_days=None)
            self.set_cookie("user_approve", str(data["approve"]), expires_days=None)
            self.set_cookie("name", urllib.quote(data["name"].encode('utf8')), expires_days=None)
            self.set_cookie("channel_name", urllib.quote(channel.encode('utf8')), expires_days=None)
        self.write(json.dumps(data, cls=CJsonEncoder))


class UpdatePassHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        old_pass = hashlib.md5(self.get_argument("old_pass").strip()).hexdigest()
        new_pass = hashlib.md5(self.get_argument("new_pass").strip()).hexdigest()
        data = UsersObject.update_pass(self.current_user, old_pass, new_pass)
        self.write(json.dumps(data, cls=CJsonEncoder))


class AjaxGetAllUserHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        data = UsersObject().get_all_user()
        self.write(json.dumps(data, cls=CJsonEncoder))


class AjaxOperateUserHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        user_id = self.get_argument("user_id")
        name = self.get_argument("name")
        user_name = self.get_argument("user_name")
        user_pass = self.get_argument("user_pass")
        user_type = json_decode(self.get_argument("user_type"))
        user_game = self.get_argument("user_game")
        upload_is = self.get_argument("upload_is")
        is_start = self.get_argument("is_start")
        is_recharge = self.get_argument("is_recharge")
        select_channel = int(self.get_argument("select_channel"))
        mail_approve = int(self.get_argument("mail_approve"))
        operate_type = "|".join(json_decode(self.get_argument("operate_type")))
        email = self.get_argument("email")
        phone = self.get_argument("phone")
        data = UsersObject().operate_user(self.current_user, user_id, name, user_name, user_pass, user_type,
                                          user_game, upload_is, select_channel, is_start, is_recharge, mail_approve,
                                          operate_type, email, phone, self.real_ip)
        self.write(json.dumps(data, cls=CJsonEncoder))


class AjaxDeleteUserHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        user_id = self.get_argument("user_id")
        data = UsersObject().delete_user(user_id)
        self.write(json.dumps(data, cls=CJsonEncoder))

