#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import game_config
from logics.gift import add_gift


class Daily_award(object):
    """
    每日签到领奖逻辑
    """
    def __init__(self, user):
        """
        daily_award init
        """
        self.user = user

    def get_all(self):
        """获取每日签到数据
        Returns:
            签到天数，签到奖励ID列表
        """
        if self.user.daily_award.can_daily_award_loop():
            pass

