#!/usr/bin/python
# encoding: utf-8

__author__ = 'hougd'

import time
import datetime
import importlib

import game_config


class TimerTaskTeamPkNewGiftAndScore(object):
    def __init__(self, config_id, version):
        self.cur_config_id = config_id
        self.key = 'team_pk_new_gift_and_score_%s' % min(game_config.server_pk_time) if game_config.server_pk_time else 0
        self.config_id = min(game_config.server_pk_time) if game_config.server_pk_time else 0
        self.next_time = 0
        self.tglobal = 2
        self.repeat = 1
        self.version = version
        self.func = lambda x: x

    def parser(self):
        """ 解析时间
        :return:
        """
        config = game_config.server_pk_time[self.config_id]
        module = importlib.import_module('logics.team_pk_new')
        if module:
            func = getattr(module, 'gift_and_score_new')
            if func:
                self.func = func

        date = datetime.datetime.now()

        close = config['reward_time']

        func_date = None

        for week in config['time_sort']:
            func_week = week - 1
            diff_day = date.weekday() - func_week
            if diff_day < 0:
                func_date = date.date() - datetime.timedelta(days=diff_day)
                break
            elif diff_day == 0 and date.strftime("%H:%M") < close:
                func_date = date.date()
                break

        if func_date is None:
            week = config['time_sort'][0]
            func_date = date.date() + datetime.timedelta(days=7 - (date.weekday() - (week - 1)))

        func_time_str = '%s %s' % (func_date.strftime('%Y-%m-%d'), close)
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