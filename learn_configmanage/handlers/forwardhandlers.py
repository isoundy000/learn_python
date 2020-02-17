#!/usr/bin/env python
# -*- coding:utf-8 -*-

from tornado.web import RequestHandler
from basehandler import BaseHandler
import tornado
from logic.systemlog import SystemLogObject



class IndexHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        self.render("index.html")


class LoginHandler(RequestHandler):

    def get(self):
        self.render("login.html")