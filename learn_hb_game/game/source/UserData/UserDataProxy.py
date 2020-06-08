#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import types
from Source.Log.Write import Log
from datetime import datetime
from UserDataObj import UserDataObj
from Source.GameOperation.Time.ComputeTimedeltaSeconds import ComputeTimedeltaSeconds
from Source.DataBase.Table.t_general_collect import t_general_collect
from Source.DataBase.Common import DBEngine
import traceback


class UserDataProxy:

    def _load(userid=None, roleid=None):
        data = UserDataObj()
        if data.LoadFirst(userid, roleid):
            return data
        Log.Write("[Critical]", userid, roleid, "no role data")
        return None