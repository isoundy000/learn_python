#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
import hashlib
from tornado.options import define, options

from common.global_variable import GlobalVal
GlobalVal.set_value()
from common.configmanager import ConfigManager
from handlers import forwardhandlers
from handlers.gameserverhandler import notice_agent


from logic.broadcast import PushBroadcast2
from common.dbhelper import DBHelperObject
import uuid
from handlers import account_handler


define("port", default=9696, type=int)
define("identity", default=0, type=int)     # 同名、一致性


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            # 接口
            # Default
            (r"/", forwardhandlers.IndexHandler),
            (r"/login", forwardhandlers.LoginHandler),
            (r"/validate", datahandlers.AjaxValidateHandler),
        ]

        key = ConfigManager.getvalue("GAME_DATA", "config_path")
        cookie_secret = hashlib.md5(key).hexdigest()
        settings = dict(
            login_url="/login",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            cookie_secret=uuid.uuid4(),
            xsrf_cookies=False,
            debug=True
        )
        tornado.web.Application.__init__(self, handlers, **settings)


def main():
    http_server = Application()
    print "Starting server on port %d....." % options.port
    # http_server.listen(options.port, address='127.0.0.1', xheaders=True)
    http_server.listen(options.port, xheaders=True)
    s_time = 5 * 60 * 1000
    if options.identity == 1:
        tornado.ioloop.PeriodicCallback(PushBroadcast2, s_time).start()
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    tornado.options.parse_command_line()
    ConfigManager.create("config.ini")
    DBHelperObject.init_connection()
    if options.identity == 1:
        account_handler.notice_acc_agent()
        notice_agent()

    main()