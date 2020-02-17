#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
from datetime import date
import datetime
from decimal import Decimal


class CJsonEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, Decimal):
            return "%.2f" % obj
        else:
            return json.JSONEncoder.default(self, obj)