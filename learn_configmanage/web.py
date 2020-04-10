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
from handlers import basehandler
from handlers import datahandlers
from handlers.gameserverhandler import notice_agent


from logic.broadcast import PushBroadcast2
from common.dbhelper import DBHelperObject
import uuid
from handlers import configfilehandler
from handlers import account_handler
from handlers.interface.config_data import GetWebInfo


define("port", default=9696, type=int)
define("identity", default=0, type=int)     # 同名、一致性


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            # 接口
            (r"/get/web_info", GetWebInfo),                             # 获取网站信息
            # Default
            (r"/", forwardhandlers.IndexHandler),                       # 主页页面
            (r"/login", forwardhandlers.LoginHandler),                  # 登录页面
            (r"/updatepass", datahandlers.UpdatePassHandler),           # 更新密码
            (r"/exit", forwardhandlers.ExitHandler),                    # 退出页面
            # 管理系统 Route
            (r"/server", forwardhandlers.ServerHandler),                # 管理系统

            # 统计系统
            (r"/trend", forwardhandlers.TrendHandler),                  # 统计系统

            # 策划系统
            (r"/config/configfile", configfilehandler.ConfigFileHandler),   # 策划系统


            # 运维系统
            (r"/allgame_b/total", forwardhandlers.AllGameBTotalHandler),    # 运维系统

            # 运营系统 Route
            (r"/broadcast", forwardhandlers.BroadcastHandler),          # 运营系统 Route

            # AJax Route
            (r"/validate", datahandlers.AjaxValidateHandler),           # 验证
            (r"/getalluser", datahandlers.AjaxGetAllUserHandler),       # 获取所有用户
            # (r"/getotheruser", datahandlers.AjaxGetOtherUserHandler),
            (r"/operateuser", datahandlers.AjaxOperateUserHandler),     # 更新或添加用户
            (r"/deleteuser", datahandlers.AjaxDeleteUserHandler),       # 删除用户
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