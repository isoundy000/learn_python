# -*-coding:utf-8-*-
__author__ = 'hougd'

import os.path

import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options

from tornado.options import define, options

define('port', default=1111, help='run on the given port', type=int)


# class Application(tornado.web.Application):
#
#     def __int__(self):
#         handlers = [
#             (r'/', HelloHandler),
#         ],
#
#         template_path=os.path.join(os.path.dirname(__file__), 'templates')
#         ui_modules = {'Hello': HelloModule}
#         super(Application, self).__init__(handlers=handlers, ui_modules=ui_modules, template_path=template_path)


class HelloHandler(tornado.web.RequestHandler):

    def get(self):
        self.render('hello.html')


class HelloModule(tornado.web.UIModule):

    def render(self):
        return '<h1>hello world 1111111!<h1>'


if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r'/', HelloHandler,)
        ],
        template_path=os.path.join(os.path.dirname(__file__), 'templates'),
        ui_modules={'Hello': HelloModule},
        debug=True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    # http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
