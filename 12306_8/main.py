# coding:utf-8
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from handler import BaseHandler, IndexHandler
from tasks.utils.config import web_port


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [(r'/', IndexHandler),
                    (r'/(?P<api_name>.+)', BaseHandler)]
        settings = {'debug': True}
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == '__main__':

    app = Application()

    tornado.options.define('port', default=7890, type=int)
    # tornado.options.options.logging = None # 关闭输出
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
    http_server.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.current().start()