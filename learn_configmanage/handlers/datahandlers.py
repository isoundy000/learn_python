#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import hashlib
import logging
import json
import os
import tornado.websocket
from tornado.escape import json_encode
from tornado.escape import json_decode
import tornado.web
import tornado.gen
import tornado.ioloop
import urllib
from tornado.httpclient import AsyncHTTPClient
from tornado.httputil import url_concat

from common.cjsonencoder import CJsonEncoder
from common.configmanager import ConfigManager

from handlers.configfilehandler import set_online_and_reload_config
from basehandler import BaseHandler



class AjaxValidateHandler(BaseHandler):
    pass