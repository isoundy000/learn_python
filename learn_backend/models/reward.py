#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import time
import game_config
import settings
from lib.db import ModelBase
from lib import utils


class Reward(ModelBase):

    def __init__(self, uid):
        """初始化
        """
        self._attrs = {
            'date': '',
            'gift_data': {},                # 今日登录时间数据

        }
        super(Reward, self).__init__(uid)

    def update_gift_task(self, save=True):
        """
        记录奖励任务
        :param save:
        :return:
        """
        timestamp = int(time.time())
        today_str = time.strftime('%Y-%m-%d')

        def to_timestamp(timestr):
            temp = time.strptime(today_str, timestr, '%Y-%m-%d %H:%M')
            return time.mktime(temp)

        for gift_id, config in game_config.reward_gift.iteritems():
            stime, etime = map(to_timestamp, config['time'].split('-'))

            if stime <= timestamp <= etime:
                self.gift_data = {gift_id: timestamp}
                save = True
                break

        if save:
            self.save()