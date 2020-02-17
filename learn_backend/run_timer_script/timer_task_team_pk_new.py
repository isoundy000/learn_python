#!/usr/bin/python
# encoding: utf-8

__author__ = 'hougd'

import time
import datetime
import importlib

import game_config


class TimerTaskTeamPkNew(object):
    def __init__(self, config_id, version):
        self.cur_config_id = config_id
        self.key = 'team_pk_new_%s' % min(game_config.server_pk_time) if game_config.server_pk_time else 0
        self.config_id = min(game_config.server_pk_time) if game_config.server_pk_time else 0
        self.next_time = 0
        self.tglobal = 2
        self.repeat = 1
        self.version = version
        self.func = lambda x: x

    def parser(self):
        """
        解析时间
        :return:
        """
        config = game_config.server_pk_time.get(self.config_id)
        module = importlib.import_module('logics.team_pk_new')
        if module:
            func = getattr(module, 'team_pk_new')
            if func:
                self.func = func

        now = int(time.time())
        date = datetime.datetime.now()
        pk_close_time = config['pk_close_time']

        open_time = config['open_time']  # '21:40', '21: 42', '21:38'
        cur_time_str = date.date().strftime('%Y-%m-%d')
        next_time_str = '%s %s' % (cur_time_str, open_time)
        start_run_time = time.mktime(datetime.datetime.strptime(next_time_str, '%Y-%m-%d %H:%M').timetuple())

        func_date = None

        for week in config['time_sort']:
            func_week = week - 1
            diff_day = date.weekday() - func_week
            if diff_day < 0:
                func_date = date.date() - datetime.timedelta(days=diff_day)
                break
            elif diff_day == 0 and date.strftime("%H:%M") < pk_close_time:
                func_date = date.date()
                break

        if func_date is None:
            week = config['time_sort'][0]
            func_date = date.date() + datetime.timedelta(days=7 - (date.weekday() - (week - 1)))

        func_time_str = None

        # if func_time_str.strftime('%Y-%m-%d') != cur_time_str:
        #     func_time_str = '%s %s' % (func_date.strftime('%Y-%m-%d'), datetime.datetime.fromtimestamp(start_run_time).strftime('%H:%M'))
        # else:
        for i in range(0, 20, 2):
            run_time = start_run_time + 60 * i + 30
            if now < run_time:
                func_time_str = '%s %s' % (func_date.strftime('%Y-%m-%d'), datetime.datetime.fromtimestamp(run_time).strftime('%H:%M'))
                break
            else:
                continue

        if func_time_str is None:
            func_time_str = '%s %s' % (func_date.strftime('%Y-%m-%d'), datetime.datetime.fromtimestamp(start_run_time).strftime('%H:%M'))

        func_time = time.mktime(time.strptime(func_time_str, '%Y-%m-%d %H:%M'))
        self.next_time = func_time

    def can_add(self, config_type, default_global_server, *args, **kwargs):
        if config_type != default_global_server:
            return False
        if not game_config.server_pk_time:
            return False
        return self.config_id == self.cur_config_id

    def is_repeat(self):
        return self.repeat

    def is_global(self):
        return self.tglobal

    def get_key(self):
        return self.key

    def get_func(self):
        return self.func

    def get_next_time(self):
        return self.next_time

    def set_next_time(self, next_time):
        self.next_time = next_time

    def get_version(self, *args, **kwargs):
        return self.version

    def set_version(self, version):
        self.version = version

    def get_config_id(self):
        return self.config_id