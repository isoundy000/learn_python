#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os

from tornado.wsgi import WSGIApplication
from tornado.options import options

# 解析tornado启动参数, 设置日志debug级别
options.parse_command_line(['', '--logging=debug'])

game_env = os.getenv('game_env')
server_name = os.getenv('server_name')
print 'game_env: %s, server_name: %s' % (game_env, server_name)

import settings
settings.set_evn(game_env, server_name)
settings.ENVPROCS = 'wsgi'

from handlers import APIRequestHandler
from handlers import ConfigHandler
from handlers import AdminHandler
from handlers import Login
from handlers import Pay, PayCallBack
from handlers import AdClick
from handlers import ZhiChong360Handler
from handlers import CMGEHandler
from handlers import AdvertHandler


class Application(WSGIApplication):

    def __init__(self):
        handlers = [
            (r"/pay/", Pay),
            (r"/pay-callback-([\w-]+)/?", PayCallBack),
            (r"/api/", APIRequestHandler),
            (r"/login/", Login),
            (r"/lr_version/", ConfigHandler),
            (r"/config/", ConfigHandler),
            (r"/admin/([\w-]+)/?", AdminHandler),
            (r"/genesis/admin/([\w-]+)/?", AdminHandler),  # 供本地开发
            (r"/ad-click-([\w-]+)/?", AdClick),  # 各种广告积分墙
            (r'/360/([\w-]+)/?', ZhiChong360Handler),  # 360支付游戏直冲接口
            (r'/cmge/([\w-]+)/?', CMGEHandler, dict(env_name=game_env)),  # 中手游需求提供接口
            (r'/appstore_advert/?', AdvertHandler),  # 针对IOS广告需求提供接口
        ]

        app_settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            debug=False,
        )

        super(Application, self).__init__(handlers, **app_settings)


app = Application()