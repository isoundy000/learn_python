#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import time
import datetime
from logics.gift import add_gift
from return_msg_config import i18n_msg

PAY_AWARD_MONTH_TITLE = unicode('月卡礼包', 'utf-8')
PAY_AWARD_MONTH_CONTENT = i18n_msg[1024]
PAY_AWARD_WEEK_TITLE = unicode('周卡礼包', 'utf-8')
PAY_AWARD_WEEK_CONTENT = i18n_msg[1025]



def auto_give_pay_award_week_and_month(user):
    """购买完月卡后每天自动发奖并邮件通知用户
    """
    today = time.strftime('%Y-%m-%d')
    pay_award = user.pay_award
    need_save = False

    # 周卡
    title = PAY_AWARD_WEEK_TITLE
    content = PAY_AWARD_WEEK_CONTENT
    model = pay_award.week
    if model['pay_dt'] and model['award_day'] != today:
        if model['days'] + 1 in model['reward']:
            need_save = True
            model['days'] += 1



    if need_save:
        pay_award.save()
        user.notify.save()