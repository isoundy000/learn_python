#!/usr/bin/env python
# -*- coding:utf-8 -*-


class TimerTaskEscortNpc(object):

    def __init__(self, config_id, version):
        self.cur_config_id = config_id
        self.key = 'escort_npc_%s' % config_id
        self.config_id = config_id
        self.next_time = 0
        self.tglobal = 2
        self.repeat = 1
        self.version = version
        self.func = lambda x: x

