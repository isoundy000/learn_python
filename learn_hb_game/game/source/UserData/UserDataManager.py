#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from Source.Log.Write import Log
from Source.DataLock.Lock1 import Lock1
from Source.DataLock.Lock2 import Lock2
from UserDataProxy import UserDataProxy
from Source.DataBase.Table.t_session import t_session
from Source.DataBase.Table.t_role import t_role


class UserDataManager:

    _data = None
    _sid_uid = None
    _uid_rid = None
    _gLock = None
    _userLock = None
    UserSocketManager = None

    @staticmethod
    def Init():
        pass