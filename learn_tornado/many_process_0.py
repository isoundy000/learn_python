#!/usr/bin/env python
# -*- coding:utf-8 -*-

# tornado 多线程服务器配置
import tornado.web
import tornado.ioloop
import tornado.options
import tornado.httpserver
import tornado.netutil
import tornado.process


from tornado.options import options, define

define("port", type=int, default=9000)


class IndexHandler(tornado.web.RequestHandler):

    def get(self, *args, **kwargs):
        self.write("<h1>hello world!</h1>")


urls = [
    (r"/", IndexHandler)
]

configs = dict(
    debug=True
)


class CustomApplication(tornado.web.Application):

    def __init__(self, configs, urls):
        settings = configs
        handlers = urls
        super(CustomApplication, self).__init__(handlers=handlers, **settings)



def create_app(n):
    tornado.options.parse_command_line()
    sockets = tornado.netutil.bind_sockets(options.port)
    tornado.process.fork_processes(n)
    http_server = tornado.httpserver.HTTPServer(CustomApplication(configs, urls))
    http_server.add_sockets(sockets)
    tornado.ioloop.IOLoop.instance().start()


app = create_app


if __name__ == '__main__':
    app(0)