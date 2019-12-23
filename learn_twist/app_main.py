#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/11/22 15:34
# @version: 0.0.1
# @Author: houguangdong
# @File: app_main.py
# @Software: PyCharm

import sys
import json
import code
import signal
import threading
import traceback
from learn_twist.server.server import FFServer


def dump_stacks(signal, frame):
    id2name = dict([(th.ident, th.name) for th in threading.enumerate()])
    codes = []
    for threadId, stack in sys._current_frames().items():
        codes.append("\n# Thread: %s(%d)" % (id2name.get(threadId, ""), threadId))
        for filename, lineno, name, line in traceback.extract_stack(stack):
            codes.append('File: "%s", line %d, in %s' % (filename, lineno, name))
            if line:
                codes.append("  %s" % (line.strip()))


def print_stack(signal, frame):
    d = {'_frame': frame}  # Allow access to frame object.
    d.update(frame.f_globals)  # Unless shadowed by global
    d.update(frame.f_locals)

    i = code.InteractiveConsole(d)
    message = "Signal received : entering python shell.\nTraceback:\n"
    message += ''.join(traceback.format_stack(frame))
    i.interact(message)


if __name__ == "__main__":

    signal.signal(signal.SIGUSR1, print_stack)
    signal.signal(signal.SIGUSR2, dump_stacks)

    args = sys.argv

    if len(args) <= 2:
        raise ValueError

    server_name = args[1]

    with open(args[2], 'r') as f:
        config = json.loads(f.read())

    servers_conf = config.get('servers', {})
    master_conf = config.get('master', {})

    # model_default_config = config.get('model_default', {})
    # model_config = config.get('models', {})


    server_config = servers_conf.get(server_name)
    ser = FFServer()
    ser.config(server_config, server_name=server_name, master_conf=master_conf)
    ser.start()