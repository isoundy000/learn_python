#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'ghou'

import time
import datetime


def dict_diff(old, new):
    """# dict_diff: 比较两个字典
    args:
        old, new:    ---    arg
    returns:
        0    ---
    """
    old_keys = set(old.keys())
    new_keys = set(new.keys())

    remove_keys = old_keys - new_keys       # 要被删除的key
    add_keys = new_keys - old_keys          # 要添加的key
    same_keys = new_keys & old_keys         # 新旧共同拥有的key，这个是用来准备做比较修改

    update = {}

    for k in same_keys:
        new_data = new[k]
        if old[k] != new_data:
            update[k] = new_data

    for k in add_keys:
        update[k] = new[k]

    return update, remove_keys


def round_float_or_str(score):
    """
    数据向上取整
    :param num: 需要转换的数据(float|str)
    :return:
    """
    return round(float(score))


def generate_rank_score(num, now=None):
    """
    生成排名的积分
    :param num: 需要转换的场数
    :param now: 当前的时间搓
    :return:
    """
    now = now if now else time.time()
    return num - now / 10 ** 10


def get_before_monday_date():
    """
    获取上周的周一的日期
    :return:
    """
    now = datetime.datetime.now()
    monday = now.date() - datetime.timedelta(days=(now.weekday() + 7))
    return monday.strftime('%Y-%m-%d')