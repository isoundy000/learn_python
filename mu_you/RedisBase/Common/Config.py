#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'ghou'

# redis_name,   redis_ip          redis_port    redis_db    socket_timeout, redis_passwd
REDIS_CONFIG = {
    'USER': {
        'host': '39.96.117.45',
        'port': 6380,
        'socket_timeout': 5,
        'db': 0,
        'password': 'sanguo_passwd',
    },
    'GAME': {
        'host': '39.96.117.45',
        'port': 6380,
        'socket_timeout': 5,
        'db': 0,
        'password': 'sanguo_passwd',
    },
    'BATTLE': {
        'host': '39.96.117.45',
        'port': 6379,
        'socket_timeout': 5,
        'db': 0,
        'password': 'sanguo_passwd',
    },
}