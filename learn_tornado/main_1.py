# -*- coding:utf-8-*-
__author__ = 'hougd'

import os.path

import tornado.web
import tornado.httpserver
import tornado.options
import tornado.ioloop

from tornado.options import define, options

define('port', default=7777, help='run on the given port', type=int)


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.render('index_2.html', header_text="Header goes here", footer_text='Footer goes here')


if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[
        (r'/', MainHandler),
    ],
    template_path = os.path.join(os.path.dirname(__file__), 'templates'),
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
