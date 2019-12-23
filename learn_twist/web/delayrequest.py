#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/11/21 23:42
# @version: 0.0.1
# @Author: houguangdong
# @File: delayrequest.py
# @Software: PyCharm

from klein.resource import KleinResource
from twisted.python.compat import nativeString, intToBytes
from twisted.web import util
from twisted.web.server import Request, Site
from twisted.internet import defer
from twisted.web import http, html
from twisted.python import log, reflect
from twisted.web import resource
from twisted.web.error import UnsupportedMethod
from twisted.web.microdom import escape

NOT_DONE_YET = 1
date_time_string = http.datetimeToLogString
string_date_time = http.stringToDatetime

# Support for other methods may be implemented on a per-resource basis.
supportedMethods = (b'GET', b'HEAD', b'POST')


class DelayRequest(Request):

    def __init__(self, args, **kw):
        Request.__init__(self, *args, **kw)
        self.transmit_parameter = {}

    def set_transmit_parameter(self):
        """
        设置需要传输的参数
        :return:
        """
        self.bytes_to_str()
        self.transmit_parameter = {
            "path": self.path, "parameter": self.parameter, "cookies": self.received_cookies,
            "client_ip": self.getClientIP()
        }

    def bytes_to_str(self):
        '''
        二进制转字符串
        :return:
        '''
        self.path = self.path.decode("utf-8")
        str_cookie = {}
        for cookie_key, cookie_val in self.received_cookies.items():
            str_cookie[cookie_key.decode("utf-8")] = cookie_val.decode('utf-8')     # 从字节变成u''字符串
        self.received_cookies = str_cookie
        return

    def render(self, resrc):
        """
        Ask a resource to render itself.
        @type resrc: KleinResource
        @param resrc: a L{twisted.web.resource.IResource}.
        :param resrc:
        :return:
        """
        self.set_transmit_parameter()
        try:
            body = resrc.render(self)
        except UnsupportedMethod as e:
            allowed_methods = e.allowedMethods
            if (self.method == b"HEAD") and (b"GET" in allowed_methods):
                # We must support HEAD (RFC 2616, 5.1.1).  If the
                # resource doesn't, fake it by giving the resource
                # a 'GET' request and then return only the headers,
                # not the body.
                log.msg("Using GET to fake a HEAD request for %s" % (resrc,))
                self.method = b"GET"
                self._inFakeHead = True
                body = resrc.render(self)

                if body is NOT_DONE_YET:
                    log.msg("Tried to fake a HEAD request for %s, but "
                            "it got away from me." % resrc)
                    # Oh well, I guess we won't include the content length.
                else:
                    self.setHeader(b"content-length", intToBytes(len(body)))

                self._inFakeHead = False
                self.method = b"HEAD"
                self.write(b'')
                self.finished()
                return

            if self.method in supportedMethods:
                # We MUST include an Allow header
                # (RFC 2616, 10.4.6 and 14.7)
                self.setHeader(b'Allow', b', '.join(allowed_methods))
                s = (
                    '''Your browser approached me (at %(URI)s) with'''
                    ''' the method "%(method)s".  I only allow'''
                    ''' the method%(plural)s %(allowed)s here.''' % {
                        'URI': escape(nativeString(self.uri)),
                        'method': nativeString(self.method),
                        'plural': ((len(allowed_methods) > 1) and 's') or '',  # ((len(allowed_methods) > 1) and 's') <--> 's' or ''
                        'allowed': ', '.join(nativeString(x) for x in allowed_methods)
                    }
                )

                epage = resource.ErrorPage(http.NOT_ALLOWED,
                                            "Method Not Allowed", s)
                body = epage.render(self)
            else:
                epage = resource.ErrorPage(
                            http.NOT_IMPLEMENTED, "Huh?",
                            "I don't know how to treat a %s request." %
                            (escape(self.method.decode("charmap")), )
                        )
                body = epage.render(self)

        # end except UnsupportedMethod

        if body == NOT_DONE_YET:
            return
        if not isinstance(body, bytes):
            body = resource.ErrorPage(
                http.INTERNAL_SERVER_ERROR,
                "Request did not return bytes",
                "Request: " + util._PRE(reflect.safe_repr(self)) + "<br />" +
                "Resource: " + util._PRE(reflect.safe_repr(resrc)) + "<br />" +
                "Value: " + util._PRE(reflect.safe_repr(body))
            ).render(self)

        if self.method == b"HEAD":
            if len(body) > 0:
                # This is a Bad Thing (RFC 2616, 9.4)
                log.msg("Warning: HEAD request %s for resource %s is"
                        " returning a message body."
                        " I think I'll eat it."
                        % (self, resrc))
                self.setHeader('content-length', str(len(body)))
            self.write(b'')
            self.finished()
        else:
            if isinstance(body, defer.Deferred):
                body.addCallback(self._defer_write)
            else:
                self.setHeader(b'content_length', str(len(body)))
                self.write(body)
                self.finished()

    @property
    def parameter(self):
        kwargs = {}
        for key, val in self.args.items():
            val = val[0].decode("utf-8")
            kwargs[key.decode("utf-8")] = val
        return kwargs

    def _defer_write(self, body):
        """延迟等待数据返回
        :param body:
        :return:
        """
        self.setHeader('content-length', str(len(body)))
        self.write(body)
        self.finished()


class DelaySite(Site):

    def __init__(self, delay_site_resource, log_path=None, timeout=60 * 60 * 12):
        Site.__init__(self, delay_site_resource, logPath=log_path, timeout=timeout)
        self.requestFactory = DelayRequest