#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import threading
import signal
import time
import psutil

cur_path = os.path.abspath(os.path.dirname(__file__))

###############################################
# url: http://docs.gunicorn.org/en/latest/settings.html

# 测试环境不要开启timeout需要设置为0

# bind = '127.0.0.1:8001'
backlog = 2048

# workers = 2
worker_class = 'lib.core.gunicorn.ggtornado.GTornadoWorker'
# timeout = 30
# keepalive = 2

# pidfile = 'logs/gunicorn.pid'
preload_app = True

pythonpath = cur_path


###############################################

class ConfigWatch(threading.Thread):

    def __init__(self, server):
        super(ConfigWatch, self).__init__()
        self.daemon = True
        self.server = server
        self.loop_time = 5

    def run(self):
        import settings
        import game_config
        from logics.share import debug_sync_change_time

        while True:
            try:
                if self.server.pid != os.getpid():
                    break

                kill_worker = False

                if settings.DEBUG and debug_sync_change_time():
                    kill_worker = True

                if not game_config.is_config_out():
                    game_config.load_all()
                    kill_worker = True

                if kill_worker:
                    self.server.kill_workers(signal.SIGQUIT)

            except:
                pass

            time.sleep(self.loop_time)


# Server Hooks

# 启动程序执行
def nworkers_changed(server, new_value, old_value):
    """ workers数量改变是调用, 第一次old_value为None

    :param server:
    :param new_value:
    :param old_value:
    :return:
    """
    print 'nworkers_changed', server, new_value, old_value


def on_starting(server):
    """ 主进程启动之前调用
        1. 遇到端口被占用杀掉进程
        2. 改变时间
    :param server:
    :return:
    """
    print 'on_starting', server
    # 杀掉之前的进程
    laddr = server.cfg.address
    for addr in laddr:
        if addr:
            pids = get_pid_by_port(addr[1])
            for pid in pids:
                os.kill(pid, signal.SIGKILL)
    # 改变时间
    import settings
    from logics.share import debug_sync_change_time
    if settings.DEBUG:
        debug_sync_change_time()


def when_ready(server):
    """ 在服务器启动后调用

    :param server:
    :return:
    """
    print 'when_ready', server
    cw = ConfigWatch(server)
    cw.start()


def pre_fork(server, worker):
    """ fork出一个子进程之前调用

    :param server:
    :param worker:
    :return:
    """
    print 'pre_fork', server, worker


def post_fork(server, worker):
    """ 已经fork出一个子进程之后调用

    :param server:
    :param worker:
    :return:
    """
    print 'post_fork', server, worker


def post_worker_init(worker):
    """ 一个子进程初始化一个应用程序(服务)后调用

    :param worker:
    :return:
    """
    print 'post_worker_init', worker


# 关闭程序执行

def worker_int(worker):
    """ 一个子进程接受到SIGINT或者SIGQUIT信号退出后调用

    :param worker:
    :return:
    """
    print 'worker_int', worker


def worker_exit(server, worker):
    """ 一个子进程退出之后调用

    :param server:
    :param worker:
    :return:
    """
    print 'worker_exit', server, worker


def on_exit(server):
    """ 退出gunicorn之后调用

    :param server:
    :return:
    """
    print 'on_exit', server


def on_reload(server):
    print 'on_reload', server


def worker_abort(worker):
    """ 当一个进程接收到SIGABRT信号后调用

    :param worker:
    :return:
    """
    print 'worker_abort', worker


def pre_exec(server):
    """ 一个新的主进程fork出来前调用

    :param server:
    :return:
    """
    print 'pre_exec', server


def pre_request(worker, req):
    """ 请求一个子进程之前调用

    :param worker:
    :param req:
    :return:
    """
    print 'pre_request', worker, req


def post_request(worker, req, environ, resp):
    """ 请求一个子进程之后调用

    :param worker:
    :param req:
    :param environ:
    :param resp:
    :return:
    """
    print 'post_request', worker, req, environ, resp


def get_pid_by_port(port):
    """ 通过端口号获取进程号

    :param port:
    :return:
    """
    pid_list = []
    if cmp(psutil.version_info, (3, 3, 0)) >= 0:
        process_list = psutil.process_iter()
    else:
        process_list = psutil.get_process_list()

    for process in process_list:
        try:
            cons = process.connections()
        except:
            cons = []
        for con in cons:
            if con.laddr and con.laddr[1] == port:
                pid_list.append(process.pid)
    return pid_list