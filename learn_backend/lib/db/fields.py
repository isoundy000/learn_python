#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import time
import itertools


class ModelItemMixIn(object):

    CACHE_TYPE = None

    def load_cache(self, obj):
        raise NotImplementedError, "Need come true"

    def get_database(self):
        return None

    def finish_save(self):
        pass

    def reset(self):
        pass


class ModelConfig(dict, ModelItemMixIn):

    CACHE_TYPE = None
    STORAGE_TYPE = 'mysql'


class ModelChat(ModelItemMixIn):

    STORAGE_TYPE = 'tornadoredis'

    @classmethod
    def get_database(self):
        return 'chat'


class ModelDict(dict, ModelItemMixIn):

    CACHE_TYPE = 'string'
    STORAGE_TYPE = 'mysql'

    def __init__(self, defaults, pickler=repr):
        super(dict, self).__init__()

        self.defaults = defaults
        self.changed = False
        self.update(defaults)
        self.reload_cache = False
        self.pickler = pickler

    def __setitem__(self, name, value):

        self.changed = True

        return super(ModelDict, self).__setitem__(name, value)

    def save(self, connection, name, carrier):

        cursor = connection.cursor()

        if not carrier.pk or not cursor.execute(*self.sql_update(name, carrier)):
            cursor.execute(*self.sql_insert(name, carrier))

            carrier.pk = cursor.lastrowid

        connection.commit()