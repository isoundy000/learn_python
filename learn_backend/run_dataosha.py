#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import json

import gevent
import gevent.monkey

gevent.monkey.patch_all()

from gevent.wsgi import WSGIServer


from lib.utils.debug import print_log

import settings

settings.set_evn('dev_new', 1)      # set_evn('dev', 'h1')

import handler_tools

from views import gvg


def get_user(uid):
    """# get_user: docstring
    args:
        uid:    ---    arg
    returns:
        0    ---
    """
    import game_config
    if not game_config.is_config_out():
        game_config.load_all()

    from logics.user import User
    user = User(uid)

    setattr(user, 'game_config_version', game_config.config_version)

    return user


def app(env, start_response):
    """# app: docstring
    args:
        env, start_response:    ---    arg
    returns:
        0    ---
    """
    print env['PATH_INFO']
    print 'time', time.time()
    query_string = env['QUERY_STRING']
    params = dict([i.split('=') for i in query_string.strip('&').split('&')])
    user_id = params.get('user_token')
    user = get_user(user_id)

    method_name = params.get('method')
    method = getattr(gvg, method_name)
    start_response('200 OK', [('Content-Type', 'application/javascript; charset=UTF-8')])
    if callable(method):
        rc, data = method(user, params)
        # 行动点数倒数
        if user.action_point >= user.action_point_max:
            action_point_update_left = 0
        else:
            action_point_update_left = int(user.ACTION_POINT_UPDATE_RATE - time.time() + user.action_point_updatetime)

        import game_config
        msg = ''
        r = handler_tools.result_generator(rc, data, msg, user)
        return [r.encode('utf-8')]

if __name__ == '__main__':
    print 'Serving on 10023'
    wsgi_server = WSGIServer(('', 10023), app)
    wsgi_server.serve_forever()