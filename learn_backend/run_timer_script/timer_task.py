#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time

from lib.utils import time_tools


class TimerTask(object):

    def __init__(self, key, config_tuple):
        """ config_tuple (差距多少月, 差距多少天, 当天的几点，几分，几秒, func, is_repeat, global所有服不分区)
        """
        self.key = key
        self.diff_month = config_tuple[0]
        self.diff_day = config_tuple[1]
        self.hour = config_tuple[2]
        self.minute = config_tuple[3]
        self.second = config_tuple[4]
        self.func = config_tuple[5]
        self.repeat = config_tuple[6]
        self.tglobal = config_tuple[7]
        self.parser()

    def parser(self):
        datetime_now = time_tools.datetime_now()
        if self.diff_month:
            timestamp = time_tools.timestamp_from_deltamonthtime(datetime_now, self.diff_month, self.diff_day, self.hour, self.minute, self.second)
        else:
            timestamp = time_tools.timestamp_from_deltadaytime(datetime_now, self.diff_day, self.hour, self.minute, self.second)

            if self.diff_day == 0 and time.time() > timestamp:
                timestamp = time_tools.timestamp_from_deltadaytime(datetime_now, 1, self.hour, self.minute, self.second)

        self.next_time = timestamp

    def can_add(self, config_type, default_global_server, *args, **kwargs):
        return not self.is_global() or (self.is_global() and config_type == default_global_server)

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
        return 0

    def set_version(self, version):
        pass

    def get_config_id(self):
        return 0