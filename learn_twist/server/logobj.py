#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/11/20 23:08
# @version: 0.0.1
# @Author: houguangdong
# @File: logobj.py
# @Software: PyCharm

from twisted.python import log
import datetime
from zope.interface import implementer

# typing
from typing import Dict

@implementer(log.ILogObserver)
class LogObj:

    def __init__(self, log_path: str):
        self.file = open(log_path, 'w')

    def __call__(self, event_dict: Dict):
        if 'logLevel' in event_dict:
            level = event_dict['logLevel']
        elif event_dict['isError']:
            level = 'ERROR'
        else:
            level = 'INFO'
        text = log.textFromEventDict(event_dict)
        if text is None or level != 'ERROR':
            return
        now_date = datetime.datetime.now()
        self.file.write('[' + str(now_date) + ']\n' + str(level) + '\n\t' + text + '\r\n')
        self.file.flush()