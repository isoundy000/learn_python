#!/usr/bin/env python
# -*- coding:utf-8 -*-

from tornado.web import RequestHandler
from tornado.web import ErrorHandler
from common.dbhelper import DBHelperObject
from tornado.escape import json_decode
import logging


ip_list = [
    # "36.110.89.59",
    "127.0.0.1"
]


user_list = [
    # "administrator_muyou",
    "administrator_debang",
    "houguangdong"
]


class BaseHandler(RequestHandler):

    def parse_param(self, **kwargs):
        '''
        解析请求参数
        :param kwargs:
        :return:
        '''
        param_dict = {}
        for x in kwargs:
            param_dict[x] = self.get_argument(x)
        return param_dict

    def isexit_username(self, user_name):
        '''
        是否存在此用户
        :param user_name: 用户名
        :return:
        '''
        query_sql = "SELECT id, username FROM t_users WHERE username='%s'" % user_name
        self.user_data = DBHelperObject.CONFIG_CON.get(query_sql)

    def get_current_user(self):
        '''
        获取当前current_user
        :return:
        '''
        user = self.get_cookie("user_session")          # 用户名
        if user == 'mosisi':
            return None
        self.real_ip = '0.0.0.0'
        if 'X-Real-Ip' in self.request.headers:
            self.real_ip = self.request.headers['X-Real-Ip']

        self.isexit_username(user)      # 是否存在此用户

        if not user or self.user_data is None:
            return None

        return user

    def get(self):
        self.write_error(404)

    def write_error(self, status_code, **kwargs):
        '''
        写回错误
        :param status_code:
        :param kwargs:
        :return:
        '''
        if status_code == 404:
            self.render("error.html", status_code=status_code)
        else:
            RequestHandler.write_error(self, status_code, **kwargs)