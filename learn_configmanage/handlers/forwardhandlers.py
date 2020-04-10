#!/usr/bin/env python
# -*- coding:utf-8 -*-

from tornado.web import RequestHandler
from basehandler import BaseHandler
import tornado
from logic.systemlog import SystemLogObject


def forward(handler, user_role, str_html, **kwargs):
    '''
    获取角色有得权限
    :param handler: 拦截器
    :param user_role: 用户角色 user_role2
    :param str_html: configfile2.html
    :param kwargs:
    :return:
    '''
    user_r = handler.get_cookie(user_role)
    if user_r == "1":
        handler.render(str_html, user_role=user_role, **kwargs)
    else:
        handler.redirect("/login")


class ServerHandler(BaseHandler):
    """
    管理系统
    """
    @tornado.web.authenticated
    def get(self):
        forward(self, "user_role1", "server.html")


class TrendHandler(BaseHandler):
    """
    统计首页
    """
    @tornado.web.authenticated
    def get(self):
        forward(self, "user_role3", "trend.html")


class AllGameBTotalHandler(BaseHandler):
    '''
    运维系统
    '''
    @tornado.web.authenticated
    def get(self):
        self.render("allgame_b_total.html", user_role='user_role4')


class BroadcastHandler(BaseHandler):
    '''
    运营系统
    '''
    @tornado.web.authenticated
    def get(self):
        forward(self, "user_role5", "broadcast.html")


class IndexHandler(BaseHandler):
    """
    主页页面
    """
    @tornado.web.authenticated
    def get(self):
        self.render("index.html")


class LoginHandler(RequestHandler):
    """
    登录页面
    """
    def get(self):
        self.render("login.html")


class ExitHandler(BaseHandler):
    """
    退出页面
    """
    def get(self):
        SystemLogObject().insert_log(self.current_user, 2, u"退出系统", self.real_ip)
        self.clear_all_cookies()
        self.redirect("/login")