#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'jutian'

from datetime import datetime
from Source.GameConfig.GameConfigVars import *


class UserLastResponse(object):

    def __init__(self):
        object.__init__(self)
        self.__my_data = []

    def __getitem__(self, item):
        for data in self.__my_data:
            if data[0] == item:
                return data[1]
        return None

    def __setitem__(self, key, value):
        self.__my_data.append((key, value))
        if len(self.__my_data) > USERLASTRESPONSE_CACHE_MAX:
            self.__my_data = self.__my_data[-1 * USERLASTRESPONSE_CACHE_MAX:]

    def has_key(self, key):
        for data in self.__my_data:
            if data[0] == key:
                return True
        return False