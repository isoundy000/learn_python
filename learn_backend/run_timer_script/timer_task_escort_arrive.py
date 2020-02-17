#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time

import game_config
from logics.escort import Escort, LEscortVehicle
from models.timer import Timer


class TimerTaskEscortArrive(object):

    def __init__(self, config_id, version):
        self.cur_config_id = config_id
        self.key = 'escort_arrive_%s' % config_id
        self.config_id = config_id
        self.next_time = 0
        self.tglobal = 2
        self.repeat = 1
        self.version = version
        self.func = lambda x: x

    def parser(self):
        """ 解析时间"""

        self.func = LEscortVehicle.timer_arrive
        self.next_time = time.time() + 10

    def can_add(self, *args, **kwargs):
        """押镖活动期间可add"""

        if game_config.escort_opentime and self.config_id == 1:
            return True
        # config = game_config.escort_opentime.get(self.config_id, {})
        # if config:
        #     s_time = Escort.get_stamp(config['start_time'])
        #     e_time = Escort.get_stamp(config['end_time'])
        #     now_time = time.time()
        #     if s_time <= now_time <= e_time:
        #         return True

        return False


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