# coding: utf-8

import logging

import socket

from tornado.httpserver import HTTPServer
from tornado import ioloop
from tornado import web
from tornado.options import define, options
from tornado import autoreload
import tornado

define("port", default=8888, help="run on the given port", type=int)
define("env", default='dev_new', help='the env', type=str)
define("server_name", default='1', help='the server name', type=str)
define("numprocs", default=2, help="process sum", type=int)
define("debug", default=False, help="run at debug mode", type=bool)
define("maxmem", default=0, help="max memory use, overflow kill by self. (0 unlimit)", type=int)

options.parse_command_line()
import settings

settings.set_evn(options.env, options.server_name)
settings.ENVPROCS = 'run'

from handlers import APIRequestHandler
from handlers import ConfigHandler
from handlers import AdminHandler
from handlers import Login
from handlers import Pay, PayCallBack
from handlers import AdClick
from handlers import ZhiChong360Handler
from handlers import CMGEHandler
from handlers import AdvertHandler

from lib.utils.debug import print_log


import os
import sys
import gc
import time
import psutil
import signal
# import resource

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))


class Application(web.Application):

    def __init__(self, debug=False):
        handlers = [
            (r"/pay/", Pay),
            (r"/pay-callback-([\w-]+)/?", PayCallBack),
            (r"/api/", APIRequestHandler),
            (r"/login/", Login),
            (r"/config/", ConfigHandler),
            # (r"/chat/", ChatRequestHandler),
            (r"/admin/([\w-]+)/?", AdminHandler),
            (r"/genesis/admin/([\w-]+)/?", AdminHandler),                             # 供本地开发
            (r"/ad-click-([\w-]+)/?", AdClick),                                 # 各种广告积分墙
            (r'/360/([\w-]+)/?', ZhiChong360Handler),                           # 360支付游戏直冲接口
            (r'/cmge/([\w-]+)/?', CMGEHandler, dict(env_name=options.env)),     # 中手游需求提供接口
            (r"/appstore_advert/?", AdvertHandler),
        ]

        app_settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            debug=False
        )

        super(Application, self).__init__(handlers, **app_settings)


import pdb


def db(sig, frame):
    """# db: docstring
    args:
        sig, frame:    ---    arg
    returns:
        0    ---
    """
    pdb.set_trace()


CHILDREN = {}

def shutdown():
    logging.warning('Stopping http server')
    server.stop()

    logging.warning('Will shutdown in %s seconds ...', 1)
    io_loop = tornado.ioloop.IOLoop.instance()

    deadline = time.time() + 1

    def stop_loop():
        now = time.time()
        if now < deadline and (io_loop._callbacks or io_loop._timeouts):
            io_loop.add_timeout(now, stop_loop)
        else:
            io_loop.stop()
            logging.info('Shutdown')
    stop_loop()

def sig_hander_parent(sig, frame):
    print 'sig', sig
    for task_id, pid in CHILDREN.iteritems():
        kill_child(task_id)
    sys.exit()

def sig_hander_child(sig, frame):
    logging.warning('Caught signal: %s', sig)   # wait request end
    tornado.ioloop.IOLoop.instance().add_callback(shutdown)
    #sys.exit()
    os._exit(0)

def kill_child(task_id):
    pid = CHILDREN[task_id]
    print_log(options.server_name, ':', task_id, ':', pid, 'ending....')
    os.kill(pid, signal.SIGTERM)
    #os.waitpid(pid, 0)
    CHILDREN[task_id] = None

def start_child(task_id):
    pid = os.fork()
    if pid: # parent proces
        # 父进程则会将子进程pid与子进程对应的i值进行映射，然后返回父进程的pid
        CHILDREN[task_id] = pid
        return pid
    # child process
    signal.signal(signal.SIGTERM, sig_hander_child)     # pid==0 表示子进程
    signal.signal(signal.SIGINT, sig_hander_child)
    print_log(options.server_name, ':', task_id, ':', os.getpid(), 'started')
    return pid

def restart_child(task_id):
    kill_child(task_id)
    return start_child(task_id)

def mem_watcher(process):
    mem_size = process.get_memory_info().rss
    timestamp = int(time.time()) + 10

    if mem_size > options.maxmem:
        # logging.info(str(gc.get_objects()))
        logging.info('------mem_watcher--------:real: %s M -- limit: %s M, server restart' % (mem_size / 1024 / 1024, options.maxmem / 1024 / 1024))
        # TODO: 内存监控
        # os.kill(os.getpid(), signal.SIGTERM)


def main():
    app = Application()

    import game_config
    print_log(os.getpid(), os.getppid(), options.port)
    try:
        sockets = tornado.netutil.bind_sockets(options.port)
    except socket.error, e:
        os.system('''for i in `ps aux | grep -v 'grep' | grep 'python' | grep 'run.py' | grep 'port=%d' | awk '{if($2!=%d){print $2}}'`;do kill -9 $i;done'''%(options.port, os.getpid()))
        sockets = tornado.netutil.bind_sockets(options.port)
        print_log('killed orphan process')
    parent = True
    # print os.getpid()
    global CHILDREN
    process_sum = options.numprocs
    i = 1
    for i in xrange(1, process_sum+1):
        pid = start_child(i)
        if pid == 0:
            parent = False
            break
    if parent and process_sum:
        signal.signal(signal.SIGTERM, sig_hander_parent)
        signal.signal(signal.SIGINT, sig_hander_parent)
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)   # let init clear zombie child
        # print CHILDREN
        while 1:
            time.sleep(5)
            print CHILDREN
            if not game_config.is_config_out():
                print_log('config out')
                game_config.load_all()
                for task_id in CHILDREN.iterkeys():
                    print_log('config out, restart '+str(task_id))
                    if not restart_child(task_id):
                        parent = False
                        break
            if not parent:
                break
            for task_id, pid in CHILDREN.iteritems():   # if child is alive
                try:
                    child_process = psutil.Process(pid)
                    if not child_process.is_running() or os.getpid() != child_process.ppid():
                        print_log('NO this child, ', task_id, pid, child_process.is_running(), child_process.pid, os.getpid(), child_process.ppid())
                        raise psutil.NoSuchProcess(pid)
                    #mem_watcher(child_process)
                except psutil.NoSuchProcess, e:
                    if not start_child(task_id):    # start child
                        parent = False
                        break
            if not parent:
                break

    from logics.share import debug_sync_change_time
    # 注意, 正式环境禁止启动此函数
    if settings.DEBUG:
        # 重启先加载时间
        debug_sync_change_time()
        # 每10秒钟加载时间
        tornado.ioloop.PeriodicCallback(debug_sync_change_time, 10 * 1000).start()

    if settings.DEBUG and not process_sum:
        def check_config():
            if not game_config.is_config_out():
                print_log('config out')
                game_config.load_all()
        # 每5秒钟加载配置
        tornado.ioloop.PeriodicCallback(check_config, 5*1000).start()

    print 'start, ', options.port+i, os.getpid(), os.getppid()
    server = HTTPServer(app, xheaders=True)
    server.add_sockets(sockets)
    loop = ioloop.IOLoop.instance()
    loop.start()


if __name__ == '__main__':
    main()