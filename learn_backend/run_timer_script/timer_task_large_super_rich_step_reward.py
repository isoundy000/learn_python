#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import datetime
import importlib

import game_config


class TimerTaskLargeSuperRichStepReward(object):

    def __init__(self, config_id, version):
        self.key = 'large_super_rich_step_reward_%s' % config_id
        self.config_id = config_id
        self.next_time = 0
        self.tglobal = 2    # 自己用的类型
        self.repeat = 1
        self.version = version
        self.func = lambda x: x

    def parser(self):
        """ 解析时间

        :return:
        """
        if self.config_id not in game_config.large_super_rich_mapping:
            return
        rich_config = game_config.large_super_rich_mapping[self.config_id]
        _id = min(rich_config)
        config = rich_config.get(_id)

        module = importlib.import_module('logics.large_super_rich')
        if module:
            func = getattr(module, 'super_rich_step_reward')
            if func:
                self.func = func

        now = int(time.time())
        start_time = config['start_time']
        start_time = time.mktime(datetime.datetime.strptime(start_time, '%Y/%m/%d %H:%M:%S').timetuple())
        for step_id in [12, 21, 24]:
            run_time = start_time + step_id * 3600 + 1
            if now < run_time:
                self.next_time = run_time
                break

    def can_add(self, config_type, default_global_server, *args, **kwargs):
        if config_type != default_global_server:
            return False
        if not game_config.large_super_rich_mapping:
            return False
        if self.config_id not in game_config.large_super_rich_mapping:
            return False
        rich_config = game_config.large_super_rich_mapping[self.config_id]
        _id = min(rich_config)
        config = rich_config.get(_id)
        end_time = config['end_time']
        end_time_stamp = time.mktime(datetime.datetime.strptime(end_time, '%Y/%m/%d %H:%M:%S').timetuple()) + 2
        now = int(time.time())
        if end_time_stamp < now:
            return False
        return True

    def is_repeat(self):
        if not game_config.large_super_rich_mapping:
            return 0
        if self.config_id not in game_config.large_super_rich_mapping:
            return 0
        rich_config = game_config.large_super_rich_mapping[self.config_id]
        _id = min(rich_config)
        config = rich_config.get(_id)
        start_time = config['start_time']
        start_time_stamp = time.mktime(datetime.datetime.strptime(start_time, '%Y/%m/%d %H:%M:%S').timetuple())
        end_time = config['end_time']
        end_time_stamp = time.mktime(datetime.datetime.strptime(end_time, '%Y/%m/%d %H:%M:%S').timetuple())
        now = int(time.time())
        if start_time_stamp > now or end_time_stamp < now:
            return 0
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
