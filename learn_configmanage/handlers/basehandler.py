#!/usr/bin/env python
# -*- coding:utf-8 -*-

from tornado.web import RequestHandler


class BaseHandler(RequestHandler):

    def parse_param(self, **kwargs):
        param_dict = {}
        for x in kwargs:
            param_dict[x] = self.get_argument(x)
        return param_dict