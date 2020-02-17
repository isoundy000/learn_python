#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2020/1/18 23:55

from tornado.web import RequestHandler
from tornado.util import unicode_type


class BaseRequestHandler(RequestHandler):

    def summary_params(self):
        return self.request.arguments

    def real_params(self):
        '''
        真实的参数
        :return:
        '''
        return self.request.query

    def params(self, strip=True):
        data = {}
        query_source = self.request.query_arguments
        body_source = self.request.body_arguments
        for source in (query_source, body_source):
            for name, values in source.iteritems():
                vs = []
                for v in values:
                    v = self.decode_argument(v, name=name)
                    if isinstance(v, unicode_type):
                        v = RequestHandler._remove_control_chars_regex(" ", v)
                    if strip:
                        v = v.strip()
                    vs.append(v)
                data[name] = vs[-1]
        return data