#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os


class GlobalVal(object):

    project_path = ''

    def __new__(cls, *args, **kwargs):
        return None

    def __init__(self):
        pass

    @staticmethod
    def set_value():
        GlobalVal.project_path = os.getcwd()