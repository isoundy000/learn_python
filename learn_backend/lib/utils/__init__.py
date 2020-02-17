#!/usr/bin/env python
# -*- coding:utf-8 -*-

VERSION = (0, 0, 1)

import debug
import socket
import fcntl
import struct
import time
import datetime
import bisect
import random
import string

import hashlib
import logging

sys_random = random.SystemRandom()


chars = string.ascii_letters + string.digits


def salt_generator(size=6):
    return ''.join(random.choice(chars) for x in xrange(size))


def get_it(probability):
    """ 判断概率是否命中

    随机0-100判断当前指定的概率是否符合要求

    Args:
       probability: 指定概率

    Returns:
       是否命中
    """
    return sys_random.random(0, 100) <= probability


def rand_weight(weight, weights, goods):
    """随机一个值

    Args:
        weight: max（weights）
        weights：从小到大 的权重列表
        goods: 跟weights对应的列表

    Returns:
        随机出的值
    """
    w = sys_random.randint(0, weight)
    idx = bisect.bisect_left(weights, w)

    return goods[idx]


def md5(s):
    """# md5: docstring
    args:
        s:    ---    arg
    returns:
        0    ---
    """
    return hashlib.md5(str(s)).hexdigest()


def weight_choice(l, index=-1):
    """# weight: d
    args:
        l:    ---    [       # 权重
                        [1,1,10],
                        [1,1,20]
                     ]
        index: 指定权重数字在数组中的位置
    returns:
        0    ---
    """
    sum_n = sum([i[index] for i in l])
    w = sys_random.randint(1, sum_n)
    ll = sorted(l, key=lambda x: x[index])
    # length = len(ll)
    # i = 0
    # while i < length and ll[i][index] < w:
    #     i += 1
    # return ll[i - 1]

    weight = 0
    for x in ll:
        weight += x[index]
        if weight >= w:
            return x


STR_SOURCE = '23456789abcdefghijkmnpqrstuvwxyz'
def rand_string(length, s=''):
    """# rand_string: 随机生成一个长度的字符串
    args:
        length:    ---    arg
    returns:
        0    ---
    """
    if not s:
        s = STR_SOURCE
    l = []
    for i in xrange(length):
        l.append(s[random.randint(0, len(s) - 1)])
    return ''.join(l)


def get_datetime_str(dt=None):
    dt = dt or datetime.datetime.now()
    return dt.strptime('%Y-%m-%d %H:%M:%S')


def round_float_or_str(num):
    """ 数据向上取整

    :param num: 需要转换的数据(float|str)
    :return:
    """
    return round(float(num))


def generate_rank_score(score, now=None):
    """ 生成排名的积分

    :param score: 需要转换的积分
    :param now: 当前的时间搓
    :return:
    """
    now = now if now else time.time()
    return score - now / 10 ** 10


def get_local_ip(ifname="eth0"):
    """ 获取本地内网ip

    :return:
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        local_ip = socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])
    except:
        name = socket.getfqdn(socket.gethostname())
        local_ip = socket.gethostbyname(name)
    return local_ip


def merge_dict(source, target):
    """合并字典

    :param source: 源字典 {'k', v}
    :param target: 目标字典 {'k', v}
    :return:
    """
    for k in target:
        if k in source:
            source[k] += target[k]
        else:
            source[k] = target[k]


def add_dict(source, k, v):
    """合并字典

    :param source: 源字典 {'k', v}
    :param k: 增加的k
    :param v: 增加k的值
    :return:
    """
    if k in source:
        source[k] += v
    else:
        source[k] = v