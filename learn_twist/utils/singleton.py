#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/11/20 11:42
# @version: 0.0.1
# @Author: houguangdong
# @File: singleton.py
# @Software: PyCharm


class Singleton(type):
    """Singleton Metaclass"""
    _instance = None


    def __init__(cls, name, bases, dic):
        super(Singleton, cls).__init__(name, bases, dic)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance