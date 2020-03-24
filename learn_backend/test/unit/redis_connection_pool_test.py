#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import unittest
import test_helper

import threading

import settings

from lib.db import get_redis_client


class UseConnectionPool(threading.Thread):

    """# UseConnectionPool: docstring"""
    def __init__(self):
        super(UseConnectionPool, self).__init__()

    def run(self):
        """# run: docstring
        args:
            :    ---    arg
        returns:
            0    ---
        """
        r = get_redis_client('a')
        d = r.hgetall('models.public_city||PublicCity||h1||20002')
        print len(d)
        while 1: pass


class ConnectionPoolTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_fname(self):
        """# fname: docstring"""
        l = []
        for i in xrange(10):
            l.append(UseConnectionPool())
        for i in l:
            i.start()
        # from lib.db import POOL_DICT_TEMP
        # print POOL_DICT_TEMP