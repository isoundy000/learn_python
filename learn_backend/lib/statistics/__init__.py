#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import copy
import time

import settings

PID = os.getpid()

path = settings.BASE_ROOT + 'logs/action/'

os.system("""[ ! -d '%s' ] && mkdir -p %s""" % (path, path))

FILE_NAME_PRE = path + '_'.join([
    settings.URL_PARTITION,
    settings.SERVICE_NAME,
    str(PID)
])

BATTLE_METHODS = [

]

FORMAT = [
    'uid',
    'pre_vip',
    'pre_level',

    'post_vip',
    'post_level'
]

import logger_funcs
import logger_action_funcs


def logger(env, args, data):
    from models.logging import Logging
    method = env.get_argument('method')
    if method:
        func_name = '_'.join(method.split('.'))
        func = getattr(logger_funcs, func_name, None)
        if callable(func):
            result = func(env, args, data)
            Logging(env.user).add_logging(method, args, result or data)



def stat(func, action_keyword=None):
    """# stat: 记录行为
    """
    if action_keyword is None:
        action_keyword = ''
    else:
        action_keyword = action_keyword + '.'

    def new_func(self, *args, **kwargs):
        """# new_func: docstring
        timestamp, url_partition, server, uid, vip, level, exp, silver, coin, action, rc, args, user_status

        """
        has_env = getattr(self, 'env', None)

        if has_env:
            arguments = copy.deepcopy(self.env.req.summary_params())
            user = self.env.user
        else:
            arguments = copy.deepcopy(self.summary_params())
            user = None

        method = action_keyword + arguments['method'][0]

        ignore_arg_name = ['method', 'user_token', 'mk', 'kgg_cjxy', 'ks']

        for arg_name in ignore_arg_name:
            if arg_name in arguments:
                del arguments[arg_name]

        one_log_list = {
            'timestamp': time.time(),
            'url_partition': settings.URL_PARTITION,
            'server': settings.SERVICE_NAME,
            'action': method,
            'args': arguments,
            'datetime': time.strftime('%F %T'),     # 格式样例： 2015-01-31 01:02:03
        }

        if user is not None:
            one_log_list.update({
                'uid': 'h11234567',
                'pre_vip': 0,
                'pre_level': 0,
            })

        rc, data, msg, user = func(self, *args, **kwargs)
        one_log_list.update({
            'rc': rc,
            'result': {},
        })

        if rc == 0:
            func_name = '_'.join(method.split('.'))
            action_func = getattr(logger_action_funcs, func_name, None)
            if action_func and callable(action_func):
                one_log_list['result'] = action_func(data)

        if user is not None:
            one_log_list.update({
                'post_vip': 0,
                'post_level': 0,
            })

        # 应BI王士宝要求，将战斗类请求的返回Data放入行为日志arg参数里里， 2015-11-30 17:55
        if rc == 0 and has_env:
            method = self.env.get_argument('method')
            if method in BATTLE_METHODS:
                arguments['is_win'] = data.get('is_win', "unknown")

        with open(FILE_NAME_PRE + '_' + time.strftime('%Y%m%d'), 'aw') as f:
            f.write('\t'.join([str(one_log_list.get(i, -10240)) for i in FORMAT]) + '\n')

        if rc == 0 and has_env:
            logger(self.env, arguments, data)

        return rc, data, msg, user

    return new_func