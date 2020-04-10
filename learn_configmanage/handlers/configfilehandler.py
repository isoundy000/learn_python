#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import datetime
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.escape import json_decode

from basehandler import BaseHandler
from common import ftp
from common.cjsonencoder import CJsonEncoder
from common.configmanager import ConfigManager
from common.dbhelper import DBHelperObject
from forwardhandlers import forward


def set_online_and_reload_config(user, section, type_list, online_model=0, task_id=0, task_name="", task_datetime="", restart_game=0, restart_ext=0, task_desc=""):
    pass


class ConfigFileHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        if "HOTBLOOD" in ConfigManager._config_dict:
            forward(self, "user_role2", "configfile2.html")
        else:
            forward(self, "user_role2", "configfile.html")